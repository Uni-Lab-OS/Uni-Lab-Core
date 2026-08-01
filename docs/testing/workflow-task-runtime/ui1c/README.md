# UI1C Feedback 事件流呈现验收证据

日期：2026-08-01

## 精确候选

- FE：`Uni-Lab-OS/uni-lab-fe@ff12bfa033a67045732e7fa738b9e4a9979d71e5`
- 受测 OS：`Uni-Lab-OS/Uni-Lab-OS@0c23a725ffc93e45baefd382619076fde8433f90`
- 实现 spec：
  `Uni-Lab-OS/uni-lab-fe@ff12bfa033a67045732e7fa738b9e4a9979d71e5:docs/migration/workflow/ui1c-runtime-resilience.md`

## 用户可见合同

- OS Job feedback 仍从
  `GET /api/v1/workflow-node-jobs/{job_uuid}/feedback` 按 sequence cursor 补读。
- 前端把 feedback 投影到 Kernel 原 `WorkflowOutput` “事件流” tab，不新建
  Feedback 面板或第二套列表。
- 事件流保留原有的最新在前顺序、sequence、feedback type、结构化
  data 和 source node 投影。
- SSE 仍只做 invalidation；feedback history 仍以 REST 记录为权威。

## 门禁

- TDD RED：真实浏览器发现仅有 `Feedback` tab，“事件流”公开 seam 失败。
- GREEN：固定 OS SHA 的 runtime resilience E2E 1/1 通过。
- `pnpm test:e2e:workflow -- --reporter=line`：7/7 通过。
- `pnpm test`、`pnpm typecheck`、`pnpm build:desktop`：通过；Web build 由 E2E
  web server 重建并通过。
- Impeccable layout detector：0 findings。
- 网络账本：47 requests / 47 responses，WebSocket 0，application/page errors 0。
  3 条 network diagnostics 是本用例显式注入的 503 与 OS restart 边界。

## 截图

1. `01-first-feedback-visible.png`
2. `02-feedback-cursor-incremental.png`
3. `03-partial-read-keeps-coherent-state.png`
4. `04-partial-read-recovered.png`
5. `05-sse-reconnecting.png`
6. `06-sse-reconnected.png`
7. `07-os-restart-uncertainty-restored.png`
8. `08-reload-restores-feedback.png`

网络账本为 `network-ledger.json`。
