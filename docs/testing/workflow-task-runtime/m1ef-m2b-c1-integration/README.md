# M1EF + M2B + C1 integration E2E

This evidence records the first combined run after merging M1EF and M2B into
the migration branches that already contained C1.

## Published integration heads

| Repository | Branch | HEAD |
|---|---|---|
| Uni-Lab-OS | `integration/workflow-task-runtime` | `31ca092a4c1a7385d636fbf4500585b7a48ee854` |
| uni-lab-fe | `integration/fe-os-migration` | `f35b39bb9cfd9b8ca4699facf9104482cc2489fe` |

The source candidates remain independently traceable:

- M1EF OS: `abc8182619082358903ec72f168d1236de71a5fd`
- M2B OS: `dca2335c8cb3ddbc10117f27906a8fa2522326cd`
- M2B FE: `1d82eea95609fa8c5365f0b8c9b5113ab5ae73bd`

## Merge compatibility gates

- OS combined C1/M1EF/M2B focused suite: `83 passed`.
- OS Ruff check and format check for the integration repair: passed.
- FE workspace typecheck: passed.
- FE Services: `102 passed`.
- FE Workflow Editor: `159 passed`.

## E2E results

### C1

`workflow-composite-authoring-real-os.spec.ts`: `1 passed`.

The browser used the original authoring panel against the merged OS. It
verified the Published child boundary, session-only expand/collapse, reload to
collapsed state, unchanged OS graph/Python, no mutation caused by toggling, no
WebSocket, and no browser/application error. See `c1/`.

### M2B

`workflow-material-source-native-cli-real-os.spec.ts`: `1 passed`.

The browser and native `unilab` CLI covered MaterialSource authoring,
canonical Python save/apply, Task confirmation, create-new Inventory admission,
MaterialSource Job result, Reservation, contention blocked Task, cancel, static
location mismatch rejection, and responsive Properties UI. See `m2b/`.

### M1EF

The merged OS was started through the native `unilab` CLI with the SZLab S09
device package and isolated authority databases. The Task ended at the expected
`failed/invalid_device_action_result` output-contract boundary, while Inventory
committed one failed no-op ChangeSet and released the fenced Claim with
`terminal_settled`; no unsettled Claim remained.

The same runtime was restarted once. The Task and Job identities and settled
terminal state were unchanged, and the restart log contains no redispatch of
the original Job. A separate two-process contention run produced exactly one
`acquired` and one `blocked`; the winner was then released with durable no-send
proof and the authority audit ended with zero unsettled Claims. See `m1ef/`.

## Integration repairs discovered by E2E

1. The M2B browser gate now follows the I1 Task form flow: `Start` then
   `Confirm and create Task`.
2. C1's PackageCatalog consumer now validates module segments and symbols with
   Python identifier rules instead of an ASCII-only regex. This keeps absolute
   module enforcement while accepting the existing SZLab symbol
   `s09_移液调试`, matching PackageCatalog, Workflow schema, and Composite
   authority validation.
