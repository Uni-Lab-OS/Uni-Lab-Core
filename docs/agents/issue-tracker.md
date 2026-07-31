# Issue tracker: GitHub with Feishu knowledge sync

Issues and PRDs for this repo live as GitHub Issues in `Uni-Lab-OS/Uni-Lab-Core`. GitHub is the canonical source for work state, assignment, labels, discussion, and closure. Use the `gh` CLI for issue operations.

The Feishu OKF knowledge base is a synchronized knowledge surface, not a second issue tracker. Automation publishes an idempotent snapshot page for each GitHub Issue without overwriting the existing protocol, implementation, or testing documents.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`, with appropriate label and state filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repository from `git remote -v`; `gh` does this automatically inside the clone.

## Feishu synchronization

`.github/workflows/sync-issues-to-feishu.yml` listens for Issue creation, editing, assignment, label changes, reopening, and closure.

Each Issue owns one automation-managed child page below `GitHub Issues 同步 · Uni-Lab-Core` in the Feishu OKF wiki. The page title uses the stable Issue number, so title edits update the existing page rather than creating duplicates.

Knowledge stages are selected using these labels, in highest-stage-first order:

| GitHub label | Feishu knowledge stage |
| --- | --- |
| `stage:accepted` | Accepted |
| `stage:testing` | Testing |
| `stage:implementation` | Implementation |
| `stage:protocol-definition` | Protocol definition |
| no stage label | Intake |

If several stage labels are temporarily present, the highest stage wins and the generated page records a warning. Apply `sync:feishu-disabled` to suppress synchronization for a particular Issue.

The synchronized page contains the Issue link, title, state, labels, author, assignees, body, selected OKF stage, update timestamp, and the relevant Feishu stage index. GitHub receives one marker-based backlink comment which is updated in place.

A synchronization failure does not roll back the GitHub operation. Fix the permission, secret, or data problem and rerun the workflow manually for the Issue number.

## Pull requests as a triage surface

**PRs as a request surface: no.**

GitHub shares one number space across Issues and PRs, so resolve a bare `#42` with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub Issue. The Feishu snapshot is produced asynchronously by the synchronization workflow.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The map is a single Issue with child Issues as tickets.

- **Map**: an Issue labelled `wayfinder:map`, holding Notes, Decisions-so-far, and Fog.
- **Child ticket**: an Issue linked through GitHub sub-issues. Where unavailable, add it to the map task list and put `Part of #<map>` at the top of the child body.
- **Blocking**: use GitHub native Issue dependencies where available; otherwise use a `Blocked by: #<n>` line.
- **Frontier query**: list open children, remove assigned or blocked Issues, and select the first remaining ticket in map order.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Resolve**: comment with the answer, close the child, then append its context pointer to the map.
