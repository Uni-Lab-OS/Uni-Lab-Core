#!/usr/bin/env python3
"""Synchronize one GitHub Issue into an automation-owned Feishu Wiki page."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence


JsonObject = dict[str, Any]
BACKLINK_MARKER = "<!-- feishu-sync:v1 -->"
GITHUB_API_VERSION = "2026-03-10"


class SyncError(RuntimeError):
    """Base class for synchronization failures."""


class ConfigurationError(SyncError):
    """Raised when the checked-in configuration is invalid."""


class ExternalCommandError(SyncError):
    """Raised when lark-cli cannot complete a requested operation."""


@dataclass(frozen=True)
class StageRule:
    label: str
    stage: str
    okf_url: str


@dataclass(frozen=True)
class SyncConfig:
    repository: str
    space_id: str
    root_node_token: str
    wiki_base_url: str
    sync_parent_title: str
    sync_parent_node_token: str
    skip_label: str
    maximum_body_characters: int
    stage_rules: tuple[StageRule, ...]
    default_stage: StageRule

    @classmethod
    def load(cls, path: str | Path) -> "SyncConfig":
        with Path(path).open(encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ConfigurationError("Feishu sync config must be a JSON object")
        return cls.from_mapping(raw)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "SyncConfig":
        if raw.get("schema_version") != 1:
            raise ConfigurationError("Unsupported Feishu sync schema_version")

        required_strings = (
            "repository",
            "space_id",
            "root_node_token",
            "wiki_base_url",
            "sync_parent_title",
            "sync_parent_node_token",
            "skip_label",
        )
        values: dict[str, str] = {}
        for key in required_strings:
            value = raw.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ConfigurationError(f"{key} must be a non-empty string")
            values[key] = value.strip()

        maximum = raw.get("maximum_body_characters", 12000)
        if not isinstance(maximum, int) or maximum < 1:
            raise ConfigurationError("maximum_body_characters must be a positive integer")

        raw_rules = raw.get("stage_labels")
        if not isinstance(raw_rules, list) or not raw_rules:
            raise ConfigurationError("stage_labels must be a non-empty array")
        rules = tuple(_stage_rule(item, "stage_labels") for item in raw_rules)
        labels = [rule.label for rule in rules]
        if len(labels) != len(set(labels)):
            raise ConfigurationError("stage_labels contains duplicate label names")
        if values["skip_label"] in labels:
            raise ConfigurationError("skip_label cannot also be a stage label")

        default_stage = _stage_rule(raw.get("default_stage"), "default_stage", label="")
        return cls(
            repository=values["repository"],
            space_id=values["space_id"],
            root_node_token=values["root_node_token"],
            wiki_base_url=values["wiki_base_url"].rstrip("/"),
            sync_parent_title=values["sync_parent_title"],
            sync_parent_node_token=values["sync_parent_node_token"],
            skip_label=values["skip_label"],
            maximum_body_characters=maximum,
            stage_rules=rules,
            default_stage=default_stage,
        )


def _stage_rule(
    raw: Any,
    location: str,
    *,
    label: str | None = None,
) -> StageRule:
    if not isinstance(raw, Mapping):
        raise ConfigurationError(f"{location} entries must be JSON objects")
    resolved_label = raw.get("label") if label is None else label
    stage = raw.get("stage")
    okf_url = raw.get("okf_url")
    if not isinstance(resolved_label, str):
        raise ConfigurationError(f"{location}.label must be a string")
    if not isinstance(stage, str) or not stage.strip():
        raise ConfigurationError(f"{location}.stage must be a non-empty string")
    if not isinstance(okf_url, str) or not okf_url.startswith("https://"):
        raise ConfigurationError(f"{location}.okf_url must be an HTTPS URL")
    return StageRule(resolved_label.strip(), stage.strip(), okf_url.strip())


@dataclass(frozen=True)
class IssueSnapshot:
    repository: str
    number: int
    html_url: str
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    author: str
    assignees: tuple[str, ...]
    created_at: str
    updated_at: str
    closed_at: str
    event_action: str

    @classmethod
    def from_issue(
        cls,
        issue: Mapping[str, Any],
        *,
        repository: str,
        event_action: str,
    ) -> "IssueSnapshot":
        if issue.get("pull_request"):
            raise SyncError("Pull requests are not part of the Feishu Issue sync surface")

        number = issue.get("number")
        if not isinstance(number, int) or number < 1:
            raise SyncError("Issue payload is missing a valid number")

        raw_labels = issue.get("labels") or []
        labels: list[str] = []
        for item in raw_labels:
            value = item.get("name") if isinstance(item, Mapping) else item
            if isinstance(value, str) and value.strip():
                labels.append(value.strip())

        raw_assignees = issue.get("assignees") or []
        assignees: list[str] = []
        for item in raw_assignees:
            value = item.get("login") if isinstance(item, Mapping) else item
            if isinstance(value, str) and value.strip():
                assignees.append(value.strip())

        user = issue.get("user")
        author = user.get("login", "unknown") if isinstance(user, Mapping) else "unknown"
        return cls(
            repository=repository,
            number=number,
            html_url=_required_string(issue, "html_url"),
            title=_required_string(issue, "title"),
            body=str(issue.get("body") or ""),
            state=str(issue.get("state") or "unknown"),
            labels=tuple(sorted(set(labels))),
            author=str(author or "unknown"),
            assignees=tuple(sorted(set(assignees))),
            created_at=str(issue.get("created_at") or ""),
            updated_at=str(issue.get("updated_at") or ""),
            closed_at=str(issue.get("closed_at") or ""),
            event_action=event_action or "unknown",
        )


def _required_string(raw: Mapping[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SyncError(f"Issue payload is missing {key}")
    return value.strip()


@dataclass(frozen=True)
class StageDecision:
    stage: str
    okf_url: str
    matched_labels: tuple[str, ...]
    warning: str


def select_stage(labels: Sequence[str], config: SyncConfig) -> StageDecision:
    label_set = set(labels)
    matched = tuple(rule for rule in config.stage_rules if rule.label in label_set)
    selected = matched[0] if matched else config.default_stage
    warning = ""
    if len(matched) > 1:
        joined = ", ".join(rule.label for rule in matched)
        warning = f"Multiple knowledge-stage labels are present ({joined}); {selected.label} won by configured priority."
    return StageDecision(
        stage=selected.stage,
        okf_url=selected.okf_url,
        matched_labels=tuple(rule.label for rule in matched),
        warning=warning,
    )


def issue_node_title(issue: IssueSnapshot) -> str:
    repository_name = issue.repository.rsplit("/", 1)[-1]
    return f"{repository_name} #{issue.number}"


_INVALID_XML_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _xml_text(value: Any) -> str:
    cleaned = _INVALID_XML_CHARACTERS.sub("", str(value))
    return html.escape(cleaned, quote=False).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")


def _xml_attribute(value: Any) -> str:
    cleaned = _INVALID_XML_CHARACTERS.sub("", str(value))
    return html.escape(cleaned, quote=True)


def render_issue_page(
    issue: IssueSnapshot,
    decision: StageDecision,
    config: SyncConfig,
    *,
    synchronized_at: str,
) -> str:
    body = issue.body
    truncated = len(body) > config.maximum_body_characters
    if truncated:
        body = body[: config.maximum_body_characters].rstrip() + "\n\n[Body truncated by synchronization limit.]"
    if not body:
        body = "（无正文）"

    labels = ", ".join(issue.labels) or "（无）"
    assignees = ", ".join(issue.assignees) or "（未分配）"
    closed_at = issue.closed_at or "—"
    warning = ""
    if decision.warning:
        warning = (
            '<callout emoji="❗" background-color="light-yellow" border-color="yellow">'
            f"<p>{_xml_text(decision.warning)}</p></callout>"
        )

    metadata = (
        f"feature_id: github:{issue.repository}#{issue.number}\n"
        f"stage: {decision.stage}\n"
        f"event_action: {issue.event_action}\n"
        f"issue_updated_at: {issue.updated_at}\n"
        f"synced_at: {synchronized_at}"
    )
    return "".join(
        (
            f"<title>{_xml_text(issue_node_title(issue))}</title>",
            "<p>This page is managed by the GitHub Issues synchronization workflow. Edit the GitHub Issue, not this snapshot.</p>",
            f'<p><a href="{_xml_attribute(issue.html_url)}"><b>GitHub Issue #{issue.number}</b></a></p>',
            warning,
            "<table><colgroup><col width=\"150\"/><col width=\"500\"/></colgroup><thead><tr>",
            '<th background-color="light-gray" vertical-align="top"><p>Field</p></th>',
            '<th background-color="light-gray" vertical-align="top"><p>Value</p></th>',
            "</tr></thead><tbody>",
            f"<tr><td vertical-align=\"top\"><p>Title</p></td><td vertical-align=\"top\"><p>{_xml_text(issue.title)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>State</p></td><td vertical-align=\"top\"><p>{_xml_text(issue.state)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Knowledge stage</p></td><td vertical-align=\"top\"><p>{_xml_text(decision.stage)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Labels</p></td><td vertical-align=\"top\"><p>{_xml_text(labels)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Author</p></td><td vertical-align=\"top\"><p>{_xml_text(issue.author)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Assignees</p></td><td vertical-align=\"top\"><p>{_xml_text(assignees)}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Created</p></td><td vertical-align=\"top\"><p>{_xml_text(issue.created_at or '—')}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Updated</p></td><td vertical-align=\"top\"><p>{_xml_text(issue.updated_at or '—')}</p></td></tr>",
            f"<tr><td vertical-align=\"top\"><p>Closed</p></td><td vertical-align=\"top\"><p>{_xml_text(closed_at)}</p></td></tr>",
            "</tbody></table>",
            "<h1>OKF stage</h1>",
            f'<bookmark name="{_xml_attribute(decision.stage)}" href="{_xml_attribute(decision.okf_url)}"></bookmark>',
            "<h1>Issue body</h1>",
            f'<pre lang="markdown" caption="GitHub Issue body"><code>{_xml_text(body)}</code></pre>',
            "<h1>Synchronization metadata</h1>",
            f'<pre lang="yaml"><code>{_xml_text(metadata)}</code></pre>',
        )
    )


class JsonCommandRunner(Protocol):
    def run(self, argv: Sequence[str], *, input_text: str | None = None) -> JsonObject: ...


class SubprocessJsonRunner:
    def __init__(self, *, attempts: int = 3, initial_backoff_seconds: float = 1.0) -> None:
        self.attempts = attempts
        self.initial_backoff_seconds = initial_backoff_seconds

    def run(self, argv: Sequence[str], *, input_text: str | None = None) -> JsonObject:
        environment = os.environ.copy()
        environment["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
        environment["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
        last_result: subprocess.CompletedProcess[str] | None = None
        for attempt in range(self.attempts):
            result = subprocess.run(
                list(argv),
                input=input_text,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            last_result = result
            combined = f"{result.stdout}\n{result.stderr}".lower()
            if result.returncode == 0:
                envelope = _decode_json_output(result.stdout)
                if envelope.get("ok") is not True:
                    raise ExternalCommandError(f"lark-cli returned an unsuccessful envelope: {envelope}")
                return envelope
            if attempt + 1 < self.attempts and ("rate_limit" in combined or "too many requests" in combined or "429" in combined):
                time.sleep(self.initial_backoff_seconds * (2**attempt))
                continue
            break
        assert last_result is not None
        detail = (last_result.stderr or last_result.stdout).strip()
        raise ExternalCommandError(f"lark-cli failed with exit {last_result.returncode}: {detail}")


def _decode_json_output(output: str) -> JsonObject:
    start = output.find("{")
    if start < 0:
        raise ExternalCommandError("Command output did not contain a JSON object")
    try:
        decoded, _ = json.JSONDecoder().raw_decode(output[start:])
    except json.JSONDecodeError as error:
        raise ExternalCommandError(f"Command output contained invalid JSON: {error}") from error
    if not isinstance(decoded, dict):
        raise ExternalCommandError("Command output JSON was not an object")
    return decoded


@dataclass(frozen=True)
class WikiNode:
    node_token: str
    obj_token: str
    obj_type: str
    title: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "WikiNode":
        return cls(
            node_token=_required_string(raw, "node_token"),
            obj_token=_required_string(raw, "obj_token"),
            obj_type=_required_string(raw, "obj_type"),
            title=_required_string(raw, "title"),
        )


class FeishuGateway(Protocol):
    def upsert_issue_page(self, *, node_title: str, content_xml: str) -> str: ...


class LarkCliFeishuGateway:
    def __init__(self, config: SyncConfig, runner: JsonCommandRunner | None = None) -> None:
        self.config = config
        self.runner = runner or SubprocessJsonRunner()

    def upsert_issue_page(self, *, node_title: str, content_xml: str) -> str:
        issue_node = self._find_exact(self.config.sync_parent_node_token, node_title)
        if issue_node is None:
            issue_node = self._create_node(self.config.sync_parent_node_token, node_title)
        if issue_node.obj_type != "docx":
            raise SyncError(f"Feishu node {node_title!r} is not a Docx page")

        self.runner.run(
            (
                "lark-cli",
                "docs",
                "+update",
                "--as",
                "bot",
                "--doc",
                issue_node.obj_token,
                "--command",
                "overwrite",
                "--content",
                "-",
                "--revision-id",
                "-1",
            ),
            input_text=content_xml,
        )
        return f"{self.config.wiki_base_url}/{issue_node.node_token}"

    def _find_exact(self, parent_node_token: str, title: str) -> WikiNode | None:
        envelope = self.runner.run(
            (
                "lark-cli",
                "wiki",
                "+node-list",
                "--as",
                "bot",
                "--space-id",
                self.config.space_id,
                "--parent-node-token",
                parent_node_token,
                "--page-all",
                "--page-limit",
                "0",
            )
        )
        data = envelope.get("data")
        nodes = data.get("nodes", []) if isinstance(data, Mapping) else []
        matches = [WikiNode.from_mapping(item) for item in nodes if isinstance(item, Mapping) and item.get("title") == title]
        if len(matches) > 1:
            raise SyncError(f"Multiple Feishu nodes have the exact title {title!r}")
        return matches[0] if matches else None

    def _create_node(self, parent_node_token: str, title: str) -> WikiNode:
        envelope = self.runner.run(
            (
                "lark-cli",
                "wiki",
                "+node-create",
                "--as",
                "bot",
                "--space-id",
                self.config.space_id,
                "--parent-node-token",
                parent_node_token,
                "--obj-type",
                "docx",
                "--title",
                title,
            )
        )
        data = envelope.get("data")
        if not isinstance(data, Mapping):
            raise ExternalCommandError("lark-cli node creation returned no data object")
        candidate = data.get("node") if isinstance(data.get("node"), Mapping) else data
        try:
            return WikiNode.from_mapping(candidate)
        except SyncError:
            created = self._find_exact(parent_node_token, title)
            if created is None:
                raise ExternalCommandError("Created Feishu node could not be resolved")
            return created


class GitHubGateway(Protocol):
    def fetch_issue(self, repository: str, number: int) -> Mapping[str, Any]: ...

    def upsert_backlink(
        self,
        issue: IssueSnapshot,
        *,
        feishu_url: str,
        decision: StageDecision,
    ) -> None: ...


class GitHubRestGateway:
    def __init__(self, token: str, *, api_base_url: str = "https://api.github.com") -> None:
        if not token:
            raise ConfigurationError("GITHUB_TOKEN is required for synchronization")
        self.token = token
        self.api_base_url = api_base_url.rstrip("/")

    def fetch_issue(self, repository: str, number: int) -> Mapping[str, Any]:
        result = self._request("GET", f"/repos/{repository}/issues/{number}")
        if not isinstance(result, Mapping):
            raise SyncError("GitHub Issue response was not an object")
        return result

    def upsert_backlink(
        self,
        issue: IssueSnapshot,
        *,
        feishu_url: str,
        decision: StageDecision,
    ) -> None:
        body = render_backlink_comment(issue, feishu_url=feishu_url, decision=decision)
        existing_comment_id: int | None = None
        for page in range(1, 11):
            comments = self._request(
                "GET",
                f"/repos/{issue.repository}/issues/{issue.number}/comments?per_page=100&page={page}",
            )
            if not isinstance(comments, list):
                raise SyncError("GitHub comments response was not an array")
            for comment in comments:
                if isinstance(comment, Mapping) and BACKLINK_MARKER in str(comment.get("body") or ""):
                    comment_id = comment.get("id")
                    if isinstance(comment_id, int):
                        existing_comment_id = comment_id
                        if str(comment.get("body") or "") == body:
                            return
                        break
            if existing_comment_id is not None or len(comments) < 100:
                break

        if existing_comment_id is None:
            self._request(
                "POST",
                f"/repos/{issue.repository}/issues/{issue.number}/comments",
                {"body": body},
            )
        else:
            self._request(
                "PATCH",
                f"/repos/{issue.repository}/issues/comments/{existing_comment_id}",
                {"body": body},
            )

    def _request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> Any:
        url = f"{self.api_base_url}{path}"
        encoded = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            url,
            data=encoded,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "Uni-Lab-Core-Feishu-Sync/1",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise SyncError(f"GitHub API {method} {path} failed with HTTP {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise SyncError(f"GitHub API {method} {path} failed: {error.reason}") from error
        if not payload:
            return None
        return json.loads(payload.decode("utf-8"))


def render_backlink_comment(
    issue: IssueSnapshot,
    *,
    feishu_url: str,
    decision: StageDecision,
) -> str:
    warning = f"\n\nStage warning: {decision.warning}" if decision.warning else ""
    return (
        f"{BACKLINK_MARKER}\n"
        "> GitHub → Feishu OKF synchronization\n\n"
        f"Feishu snapshot: [{issue_node_title(issue)}]({feishu_url})  \n"
        f"Knowledge stage: `{decision.stage}`  \n"
        f"Issue updated: `{issue.updated_at or 'unknown'}`"
        f"{warning}"
    )


@dataclass(frozen=True)
class SyncOutcome:
    status: str
    repository: str
    issue_number: int
    stage: str
    feishu_url: str = ""
    warning: str = ""


def synchronize_issue(
    issue: IssueSnapshot,
    config: SyncConfig,
    feishu: FeishuGateway,
    github: GitHubGateway,
    *,
    clock: Callable[[], datetime] | None = None,
) -> SyncOutcome:
    decision = select_stage(issue.labels, config)
    if config.skip_label in issue.labels:
        return SyncOutcome(
            status="skipped",
            repository=issue.repository,
            issue_number=issue.number,
            stage=decision.stage,
        )

    now = (clock or (lambda: datetime.now(timezone.utc)))()
    synchronized_at = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    content = render_issue_page(issue, decision, config, synchronized_at=synchronized_at)
    feishu_url = feishu.upsert_issue_page(
        node_title=issue_node_title(issue),
        content_xml=content,
    )
    github.upsert_backlink(issue, feishu_url=feishu_url, decision=decision)
    return SyncOutcome(
        status="synchronized",
        repository=issue.repository,
        issue_number=issue.number,
        stage=decision.stage,
        feishu_url=feishu_url,
        warning=decision.warning,
    )


def _load_event(path: str) -> JsonObject:
    if not path:
        return {}
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SyncError("GitHub event payload must be a JSON object")
    return payload


def _parse_issue_number(value: str) -> int | None:
    if not value:
        return None
    try:
        number = int(value)
    except ValueError as error:
        raise ConfigurationError("issue-number must be an integer") from error
    if number < 1:
        raise ConfigurationError("issue-number must be positive")
    return number


def run_sync(arguments: argparse.Namespace) -> SyncOutcome | JsonObject:
    config = SyncConfig.load(arguments.config)
    if arguments.repository != config.repository:
        raise ConfigurationError(
            f"Workflow repository {arguments.repository!r} does not match configured repository {config.repository!r}"
        )

    event = _load_event(arguments.event)
    issue_payload = event.get("issue")
    action = str(event.get("action") or "manual")
    issue_number = _parse_issue_number(arguments.issue_number)

    token = os.environ.get("GITHUB_TOKEN", "")
    github: GitHubGateway | None = GitHubRestGateway(token) if token else None
    if not isinstance(issue_payload, Mapping):
        if issue_number is None:
            raise ConfigurationError("No Issue payload or manual issue-number was provided")
        if github is None:
            raise ConfigurationError("GITHUB_TOKEN is required to fetch a manual Issue")
        issue_payload = github.fetch_issue(config.repository, issue_number)
    issue = IssueSnapshot.from_issue(
        issue_payload,
        repository=config.repository,
        event_action=action,
    )

    decision = select_stage(issue.labels, config)
    if arguments.dry_run:
        timestamp = "DRY-RUN"
        return {
            "status": "dry-run",
            "issue": asdict(issue),
            "stage": asdict(decision),
            "node_title": issue_node_title(issue),
            "content_xml": render_issue_page(issue, decision, config, synchronized_at=timestamp),
        }

    if github is None:
        raise ConfigurationError("GITHUB_TOKEN is required for synchronization")
    feishu = LarkCliFeishuGateway(config)
    return synchronize_issue(issue, config, feishu, github)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    sync = subparsers.add_parser("sync", help="Synchronize one Issue")
    sync.add_argument("--config", required=True, help="Path to the checked-in JSON configuration")
    sync.add_argument("--event", default=os.environ.get("GITHUB_EVENT_PATH", ""), help="GitHub event JSON path")
    sync.add_argument("--repository", required=True, help="Expected owner/repository")
    sync.add_argument("--issue-number", default="", help="Manual replay Issue number")
    sync.add_argument("--dry-run", action="store_true", help="Render without remote writes")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "sync":
            result = run_sync(arguments)
        else:
            parser.error(f"Unknown command {arguments.command}")
            return 2
    except (OSError, ValueError, SyncError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    payload = asdict(result) if isinstance(result, SyncOutcome) else result
    print(json.dumps({"ok": True, "result": payload}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
