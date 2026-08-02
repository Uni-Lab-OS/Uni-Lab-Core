# D1A-S1 device single Action Task evidence

## Published pins

- Private OS dev: `Uni-Lab-OS/Uni-Lab-OS:dev@f660fd83dd8008c3947d75241a1e222f30ad7852`
- Private OS dev production merge: `f4d9c1e4fb007ff26c8a867d0d2e1f43eafd404b`
- OS integration merge: `Uni-Lab-OS/Uni-Lab-OS@25e71d1aeff1e13e9ab3405c2302cf5a4bf15b7a`
- Current OS integration documentation successor: `cf6f81da8bf41950c8779555c60a7b7349184fbe`
- OS aligned E2E checkout: `2c65cd139605985047d5ecf82592c8850636cbd9`
- OS D1A code commit: `305a5caceda42acfe0d835263cd2e51cc6fc497d`
- Current FE integration/Core pin: `Uni-Lab-OS/uni-lab-fe@0bf83ea93de9aff5a10f0419a3322cff27b48595`
- D1A FE integration merge: `b963a33d0a589a12b1e2aa16a9e0d05929ee4ff7`
- FE aligned E2E checkout: `b502e4379250f7b5d3b3ed7506d4476b50353538`
- FE D1A code commit: `a380bf81666509b8a5bfe7a7c84af43576828dd9`
- Core publication baseline: `886cbc556597fbbe4699043af6fbe342d4e737ba`

The OS/FE integration commits and the private OS dev production commit preserve
non-squash, two-parent provenance. The private dev first preserves its existing
Constructor packaging commit and the restored public-dev base, then merges the
full private integration line. Relative to the previously gated release tree,
the private production merge adds only those three pre-existing packaging
files; `f660fd83` then corrects two publication documents. D1A production and
test blobs are unchanged.

## Gate result

- OS aligned candidate: `2347 passed, 4 skipped`.
- Private OS dev production composition: same gated production tree; its only
  additional files are the pre-existing Constructor packaging assets.
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
