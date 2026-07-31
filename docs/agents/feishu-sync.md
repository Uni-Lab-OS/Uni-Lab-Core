# GitHub Issues to Feishu OKF synchronization

This repository synchronizes GitHub Issue snapshots into an automation-owned area of the Feishu OKF wiki. GitHub remains authoritative for work state. Existing Feishu protocol, implementation, testing, and development-standard pages remain authoritative for accepted knowledge and are never overwritten by the workflow.

## Data flow

1. A supported GitHub Issue event starts `.github/workflows/sync-issues-to-feishu.yml`.
2. `scripts/github_feishu_sync.py` validates the repository and event payload.
3. The first matching stage label in `.github/feishu-sync.json` selects the OKF stage.
4. The Feishu adapter uses the pre-provisioned repository sync parent and finds or creates the stable Issue child page.
5. The child page is overwritten with the latest deterministic snapshot.
6. A marker-based GitHub comment is created or updated with the Feishu backlink.

The workflow serializes all synchronization runs for this repository so two Issue events cannot race while creating the same Feishu node.

## GitHub labels

Exactly one stage label should normally be present:

| Label | Meaning |
| --- | --- |
| `stage:protocol-definition` | The Issue is defining or freezing a protocol. |
| `stage:implementation` | The Issue is implementing a frozen protocol. |
| `stage:testing` | The Issue is collecting test or acceptance evidence. |
| `stage:accepted` | The Issue has passed acceptance. |

When multiple stage labels are present, the highest-stage entry in `.github/feishu-sync.json` wins and the Feishu snapshot records the conflict. Apply `sync:feishu-disabled` to skip an Issue entirely.

The five triage labels in `docs/agents/triage-labels.md` are independent of these knowledge-stage labels.

## Required GitHub configuration

Create these repository Secrets:

- `FEISHU_APP_ID` — the Feishu application's app ID.
- `FEISHU_APP_SECRET` — the Feishu application's app secret.

Set them without putting secret values in shell history:

```bash
gh secret set FEISHU_APP_ID --repo Uni-Lab-OS/Uni-Lab-Core
gh secret set FEISHU_APP_SECRET --repo Uni-Lab-OS/Uni-Lab-Core
```

The workflow uses the built-in `GITHUB_TOKEN` with only `contents: read` and `issues: write`.

## Required Feishu configuration

The Feishu application must have `wiki:node:retrieve` and `wiki:node:create`, plus Docx read/write scopes. `wiki:node:retrieve` is the narrow read scope used to find an existing Issue child before creating one. Because this is a public wiki space, applications cannot be added as space members. Instead, grant the Bot edit access only to the pre-provisioned automation parent and its descendants.

The approved application is `cli_aa909ff57c38dbd7` (“昌珺涵的飞书 CLI”), whose Bot open ID is `ou_5c0fbb13bb064dabdbc38658e15baaaf`. The automation parent is `P4VDwEQQ8iCLNpkXRm2cDs6en2f` (“GitHub Issues 同步 · Uni-Lab-Core”). Grant container-scoped edit access with a user identity that administers the page:

```bash
lark-cli drive +member-add \
  --as user \
  --token "P4VDwEQQ8iCLNpkXRm2cDs6en2f" \
  --type wiki \
  --member-id "ou_5c0fbb13bb064dabdbc38658e15baaaf" \
  --member-type openid \
  --perm edit \
  --perm-type container \
  --yes
```

## Manual replay

Run the workflow from GitHub Actions and provide the Issue number, or use the CLI locally after configuring both identities:

```bash
python scripts/github_feishu_sync.py sync \
  --config .github/feishu-sync.json \
  --event /path/to/workflow-event.json \
  --repository Uni-Lab-OS/Uni-Lab-Core \
  --issue-number 42
```

For an Issue event payload, the Issue number is read from the payload. For a manual workflow event, the GitHub adapter fetches the requested Issue.

## Failure handling

- **Missing GitHub Secret**: the configuration step fails before any Feishu write.
- **Feishu application scope denied**: apply `wiki:node:retrieve` (and verify `wiki:node:create`) for the application, publish the application change, and then rerun the Bot check.
- **Feishu resource permission denied**: verify that the Bot has container-scoped edit access on the configured synchronization parent.
- **Duplicate exact node titles**: resolve the duplicate manually; the module refuses to guess which node to overwrite.
- **Rate limiting**: the Feishu command runner retries rate-limit responses with exponential backoff.
- **Stale GitHub backlink**: rerun the workflow; the marker comment is updated in place.
- **Synchronization disabled**: remove `sync:feishu-disabled` and rerun manually.

GitHub state is never rolled back after a synchronization failure.
