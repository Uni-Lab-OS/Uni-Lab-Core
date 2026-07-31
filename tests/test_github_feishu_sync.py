from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from scripts.github_feishu_sync import (
    BACKLINK_MARKER,
    ConfigurationError,
    IssueSnapshot,
    LarkCliFeishuGateway,
    StageDecision,
    SyncConfig,
    SyncError,
    issue_node_title,
    render_backlink_comment,
    render_issue_page,
    select_stage,
    synchronize_issue,
)


def config_mapping() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "repository": "Uni-Lab-OS/Uni-Lab-Core",
        "space_id": "7498240950477668371",
        "root_node_token": "root-node",
        "wiki_base_url": "https://example.feishu.cn/wiki",
        "sync_parent_title": "GitHub Issues 同步 · Uni-Lab-Core",
        "sync_parent_node_token": "sync-parent-node",
        "skip_label": "sync:feishu-disabled",
        "maximum_body_characters": 12000,
        "stage_labels": [
            {"label": "stage:accepted", "stage": "accepted", "okf_url": "https://example.com/accepted"},
            {"label": "stage:testing", "stage": "testing", "okf_url": "https://example.com/testing"},
            {
                "label": "stage:implementation",
                "stage": "implementation",
                "okf_url": "https://example.com/implementation",
            },
            {
                "label": "stage:protocol-definition",
                "stage": "protocol-definition",
                "okf_url": "https://example.com/protocol",
            },
        ],
        "default_stage": {"stage": "intake", "okf_url": "https://example.com/intake"},
    }


def issue_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "number": 42,
        "html_url": "https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/42",
        "title": "Synchronize A & B <safely>",
        "body": "First line\nSecond <line> & more",
        "state": "open",
        "labels": [{"name": "stage:implementation"}, {"name": "ready-for-agent"}],
        "user": {"login": "reporter"},
        "assignees": [{"login": "builder"}],
        "created_at": "2026-07-30T00:00:00Z",
        "updated_at": "2026-07-31T00:00:00Z",
        "closed_at": None,
    }
    payload.update(overrides)
    return payload


def snapshot(**overrides: Any) -> IssueSnapshot:
    payload_overrides = overrides.pop("payload", {})
    issue = IssueSnapshot.from_issue(
        issue_payload(**payload_overrides),
        repository="Uni-Lab-OS/Uni-Lab-Core",
        event_action="edited",
    )
    return replace(issue, **overrides)


class FakeFeishu:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def upsert_issue_page(self, *, node_title: str, content_xml: str) -> str:
        self.calls.append({"node_title": node_title, "content_xml": content_xml})
        return "https://example.feishu.cn/wiki/issue-node"


class FakeGitHub:
    def __init__(self) -> None:
        self.backlinks: list[dict[str, Any]] = []

    def fetch_issue(self, repository: str, number: int) -> Mapping[str, Any]:
        raise AssertionError("fetch_issue was not expected")

    def upsert_backlink(
        self,
        issue: IssueSnapshot,
        *,
        feishu_url: str,
        decision: StageDecision,
    ) -> None:
        self.backlinks.append(
            {"issue": issue, "feishu_url": feishu_url, "decision": decision}
        )


class QueueRunner:
    def __init__(self, responses: Sequence[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[tuple[str, ...], str | None]] = []

    def run(self, argv: Sequence[str], *, input_text: str | None = None) -> dict[str, Any]:
        self.calls.append((tuple(argv), input_text))
        if not self.responses:
            raise AssertionError(f"No queued response for command: {argv}")
        return self.responses.pop(0)


def node(title: str, token: str, obj_token: str) -> dict[str, Any]:
    return {
        "title": title,
        "node_token": token,
        "obj_token": obj_token,
        "obj_type": "docx",
    }


class ConfigurationTests(unittest.TestCase):
    def test_rejects_duplicate_stage_labels(self) -> None:
        raw = config_mapping()
        raw["stage_labels"].append(dict(raw["stage_labels"][0]))
        with self.assertRaisesRegex(ConfigurationError, "duplicate"):
            SyncConfig.from_mapping(raw)


class StageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SyncConfig.from_mapping(config_mapping())

    def test_uses_default_stage_without_stage_label(self) -> None:
        decision = select_stage(("ready-for-agent",), self.config)
        self.assertEqual("intake", decision.stage)
        self.assertEqual((), decision.matched_labels)

    def test_highest_stage_wins_and_conflict_is_visible(self) -> None:
        decision = select_stage(
            ("stage:protocol-definition", "stage:accepted", "stage:testing"),
            self.config,
        )
        self.assertEqual("accepted", decision.stage)
        self.assertEqual(
            ("stage:accepted", "stage:testing", "stage:protocol-definition"),
            decision.matched_labels,
        )
        self.assertIn("Multiple knowledge-stage labels", decision.warning)


class RenderingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SyncConfig.from_mapping(config_mapping())

    def test_renders_validly_escaped_snapshot(self) -> None:
        issue = snapshot()
        decision = select_stage(issue.labels, self.config)
        content = render_issue_page(
            issue,
            decision,
            self.config,
            synchronized_at="2026-07-31T01:00:00Z",
        )
        self.assertIn("Synchronize A &amp; B &lt;safely&gt;", content)
        self.assertIn("First line<br/>Second &lt;line&gt; &amp; more", content)
        self.assertIn("<title>Uni-Lab-Core #42</title>", content)
        self.assertNotIn("<safely>", content)

    def test_truncates_large_issue_body(self) -> None:
        config = replace(self.config, maximum_body_characters=5)
        issue = snapshot(payload={"body": "abcdefghij"})
        decision = select_stage(issue.labels, config)
        content = render_issue_page(issue, decision, config, synchronized_at="now")
        self.assertIn("abcde<br/><br/>[Body truncated by synchronization limit.]", content)
        self.assertNotIn("abcdefghij", content)

    def test_backlink_has_stable_marker_and_stage(self) -> None:
        issue = snapshot()
        decision = select_stage(issue.labels, self.config)
        comment = render_backlink_comment(
            issue,
            feishu_url="https://example.feishu.cn/wiki/issue-node",
            decision=decision,
        )
        self.assertTrue(comment.startswith(BACKLINK_MARKER))
        self.assertIn("Knowledge stage: `implementation`", comment)
        self.assertIn("Uni-Lab-Core #42", comment)


class SynchronizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SyncConfig.from_mapping(config_mapping())

    def test_synchronizes_through_the_module_interface(self) -> None:
        issue = snapshot()
        feishu = FakeFeishu()
        github = FakeGitHub()
        outcome = synchronize_issue(
            issue,
            self.config,
            feishu,
            github,
            clock=lambda: datetime(2026, 7, 31, 1, 2, 3, tzinfo=timezone.utc),
        )
        self.assertEqual("synchronized", outcome.status)
        self.assertEqual("implementation", outcome.stage)
        self.assertEqual("Uni-Lab-Core #42", feishu.calls[0]["node_title"])
        self.assertIn("2026-07-31T01:02:03Z", feishu.calls[0]["content_xml"])
        self.assertEqual(1, len(github.backlinks))

    def test_skip_label_causes_no_remote_calls(self) -> None:
        issue = snapshot(labels=("sync:feishu-disabled", "stage:testing"))
        feishu = FakeFeishu()
        github = FakeGitHub()
        outcome = synchronize_issue(issue, self.config, feishu, github)
        self.assertEqual("skipped", outcome.status)
        self.assertEqual([], feishu.calls)
        self.assertEqual([], github.backlinks)

    def test_pull_request_payload_is_rejected(self) -> None:
        with self.assertRaisesRegex(SyncError, "Pull requests"):
            IssueSnapshot.from_issue(
                issue_payload(pull_request={"url": "https://api.github.com/pulls/42"}),
                repository="Uni-Lab-OS/Uni-Lab-Core",
                event_action="opened",
            )


class LarkCliAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SyncConfig.from_mapping(config_mapping())

    def test_updates_existing_issue_node(self) -> None:
        issue = node("Uni-Lab-Core #42", "issue-node", "issue-doc")
        runner = QueueRunner(
            [
                {"ok": True, "data": {"nodes": [issue]}},
                {"ok": True, "data": {"result": "success"}},
            ]
        )
        gateway = LarkCliFeishuGateway(self.config, runner)
        url = gateway.upsert_issue_page(node_title="Uni-Lab-Core #42", content_xml="<title>snapshot</title>")
        self.assertEqual("https://example.feishu.cn/wiki/issue-node", url)
        self.assertIn("docs", runner.calls[-1][0])
        self.assertEqual("<title>snapshot</title>", runner.calls[-1][1])

    def test_creates_issue_node_once(self) -> None:
        issue = node("Uni-Lab-Core #42", "issue-node", "issue-doc")
        runner = QueueRunner(
            [
                {"ok": True, "data": {"nodes": []}},
                {"ok": True, "data": issue},
                {"ok": True, "data": {"result": "success"}},
            ]
        )
        gateway = LarkCliFeishuGateway(self.config, runner)
        gateway.upsert_issue_page(node_title="Uni-Lab-Core #42", content_xml="<title>snapshot</title>")
        create_calls = [call for call, _ in runner.calls if "+node-create" in call]
        self.assertEqual(1, len(create_calls))

    def test_refuses_duplicate_exact_titles(self) -> None:
        duplicate = node("Uni-Lab-Core #42", "one", "doc-one")
        other = node("Uni-Lab-Core #42", "two", "doc-two")
        runner = QueueRunner([{"ok": True, "data": {"nodes": [duplicate, other]}}])
        gateway = LarkCliFeishuGateway(self.config, runner)
        with self.assertRaisesRegex(SyncError, "Multiple Feishu nodes"):
            gateway.upsert_issue_page(node_title="Uni-Lab-Core #42", content_xml="<title>x</title>")


if __name__ == "__main__":
    unittest.main()
