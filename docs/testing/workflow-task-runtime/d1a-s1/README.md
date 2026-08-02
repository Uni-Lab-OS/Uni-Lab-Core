# D1A-S1 device single Action Task evidence

## Published pins

- Canonical OS dev: `deepmodeling/Uni-Lab-OS:dev@8e6dec6f6cb5bdfc76653e28f421f78c53ba893d`
- Tested OS dev production merge: `b3190ca8a99f5be2cdc4c9943771728bf98dc10f`
- OS integration merge: `Uni-Lab-OS/Uni-Lab-OS@25e71d1aeff1e13e9ab3405c2302cf5a4bf15b7a`
- OS aligned E2E checkout: `2c65cd139605985047d5ecf82592c8850636cbd9`
- OS D1A code commit: `305a5caceda42acfe0d835263cd2e51cc6fc497d`
- Current FE integration/Core pin: `Uni-Lab-OS/uni-lab-fe@0bf83ea93de9aff5a10f0419a3322cff27b48595`
- D1A FE integration merge: `b963a33d0a589a12b1e2aa16a9e0d05929ee4ff7`
- FE aligned E2E checkout: `b502e4379250f7b5d3b3ed7506d4476b50353538`
- FE D1A code commit: `a380bf81666509b8a5bfe7a7c84af43576828dd9`
- Core publication baseline: `886cbc556597fbbe4699043af6fbe342d4e737ba`

Both integration commits and the canonical OS dev commits preserve non-squash,
two-parent provenance. The `8e6dec6f` dev successor changes only this round's
implementation report and migration matrix after publication; its production
tree is the tested `b3190ca8` merge. The OS/FE aligned candidates were rebased
by merge onto the latest integration targets before the final gate; D1A
production and test blobs were unchanged by those target merges.

## Gate result

- OS aligned candidate: `2347 passed, 4 skipped`.
- Canonical OS dev merge: `2347 passed, 4 skipped`.
- OS direct D1A suite: `30 passed`.
- D1A-aligned FE material/services/pascal/workflow-editor/kernel/desktop suites:
  262 tests.
- Current FE integration successor: 286 tests; workspace typecheck, Web build
  and Desktop build passed. It contains the D1A non-squash integration merge.
- FE workspace typecheck, Web build and Desktop build: passed.
- Final real OS-to-browser E2E: 1/1 passed in 18.8 seconds.
- Independent exact-SHA review: Standards 0 Blocking / 1 Non-blocking;
  Spec 0 Blocking / 0 Non-blocking. The non-blocking item is the existing
  `DevicePanel` orchestration concentration.

The ledger records two UI submissions creating two formal Task/Job pairs. It
also proves that timeline and monitor expose only the public Job UUID and that
legacy Runtime routes, Runtime WebSocket, frontend-direct Edge WebSocket,
system Workflow reads, browser errors and internal source fields are all zero.
The `exactShas.core` value in the machine ledger identifies the local E2E runner
checkout; this directory's Git commit and the gitlinks above are the publication
authority.

## Visual evidence

1. [Parameter form and existing busy holder](01-parameter-and-busy-holder.png)
2. [Original Action form ready](02-original-action-form-ready.png)
3. [Durable pending acceptance](03-durable-pending-accepted.png)
4. [Running feedback in the original event stream](04-running-feedback-event-stream.png)
5. [Device busy during execution](05-device-busy-during-run.png)
6. [Typed terminal result in the original panel](06-terminal-result-in-original-panel.png)
7. [Device free and rerun enabled](07-free-and-rerun-enabled.png)
8. [Second formal Task/Job succeeded](08-second-formal-run-succeeded.png)

Combined visual: [contact sheet](contact-sheet.png).

Machine-readable evidence: [network ledger](network-ledger.json). Runtime log:
[OS log](os.log).

## Acceptance state

Software implementation, integration publication, exact-SHA review and Core
evidence pin are complete. Real physical device/ROS and Feishu acceptance remain
open under Core `#162/#163`; therefore D1A-S1 is `stage:testing`, not
`stage:accepted`.
