# UI1E 持久 Authoring 文件导入验收证据

日期：2026-08-01

## 精确候选

- FE：`Uni-Lab-OS/uni-lab-fe@95c072077b193cafaeb3c6d4977c10f22af911fb`
- OS：`Uni-Lab-OS/Uni-Lab-OS@0c23a725ffc93e45baefd382619076fde8433f90`
- 实现 spec：
  `Uni-Lab-OS/uni-lab-fe@95c072077b193cafaeb3c6d4977c10f22af911fb:docs/migration/workflow/ui1e-authoring-file-import.md`
- FE delivery：`Uni-Lab-OS/uni-lab-fe#11`
- Core Decision：`Uni-Lab-OS/Uni-Lab-Core#139`

OS 本轮无生产接口变更；上述 OS tip 只在交互迁移矩阵中记录 UI1E
候选、health v1 对齐和联调结果。

## 验收结果

- Python 导入：文件进入当前 Workflow 的未保存 Draft；OS 规范化源码时
  必须接受完整 diff，然后得到 Candidate 并 Apply。
- JSON 导入：仅接受同 Workflow 的 `WorkflowAuthoringGraph`；真实调用
  `POST /api/v1/authoring/generate-python`，完整 diff 接受前不写 Draft，
  Apply body 仅有 `candidate_hash`。
- 负向：跨 Workflow Graph 显式拒绝，当前文档不变，不调用
  `generate-python`。Canonical v2/Cloud JSON 在浏览器中 fail closed。
- 原 UI 复用：`useWorkflowFileUpload`、`PersistentWorkflowAuthoringPanel`、
  CodeMirror、DAG、完整 diff 和已有 Draft/Apply 控件继续作为唯一生产路径；
  未恢复旧 `WorkflowToolbar`、Run、Runtime WebSocket 或 polling。

## 门禁

- `pnpm test`：通过；workflow-editor 58 tests，workspace 全部通过。
- `pnpm typecheck`：通过。
- `pnpm build:web`：通过。
- `pnpm build:desktop`：通过，4340 modules transformed。
- `pnpm test:e2e:workflow-authoring-import -- --reporter=line`：3/3 通过。
- `pnpm test:e2e:workflow -- --reporter=line`：7/7 通过。
- 精确 SHA `pnpm test:e2e:workflow-final-gate -- --reporter=line`：1/1 通过；
  扫描 164 个 production files，禁止的 runtime 引用 0，timer fallback 0。
- 三份网络账本合计 32 个 API requests/32 responses，4xx/5xx 0，
  `console.error` / `pageerror` 0。

## 截图

1. `01-python-file-imported.png`
2. `02-python-normalization-diff.png`
3. `03-python-candidate-saved.png`
4. `04-python-candidate-applied.png`
5. `05-json-graph-imported.png`
6. `06-json-full-python-diff.png`
7. `07-json-candidate-saved.png`
8. `08-json-candidate-applied.png`
9. `09-cross-workflow-json-rejected.png`

网络账本为 `python-network-ledger.json`、`json-network-ledger.json` 和
`rejected-json-network-ledger.json`。
