# C1 Composite Authoring real-OS E2E

Status: **testing complete; awaiting explicit Accepted decision**.

This gate exercises the production OS authoring authority with a Registry-backed
typed Action and a PackageCatalog-backed Published Workflow. The child is saved,
normalized, applied, published, and then invoked by a parent through the same
`WorkflowService` used by the HTTP server.

## Immutable inputs

| Repository | Ref | Commit |
|---|---|---|
| Uni-Lab-OS | `integration/workflow-task-runtime` | `000222a3750617481f9cb2fa1707c817f122614c` |
| uni-lab-fe integration | `integration/fe-os-migration` | `e6609fd52cd5f0a3fe46ccdee7e70458fca2694b` |
| FE exact E2E candidate | `migration/c1-e2e-real-os` | `28a2e5e6403428bad4815ec156df6ae25438a68a` |

## Assertions

- OS returns an Applied parent with one Published Workflow boundary, one private
  internal node carrying `parent_uuid`, and two boundary edges with authoritative
  source/target Handle UUIDs.
- Canonical Python retains one absolute PackageCatalog import and one child call.
- The browser starts collapsed, expands the OS-owned internal graph locally,
  collapses it again, and resets to collapsed after reload.
- Toggle operations issue no authoring mutation, Runtime Task/Job request, or
  WebSocket traffic.
- Applied graph, canonical Python, and Workflow revision remain unchanged.
- The A1 Action Catalog and C1 Published Workflow Catalog both load successfully;
  no visible catalog error, HTTP application error, page error, or WebSocket is
  observed.

## Verification

| Gate | Result |
|---|---|
| `pnpm test:e2e:workflow-composite` | `1 passed` |
| Existing real-OS Authoring E2E | `11 passed` |
| Workflow editor unit suite | `148 passed` |
| FE workspace typecheck | passed |
| FE Web production build | passed |
| OS focused C1 regression suite | `21 passed` |
| OS Ruff / format for changed files | passed |

The E2E uncovered and fixed two cross-contract blockers:

1. Composite boundary nodes are non-executable but must remain valid data
   providers for downstream A1 typed Action required fields.
2. Template Catalog detail rows do not promise Handle array order; FE now
   canonicalizes Published Workflow Handles by `(handle_key, io_type)` before
   validating the I/O contract.

This evidence covers C1 authoring only. It does not claim R2 admission,
ExecutionPlan generation, dispatch, or Composite runtime completion.

## Evidence checksums

| File | SHA-256 |
|---|---|
| `01-collapsed.png` | `fac5e7e8eb07458bbd291029189d3638e41d6afe38c0abf04f93f90bc831fc21` |
| `02-expanded.png` | `4ccdff26e1804a50cdf244f7286af1c6a2ac62f8987010436da0e124ad2bdb91` |
| `03-reload-collapsed.png` | `3154465edba43b785647bc5f83b2456b59c249e2ad0a7d019f94182b04ed94c7` |
| `authoring-before.json` | `cc2c405bea7eb6814d4db007bfe7d3b00dc0686fbc6cfe3de6b087cc886c1b84` |
| `catalog-wire.json` | `eec64f12d6f709e4e42927540de4cf6a18c566b7db1c36dd5f47a96591a690b5` |
| `network-graph-ledger.json` | `2306d3ba8dadd1d7608e1169a8e915dabd338c158352399b38aa6fe6ef7f439a` |
