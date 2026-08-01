# UI1D Runtime final gate evidence

## Candidate pins

- FE candidate: `Uni-Lab-OS/Uni-Lab-FE@27212c7674f746d0ac941ccf592dd57644983272`
- FE integration: `Uni-Lab-OS/Uni-Lab-FE@bb0bb249afd0dd6ded0025fb8c34e534aec5c278`
- Tested OS production candidate: `Uni-Lab-OS/Uni-Lab-OS@3eb8a59014267f3b6161c36dcbc882c4aa3b9e90`
- OS integration after the documentation-only matrix updates: `Uni-Lab-OS/Uni-Lab-OS@68c364e2e70c228a9598fbe1f4a10510602b51c2`
- Core gate baseline: `Uni-Lab-OS/Uni-Lab-Core@9a7467cd4d91a008bdd4b8f754d73fafbb3cacc8`

The production OS tree did not change between the tested candidate and the
documentation-only matrix update.

## Gate result

- `pnpm typecheck`: passed.
- `pnpm test`: passed (material 54, pascal-lab-plugin 13, services 34,
  workflow-editor 51, kernel-web 16, plus desktop icon/installer checks).
- `pnpm build:web`: passed with known Sass, third-party sourcemap, and chunk
  warnings only.
- `pnpm build:desktop`: passed.
- `pnpm test:e2e:workflow`: 7/7 passed against real production OS HTTP/SSE.
- `pnpm test:e2e:workflow-final-gate`: 1/1 passed against real production OS.
- Static retired-contract scan: 163 production TypeScript files scanned, 15
  retired files absent, and zero forbidden Runtime references.
- Network ledger: 50 requests and 50 responses; zero forbidden requests,
  WebSocket URLs, application errors, or page errors.

The final gate reused `PersistentWorkflowAuthoringPanel`, `WorkflowDag`,
`WorkflowDebugger`, `WorkflowOutput`, the existing node start/breakpoint
controls, and the existing output dock. It did not introduce a replacement
workbench or screenshot-only UI.

## Visual evidence

1. [Applied original workbench](01-applied-original-workbench.png)
2. [Terminal race while SSE is disconnected](02-terminal-race-sse-disconnected.png)
3. [Terminal race restored from REST/SSE](03-terminal-race-restored.png)
4. [Step Task and Jobs projection](04-step-task-and-jobs.png)
5. [Idempotent step replay and 409 conflict](05-step-replay-and-conflict.png)
6. [Resume accepted and applied](06-resume-accepted-and-applied.png)
7. [Pause accepted and applied](07-pause-accepted-and-applied.png)
8. [Cancel terminal state](08-cancel-terminal-state.png)
9. [Reload restores the latest Task](09-reload-restores-latest-task.png)

Machine-readable evidence: [network-ledger.json](network-ledger.json).

## Remaining acceptance gate

UI1D implementation and cross-repository E2E are complete. Exact-SHA
independent review and Feishu Testing/Accepted reconciliation remain required
before Core decision `#150` can enter `stage:accepted`.
