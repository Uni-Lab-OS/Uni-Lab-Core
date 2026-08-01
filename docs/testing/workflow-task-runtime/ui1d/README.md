# UI1D Runtime final gate evidence

## Candidate pins

- FE candidate: `Uni-Lab-OS/uni-lab-fe@b2547ee51fd9d7e6f9f277c407e3503c59cc4085`
- FE integration: `Uni-Lab-OS/uni-lab-fe@a641fa6fa38b223ec90648a2c308c67d4a57b6fd`
- Tested OS checkout: `Uni-Lab-OS/Uni-Lab-OS@68c364e2e70c228a9598fbe1f4a10510602b51c2`
- OS integration after the final documentation-only matrix update:
  `Uni-Lab-OS/Uni-Lab-OS@b05793d9dfaefecf048c98fb709eca94b722fe27`
- Core gate baseline: `Uni-Lab-OS/Uni-Lab-Core@0ecb9448ffc4bfb4d05687f5234784f454d6664c`

The production OS tree did not change between the tested checkout and the
documentation-only matrix update. Standards and Spec reviews of the exact FE
candidate both passed with 0 Blocking and 0 Non-blocking findings.

## Gate result

- `pnpm typecheck`: passed.
- `pnpm test`: passed (material 54, pascal-lab-plugin 13, services 34,
  workflow-editor 51, kernel-web 15, plus desktop icon/installer checks).
- `pnpm build:web`: passed with known Sass, third-party sourcemap, and chunk
  warnings only.
- `pnpm build:desktop`: passed.
- `pnpm test:e2e:workflow-debug`: 8/8 passed against real production OS
  HTTP/SSE, including Authoring, Task Runtime, resilience, and final gate.
- Static retired-contract scan: 160 production TypeScript files and 2 active
  E2E fixture/helper files scanned, 19 retired files absent, and zero forbidden
  Runtime or timer-polling references.
- Network ledger: 50 requests and 50 responses; zero forbidden requests,
  WebSocket URLs, application errors, or page errors. A 3.5-second quiet
  terminal window observed zero Task-list/detail, Jobs, or feedback GETs.

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

## Acceptance state

UI1D implementation, cross-repository E2E, exact-SHA review, matrix update and
submodule pins are complete. Core decision `#150` is the authority for the
Feishu Testing/Accepted synchronization and final repository-ticket closure.
