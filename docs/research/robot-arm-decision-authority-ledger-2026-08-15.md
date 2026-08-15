# 机械臂历史设计决策总账与本轮权威裁决

> - Wayfinder 研究票：[Core #226](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/226)
> - 研究日期：2026-08-15（Asia/Shanghai）
> - 当前合并 Map：[Core #225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225)
> - 当前合并基线：OS `codex/integrate-device-factory-backend-authority@57aaf11a9be420a41a7f7eb24978757da20616ee`；FE `codex/integrate-dev-model-runtime-backend-authority@e3e4059bbb81301dfb1d9cbeddba91255c917ec5`

## 当前权威摘要

1. **本轮最新维护者约束以 Core #225 为准。** 它要求：Shared Interface 由 Backend 合同拥有，Workspace Backend 与正式 Backend 是两个 Adapter；单设备调度准入增加简单 `Exclusive`；正常调度时仍持续上报 joint state；Edge 先用 HTTP 提交完整 joint-state fact，再用既有 Edge WebSocket 发送短通知；Backend 不逐帧落库并通过独立 SSE 向前端上报；未来 `start_jog` / `stop_jog` 是离散命令，不新增前端高频下行链路；owner、RBAC、TTL、完整 maintenance lease、Fence、审计和复杂断线恢复不在本轮范围。[来源：#225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225)
2. **Core #224 仍拥有未与上述约束冲突的关节遥测和运动学不变量。** 继续有效的核心包括：真实 JointState 才能成为观测、每个 Graph `device_id` 的 exact joint ownership、qualified joint name、`topology_digest + boot_id + sequence + observed_at`、latest-value-wins、stale 时冻结最后可信姿态、遥测与控制分离、双同型号机械臂不串流。[来源：#224 最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321)
3. **Core #224 的旧传输拓扑不再是本轮实现权威。** D15-1、D19-A1 和 D22-1 所冻结的“本地 OS 直接经 `/api/v1/ws/device_status` 向 FE 发送完整 `push_joint_state/v2`，Backend 延后”与 #225 的强制 HTTP fact + WS notification + Backend SSE 拓扑冲突；本轮按 #225 取代。D23-1 只保留“遥测只读、控制另走控制面”，不引入旧的完整 commissioning session/lease/Fence。[旧 D15/D22](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285899389)、[旧 D19-A1](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286430078)、[旧 D23-1](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286320189)
4. **Core #214 的 PointSet/目标资产决策继续有效，但不进入本轮重设计。** joint state 是短寿命只读观测，绝不进入 PointSet、SiteAccess、物料图或调度写模型；完整点位、示教回写与多执行器资产重新设计被 #225 明确排除。[来源：#214 边界补充](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5285717329)
5. **Frontend 的常规实时合同仍是 SSE，但 joint state 是本轮明确增加的例外通路。** 历史 D-025 要求所有浏览器实时投影走单一 `/api/v1/events` SSE、内部 `/api/v1/edge/ws` 不暴露给浏览器；#225 后来明确 joint state 可以使用独立 SSE，因此 D-025 对普通 Workflow/Job/feedback/attention 事件继续有效，对 joint-state endpoint 单一性和耐久 re-hydration 语义被本轮收窄。[来源：D-025 / Core #33](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/33)
6. **Feishu OKF 正文尚未完成本次复核。** 当前用户身份缺少 `docx:document:readonly` 和 `wiki:node:retrieve`，所以本总账是“GitHub 维护者决策 + 一手代码/提交”的可执行中间裁决，不能宣称已替代 Feishu 当前协议正文。恢复授权后，应把本轮 delta 写入/核对 Feishu Protocol、Implementation、Testing 文档，再进入最终 accepted spec。

状态标记：

- **有效**：没有被更晚约束取代，可继续作为规范输入。
- **已取代**：更晚决策明确替换旧方案；不得恢复旧实现。
- **与本轮冲突**：在原 Issue 范围曾冻结，但本轮 #225 对当前交付给出相反强制约束。
- **待决**：只有方向或实现证据，仍需对应 Wayfinder 票冻结合同。
- **实现证据**：证明某能力做过或验证过，不自动成为规范权威。

## 时间线

| 时间 | 来源 | 发生的决策或证据 | 当前判断 |
| --- | --- | --- | --- |
| 2026-07-29～07-31 | [Frontend 合同目录 #130](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/130)、[D-025 / #33](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/33)、[D-027 / #35](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/35)、[D-058 / #66](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/66) | 前端共享 Interface 一次只选一个 Authority；浏览器实时使用 SSE；内部 Edge WebSocket 不暴露给前端；只镜像 Backend 的 frontend-facing contract。 | #130 只是索引；组成决策的基础原则有效，独立 joint-state SSE 是 #225 的后来例外。 |
| 2026-08-01 | [领域设备包 Wayfinder #147](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/147) | 模型与驱动共置、统一 PackageCatalog、Graph 拥有运行实例配置、Warehouse/Site 与 robot point binding 分层。 | 有效；#214 对 point binding 进一步细化。 |
| 2026-08-02～03 | [Xacro/STL 闭环 #169](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/169) | Package Catalog 审计模型闭包；OS 投影受控模型 URL；FE 使用服务端 macro/mesh root；浏览器模型资产链 E2E。 | 有效；属于静态/包内模型基础，不等于实时关节驱动。 |
| 2026-08-04～11 | [WorkCell Spec #189](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/189)、[包分层补充](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/189#issuecomment-5248512067) | Arm/Rail 模块独立，vendor-neutral coordinator/compiler 不注册第二 Device；部署包只注册一个复合 Device；近期以离线编译的静态 URDF/SRDF/shape/controller snapshot 交付。 | 有效的组合/所有权边界；#224 D18R 补充 execution/render 双视图。 |
| 2026-08-13 | [PointSet Wayfinder #214](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214) | D1～D14 冻结 PointSet v3、SiteAccess、rail/arm 复合目标、生成式阵列、PLC/SDK/MoveIt 资产分层、运动模板、资格和原子激活。 | 有效；本轮不重新设计。 |
| 2026-08-13～14 | [Joint telemetry Wayfinder #224](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224) | D15～D24、KIN-1、D17/D18/D25 冻结本地实时 joint state、实例身份、拓扑、背压、stale、只读边界和双实例验收。 | 语义大部有效；D15/D19/D22 传输拓扑被 #225 取代。 |
| 2026-08-14 | [OS `92082078`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/92082078027dabed6ae7f6bc28fe84e8b44920e0) | 实现 `JointStateProjector`、模型/拓扑、HostNode 接线以及本地 `RobotCommissioningService`。 | 实现证据；projector/model 可候选复用，旧路由/session 需重写或排除。 |
| 2026-08-14～15 | [FE `ddad91d`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/ddad91d0b3fc03fa47c309e3b1f023e54b102e91)、[`feat/card-robot@9a470d5`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/9a470d57233bc9d9192564011293c91f3f11f7bd) | 实现 joint preview、scene runtime、`push_joint_state` WebSocket 解析和完整 Robot Commissioning Card bridge。 | 实现证据；scene/runtime 可候选复用，WS transport 与完整 session 模型不符合本轮。 |
| 2026-08-15 | [OS robot tip `3f92d010`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/3f92d010da263ebb2d7b6e4c6e901cc292484e9a)、[FE robot tip `9a470d5`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/9a470d57233bc9d9192564011293c91f3f11f7bd) | 两个 robot 分支形成旧架构下的端到端候选。 | 尚未通过 PR 合入；只能选择性迁移。 |
| 2026-08-15 | [当前 Map #225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | 维护者把本轮收敛为通用 Exclusive、HTTP fact + WS notification、Backend memory latest + 独立 SSE、离散 jog 命令。 | 本轮最高 GitHub 决策入口。 |
| 2026-08-15 | [#227](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/227)、[#228](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/228)、[#229](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/229)、[#230](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/230)、[#231](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/231) | 分别审计复用边界、正式 Backend seam、Exclusive 合同、joint-state 合同和最高测试 seam。 | 待决/进行中。 |

## 主题索引

| 主题 | 当前有效入口 | 本轮必须忽略或改写 | 待决入口 |
| --- | --- | --- | --- |
| 控制 / Commissioning | #224 D23 的“遥测只读、控制分离”；#225 的离散命令方向 | robot 分支的 owner/session/maintenance lease/Fence 完整体系 | [#229](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/229)、[#231](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/231) |
| Exclusive / 手动模式 | #225 的通用单设备调度准入 Exclusive | 机器人专属 commissioning session 作为唯一独占模型 | [#229](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/229) |
| joint telemetry | #224 D16、D17、D20、D21 的观测/身份/背压/stale 语义 | D19-A1 的完整帧直发 FE WebSocket | [#230](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/230) |
| 运动学身份 / 模型拓扑 | #224 KIN-1、D17S/C/W、D18M/R | 显示名、裸 joint 名、前缀猜测、随机 token 候选 | #227 只审实现复用，不应重开已冻结语义 |
| PointSet / targets | #214 D1～D14 与 D25 | joint state 写入 PointSet；本轮重做示教资产 | 本轮排除 |
| Robot Card / Workbench | #169 静态模型闭环；#224 FE exact mapping/latest/stale | Card 直接打开旧 robot session；FE 直连 Edge joint WS | [#227](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/227)、[#231](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/231) |
| Backend / Edge transport | #225 强制 HTTP fact → existing WS notification → Backend SSE | D15/D22 本地绕过 Backend；D19 完整帧经 WS | [#228](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/228)、[#230](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/230) |
| 测试 | #224 D24 的双实例/自动联动/stale；#169 的模型资产闭环 | 只凭单 CR5 截图或旧 WS E2E 宣称新合同完成 | [#231](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/231) |

## 决策总账 A：共享 Authority、前端实时与包/模型基础

| ID | 来源 | 原决策 | 当前状态 | 本轮解释 |
| --- | --- | --- | --- | --- |
| FE-CATALOG | [Core #130](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/130) | 汇总 frontend contract 的现行与已取代决策，并明确目录不复制组成票的规范正文。 | **有效索引，不是独立规范** | 本总账读取 #33/#35/#51/#66 的正文，不把 #130 的“历史已吸收”误当实现权威。 |
| FE-D025 | [Core #33](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/33) | 所有 frontend-facing realtime 使用 `/api/v1/events` SSE；REST 是耐久真值；`/api/v1/edge/ws` 仅内部使用。 | **有效，但被 #225 收窄** | 普通 Workflow/Job/feedback/attention 继续适用。joint state 是不落库、独立 SSE 的易失投影，路由、首帧与重连语义由 #230 冻结。 |
| FE-D027 | [Core #35](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/35) | 每个共享前端 Interface 一次只选择一个 Authority；切换只改变 base URL；路径/DTO/envelope/错误和业务语义一致。 | **有效** | 与 #225“Backend Shared Interface、两个 Adapter”完全一致。 |
| FE-D043 | [Core #51](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/51) | Backend-style JSON envelope；SSE 保留原生 `id/event/data`，不套 JSON envelope。 | **有效** | joint-state HTTP 与 SSE 仍应遵循 shared envelope/framing；具体 payload 待 #230。 |
| FE-D058 | [Core #66](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/66) | OS 只镜像 Backend 的 frontend-facing Interface；Backend-to-Edge 协议不得泄露成前端合同。 | **有效** | 前端不理解 Edge HTTP/WS 两段提交；只消费 shared SSE/HTTP。 |
| PKG-D2/D3 | [Core #147](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/147) | 删除平行 model-bundle 事实源；设备模型与驱动共置并进入统一 PackageCatalog。 | **有效** | robot execution/render model 应继续来自 exact package asset，不由 FE 猜路径。 |
| PKG-D9 | [Core #147](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/147) | Warehouse/Site 业务位置与 robot point 到达方式分层，通过 site + operation binding 关联。 | **有效，已由 #214 细化** | 使用 #214 的 PointSet/SiteAccess 术语，不恢复旧宽泛 PointBinding。 |
| MODEL-169 | [Core #169](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/169)、[修复账本](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/169#issuecomment-5160864715) | Catalog 审计包内 Xacro/STL；OS 投影受控 URL；FE 使用服务端 macro/mesh root。 | **有效；有实现证据** | 是 Workbench 模型加载基础，不定义实时关节传输。 |
| WC-PKG | [#189 包分层补充](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/189#issuecomment-5248512067) | Arm/Rail 模块可独立复用；协调/编译包不注册第二 Device；部署包只注册一个复合 Device；静态编译模型作为近期交付。 | **有效** | 防止 standalone Arm 与复合 Arm 同时成为两个调度入口。 |

## 决策总账 B：PointSet、目标与机械臂/导轨资产（Core #214）

这些决策是独立的资产与执行规划权威。本轮只引用边界，不重新实现 PointSet/示教写回。

| ID | 来源 | 原决策 | 当前状态 |
| --- | --- | --- | --- |
| D1 | [D1 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5278576438) | 新增 `unilab.robot-point-set/v3`；顶层直接按 Deck 设备分组；`global` 保留；rail 可选；不加 `devices:` 包装。 | **有效** |
| D2 | [D2 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5278723992) | Resource/Slot/Site 与点位通过唯一 SiteAccess binding 层关联；点位资产不保存 Material/SiteOccupancy；发布时 exact-set 冻结。 | **有效，术语被 D8a 的 SiteAccessDeclaration/activation 细化** |
| D3 | [D3 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5278789478) | 顶层键只可读分组；稳定 `device_ref` 承担跨 revision 的 Deck/WorkCell 成员引用；显示名不参与身份。 | **有效** |
| D4/D4a | [D4/D4a 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279015703) | 一个 target 是 optional rail + optional arm 的声明包，不授权并行；缺 rail 表示 hold frozen target；rail 改变前 Arm 必须到已资格 `rail_transfer_safe`，发生不确定结果即 Fence。 | **有效；不等于本轮要实现完整 Fence** |
| D5 | [D5 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279131470) | `global.arm.home`、`standby`、`rail_transfer_safe` 是不同类型化目标；加载资产不产生运动或解除 Fence。 | **有效** |
| D6 初版 | [D6](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279197324)、[D6b](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279285876)、[D6c](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279452173) | 三锚点仿射阵列；设备局部 frame + versioned Calibration；共享 TCP 姿态 + sparse absolute orientation override。 | **部分已取代**：可能被理解为发布逐格 `resolved_cells` 的措辞由最终 D6 撤销；其余规则保留。 |
| D6 最终 | [D6 最终修正](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279777929) | 只有一份生成式 PointSet；发布验证遍历全部 cell 并冻结摘要，但不生成第二份可编辑逐格坐标事实源；运行时按 exact source/digest/generator 确定性解析。 | **有效** |
| D6d | [D6d 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279919452) | rail assignment 使用 direct-position `default + groups + overrides`，优先级固定，仍遵守 D4a。 | **有效** |
| D7 初版 | [D7 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5279956502) | v3 一次迁移，删除 v2，不保留双读/回退。 | **有效但范围被修正** |
| D7R | [D7 范围修正](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5280006992) | PointSet 只服务 SDK/MoveIt；PLC 使用控制器内示教点和独立 ProgramSet，不迁入 v3。 | **有效，取代 D7 对 PLC 的可能泛化** |
| D8b | [D8b 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5280433187) | 领域包作者态禁止硬编码环境实例 UUID；使用 `owner_resource_ref + slot_key`，激活期 exact resolve 为 Site UUID。 | **有效；原先把 Site UUID 直接写入源码的 D8a 候选已取代** |
| D8a/D8c | [D8a、D8c 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5280931260) | PLC 三层资产：SiteAccessDeclaration / PLCProgramSet / PLCAdapterProfile；激活快照冻结 `activation_epoch + topology_digest`，执行中不重新查找并静默换绑。 | **有效** |
| D9-1S | [D9-1S 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5281454717) | 标准 pick/place 使用版本化 `AccessMotionBlock/v1`，而非任意 Recipe DSL；entry/approach 相对 interaction；grip/release 和观测由封闭模板拥有；rail 变化在块外插入屏障。 | **有效；取代原任意 SiteOperationRecipe 候选** |
| D10 | [D10/D11/D14 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5281198468) | PointSet 几何与 MotionProfile 的 PTP/LIN、速度、容差和碰撞要求分离；MoveIt/SDK/PLC 只做明确映射。 | **有效** |
| D11 | [同上](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5281198468) | PointQualification、ProgramQualification、SiteOperationQualification 分层；不把 `VERIFIED` 写回不可变 PointSet。 | **有效** |
| D12 | [D12 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5280931260) | 调试速度上限由 HardwareProfile 必填；默认 25%，平台硬上限 30%，提高需重新审批/资格。 | **有效；本轮不实现权限体系不代表可删除设备侧限制** |
| D13 | [D13 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5280931260) | 夹爪是独立 EndEffectorPort；快换与 ToolContext 独立；由 WorkCell Coordinator 编排，不并入 RobotExecutionBackend。 | **有效** |
| D14 | [D10/D11/D14 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5281198468) | 新资产先准备/校验，再在 WorkCell 空闲窗口原子激活；WorkflowTask 冻结 activation；旧任务不切到新版。 | **有效；与本轮简单 Exclusive 是不同层次** |
| D25A/B/C | [多机械臂点位归属最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5288597391) | 每个稳定 Graph `device_id` 的 manifest 锁定独立完整 PointSet/ProgramSet；Graph exact path+digest 选资产；换机可保留 device_id，但 Calibration/Qualification 必须更新、旧 activation 失效。 | **有效** |
| JS/PointSet 边界 | [#214 边界补充](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5285717329) | 实时 joint state 是短寿命只读运行观测，不是 PointSet/SiteAccess/Material/调度写模型。 | **有效，本轮强制保留** |

## 决策总账 C：实时关节状态、运动学身份和模型（Core #224）

| ID | 来源 | 原决策 | 当前状态 | 当前裁决 |
| --- | --- | --- | --- | --- |
| D15-1 | [D15/D22/D24 冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285899389) | 首期只做 Robot package → OS → FE/Pascal 本地直连；不得依赖 Backend。 | **与本轮冲突** | #225 明确要求 joint state 经所选 Authority：Edge HTTP fact + WS notification，Authority SSE → FE。 |
| D16-2R | [D16-2R 已选择](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288531907) | 不新增 `RobotKinematicsTelemetryPort`；MoveIt、TCP/SDK、PLC 将真实读回规范化为 ROS `sensor_msgs/JointState`，再由 OS projector 投影；无真实读回不得猜测。 | **有效** | 与本轮只改变 Edge→Authority/FE 传输，不冲突。 |
| KIN-1 | [D17/D18 纠正](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285777585) | 同场景相同型号实例必须在 OS 与 FE 都拥有独立 link/joint/controller/group/TF/tool/collision identity；显示名不参与匹配；帧需 identity + digest + boot + sequence。 | **有效** | 本轮不能因简化状态管理而降级身份校验。 |
| D17N 随机 token 候选 | [候选](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285805722)、[状态校正](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285808630) | OS 生成持久随机实例 token。 | **已取代** | 后续正式选择可读、唯一 Graph `device_id=node.id`；不得复活 token registry。 |
| D17S-1 | [最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | Graph `device_id=node.id` 是活动 Edge 内唯一运动学 namespace；远程 envelope 外层另带 `edge_id`；`boot_id` 只表示激活会话。 | **有效** | Shared Interface 的跨 Edge cache key 至少需要 `edge_id + device_id`，精确 wire shape 由 #230 决定。 |
| D17C-1 | [最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | Arm 与 Rail 各自独立 device namespace；Tool 是 Arm attachment；组合由 Coordinator + topology digest 冻结。 | **有效** | 不把导轨或工具吞入一个裸 Arm joint namespace。 |
| D17W-1 | [最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | 所有 Adapter 在 `/joint_states` 发布完整 qualified joint name；OS 用冻结 exact ownership table 分组，禁止前缀猜测和单设备 fallback。 | **有效** | `JointStateProjector` 是直接复用候选。 |
| D18M-1 | [最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | exact Arm/Rail 型号包拥有 canonical joint specs 和 Adapter raw→canonical 映射；实例编译器 canonical→qualified。 | **有效** | Backend 不重新映射 joint 名，只中继已验证 producer identity。 |
| D18R-1 | [最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | 单一模型编译权威从 canonical URDF 生成 execution/render 双视图；二者共享 qualified names 与 topology digest；render 不重复 world placement。 | **有效** | 当前 robot OS/FE 模型实现可按 #227 选择性迁移。 |
| D19-A1 | [D19-A1 已接受](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286430078) | 恢复 `publish_joint_state()` / `action: push_joint_state` schema v2；完整帧复用 `/api/v1/ws/device_status` 直发本地 FE。 | **与本轮冲突** | 只可保留 projector 方法/identity schema 作为内部实现参考；完整 fact 必须 HTTP 上报，WS 只通知，FE 改走 SSE。是否保留 action 名作为兼容别名由 #230 决定。 |
| D20-2 修订 | [D19/D20/D21 核查](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286008211)、[后续修订](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286320189) | producer/transport 最高 20 Hz；Pascal 最多 10 Hz apply；每实例 latest-value-wins，不排队、不逐帧持久化。 | **有效** | HTTP producer 频率、Backend/SSE coalescing 与背压细节仍由 #230 冻结；不允许形成 HTTP 请求积压队列。 |
| D21-1 / D21S-2 | [D20/D21 冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286008211)、[最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321) | 校验 boot/sequence/observed time；旧 boot/倒序丢弃；过期冻结最后可信姿态并显示 stale；HardwareProfile `stale_after_s` 默认 1.0，范围 0.5～5.0 秒。 | **有效** | SSE 重连不回放历史帧；首帧、cache miss 和 stale 责任需 #230 定义。 |
| D22-1 | [D15/D22/D24 冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285899389) | 本地绕过 Backend；Backend 只在未来远程模式做鉴权/限流的短寿命中继，不持久化。 | **与本轮冲突（部分语义保留）** | “本地绕过、Backend 延后”被取代；“短寿命、不逐帧持久化、不重编号 producer sequence”保留，并同时适用于 Workspace/正式 Backend Adapter。 |
| D23-1 | [D23-1 冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286320189) | joint telemetry 只读；控制经独立 `RobotCommissioningPort`、maintenance lease、Fence、互锁。 | **部分有效、部分与本轮冲突** | 只读/控制分离与设备侧安全互锁有效；完整 lease/Fence/owner/session 本轮排除，改为通用简单 Exclusive。 |
| D24-1 | [D15/D22/D24 冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285899389) | 双同型号机械臂不串流；真实 MoveIt 后网页自动更新；断线 stale/重连；跨 Robotics/OS/FE E2E，不能以截图代替。 | **有效，但测试拓扑需更新** | 新验收还必须覆盖两种 Authority、HTTP fact 先于 WS notification、Backend latest cache、SSE 驱动 URDF；由 #231 冻结。 |
| D25A/B/C | [#224 最终冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5288595321)、[#214 同步冻结](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/214#issuecomment-5288597391) | 每个 device manifest 锁定自己的 PointSet/ProgramSet；换机后旧激活失效。 | **有效，本轮排除重做** | 只作为 topology/device identity 的先决条件。 |

## 决策总账 D：控制、Commissioning、Exclusive 与 Robot Card

| 决策/实现 | 来源 | 原设计 | 当前状态 | 当前裁决 |
| --- | --- | --- | --- | --- |
| 通用手动 Exclusive | [Core #225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | 单设备调度准入增加 Exclusive；不做 owner/RBAC/TTL/Fence/复杂恢复。 | **有效方向，合同待决** | canonical 术语、`idle/busy/exclusive`、busy 拒绝、Edge ACK、重启清空由 [#229](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/229) 冻结。 |
| 调度时持续 joint state | [Core #225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | `busy/scheduled` 只影响控制准入，不关闭只读 joint telemetry。 | **有效** | FE 在正常调度和 Exclusive 都订阅同一观测面。 |
| 完整 Robot Commissioning session | [OS `robot_commissioning.py@92082078`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/blob/92082078027dabed6ae7f6bc28fe84e8b44920e0/unilabos/app/robot_commissioning.py)、[FE service at robot tip](https://github.com/Uni-Lab-OS/uni-lab-fe/blob/9a470d57233bc9d9192564011293c91f3f11f7bd/packages/services/src/robotCommissioning.ts) | owner、simulation/maintenance mode、session id、snapshot、move/jog/stop、PointSet revise、session close/Fence。 | **与本轮冲突；实现证据** | 不直接合入。通用 Exclusive 替代 session 独占；PointSet revise、owner、lease/Fence 排除；未来控制命令应走 Shared Interface/现有 Edge 控制链。 |
| 离散 jog | [Core #225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | 未来使用 `start_jog` / `stop_jog`，不建立前端高频控制流。 | **有效方向；本轮不实现完整协议** | #229/#231 只需保证 Exclusive/命令 seam 可兼容；设备侧 watchdog/互锁不能由前端连接承担。 |
| Card Mock joint preview | [FE `ddad91d`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/ddad91d0b3fc03fa47c309e3b1f023e54b102e91)、[分支架构文档](https://github.com/Uni-Lab-OS/uni-lab-fe/blob/9a470d57233bc9d9192564011293c91f3f11f7bd/docs/architecture/device-card-vibe-coding.md) | Mock 完整 joint snapshot 进入应用级 scene-runtime 临时缓存；不写 Material Graph/磁盘；Live 拒绝伪造 preview。 | **待决（实现证据，原则与 D23 一致）** | scene-runtime/命令式 URDF apply 可候选复用；是否作为本轮 UI 必选由 #227/#231 决定。 |
| Card Live RobotCommissioning bridge | [FE controller at robot tip](https://github.com/Uni-Lab-OS/uni-lab-fe/blob/9a470d57233bc9d9192564011293c91f3f11f7bd/packages/services/src/deviceCardRobotCommissioningController.ts) | Card Host 代持 device/session，Card 通过 `robot-commissioning` capability 打开/执行/关闭 session。 | **与本轮冲突；实现证据** | 不能原样迁移；改成通用 Exclusive 交互和未来离散命令，或本轮排除。 |
| Card / Pascal live joint apply | [FE realtime parser](https://github.com/Uni-Lab-OS/uni-lab-fe/blob/9a470d57233bc9d9192564011293c91f3f11f7bd/packages/services/src/realtime.ts)、[scene runtime commit history](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/9a470d57233bc9d9192564011293c91f3f11f7bd) | 解析 `push_joint_state/v2`，按 device/topology/boot/sequence/stale 更新 scene runtime。 | **语义有效，transport 与本轮冲突** | 保留验证/store/apply；把 WebSocket Adapter 改成独立 SSE Adapter。 |

## 决策总账 E：Backend / Edge 传输与缓存

| 决策 | 来源 | 当前状态 | 尚需冻结 |
| --- | --- | --- | --- |
| Backend Shared Interface 为公共合同，Workspace Backend 与正式 Backend 是两个 Adapter | [#225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225)、[D-027](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/35) | **有效** | 两 Adapter 的路径、DTO、错误、SSE 行为必须相同。 |
| Edge 用 HTTP 提交完整 joint-state fact；成功后用既有 Edge WebSocket 发短通知 | [#225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | **有效强制方向** | HTTP method/path、认证、序列/幂等、旧帧处理、WS notification type/minimal payload、通知丢失后的恢复，由 [#230](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/230) 冻结。 |
| Backend 不逐帧持久化，只保留 latest 并通过独立 SSE 上报 FE | [#225](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/225) | **有效强制方向** | cache key/owner、bounded latest-only、SSE 路由/首帧/heartbeat/reconnect/stale、慢消费者策略，由 [#228](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/228) 与 [#230](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/230) 冻结。 |
| 正式 Backend 进程拓扑与无库 cache 可见性 | [#228](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/228) | **待决** | HTTP handler、Edge WS handler、SSE fanout 是否同进程；Scheduler 地址是否独立；多副本/粘性路由或共享 cache 边界。不得从 OS local adapter 反推。 |
| 普通前端事件单 SSE `/api/v1/events` | [#33](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/33) | **有效；joint telemetry 被本轮收窄** | joint SSE 是独立 endpoint 还是 `/events` 的独立订阅/流，#225 倾向独立通路，最终由 #230 明确。 |
| 旧 `push_joint_state` 名称兼容 | [D19-A1](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5286430078) | **待决/旧 transport 已取代** | 可保留 projector 方法或兼容 action alias，但不得使完整 joint payload 回到 Edge WS 或 FE WS。 |

## 决策总账 F：测试与验收

| 测试决策/证据 | 来源 | 当前状态 | 本轮使用方式 |
| --- | --- | --- | --- |
| 双同型号实例隔离、MoveIt 后网页自动更新、stale/reconnect、零手工注入 | [D24-1](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5285899389) | **有效** | 继续作为 joint telemetry 的最高行为门。 |
| 旧本地 `push_joint_state/v2` E2E | [#224 E2E 记录](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5289045093)、[实机链路复验](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/224#issuecomment-5289270885) | **实现证据；旧 transport 已取代** | 证明 ROS→projector→FE/URDF 能工作；不能证明 HTTP fact + WS notification + Backend SSE。 |
| Xacro/STL 受控资产闭环 | [#169](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/169) | **有效实现证据** | 作为模型装载前置门，不能替代 articulated telemetry 验收。 |
| SZLab 空工作区机械臂转运 E2E | [#191](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/191)、[验收记录](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/191#issuecomment-5227807271) | **相邻实现证据** | 证明 Site/Workflow/robot transfer 基础，不覆盖实时 joint state 或 Exclusive。 |
| 新本轮最高 seam | [#231](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/231) | **待决** | 至少覆盖：scheduled 时实时展示、busy 拒绝 Exclusive、Exclusive 阻调度、HTTP 先于 WS 通知、latest-only、SSE 驱动 URDF、两 Authority 合同一致、未来 jog seam。 |

## 分支与提交：实现证据，不是规范权威

| 仓库/提交 | 事实 | 对本轮的意义 |
| --- | --- | --- |
| OS [`48e13a7b`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/48e13a7b4d7f3356e7c7232347991cdb3a5f31b6) | 历史 HostNode 直接订阅 `/joint_states` 并发布旧 `push_joint_state`；无 boot/sequence/topology/stale，多实例按前缀猜测。 | 只作历史来源；#224 已明确禁止原样恢复。 |
| OS [`92082078`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/92082078027dabed6ae7f6bc28fe84e8b44920e0) | 新增 exact `JointStateProjector`、`package_moveit_model`、motion runtime plan、HostNode 接线和 524 行本地 commissioning service。 | projector/model/test 可候选复用；route/session 需要按 #225 改写。 |
| OS [`7283c2bb`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/7283c2bb7f0fd575026c050e3f0449551239c211) | 增加安全 commissioning simulation controller/timing、MoveIt controller launch plan。 | 本轮是否纳入由 #227/#231 决定；不是 Exclusive/joint transport 必需项。 |
| OS robot tip [`3f92d010`](https://github.com/Uni-Lab-OS/Uni-Lab-OS/commit/3f92d010da263ebb2d7b6e4c6e901cc292484e9a) | `origin/codex/device-factory-model-ref-validation-fix` 当前远端 tip。 | 相对本轮 OS 基线有 49 个相关文件差异；未发现对应 GitHub PR。 |
| FE [`ddad91d`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/ddad91d0b3fc03fa47c309e3b1f023e54b102e91) | Mock articulated model preview 与 scene-runtime 基础。 | 与 transport 解耦，优先作为复用候选。 |
| FE robot tip [`9a470d5`](https://github.com/Uni-Lab-OS/uni-lab-fe/commit/9a470d57233bc9d9192564011293c91f3f11f7bd) | `origin/feat/card-robot`；包含 joint WS parser、scene runtime、Robot Commissioning service/controller、Card SDK capability、desktop joint preview。 | store/render 可迁移；WS parser 与完整 session bridge 需重写/排除；未发现对应 GitHub PR。 |
| 当前本地合并基线 OS `57aaf11a` / FE `e3e4059` | #225 指定的两条已完成合并线；它们没有上述 robot-specific modules。 | 正式实现必须从这里选择性迁移，不能直接 merge 两个 robot 分支。 |

## 本轮已经冻结与仍待决定

### 已冻结，不应在后续 Grill 重开

- joint state 是常驻只读观测；`idle`、调度 `busy`、手动 `exclusive` 都可观察。
- MoveIt/SDK/PLC 只有真实 joint readback 才能生产 JointState。
- Graph `device_id`、qualified joint、exact ownership、topology digest、boot/sequence/observed time 和 stale 语义。
- latest-value-wins、不逐帧排队、不逐帧落数据库。
- Edge 完整 joint fact 走 HTTP；HTTP 成功后 existing Edge WS 只发短通知；Backend→FE 走独立 SSE。
- telemetry 与 control 分离；本轮 Exclusive 是通用调度准入，不是完整 Robot Commissioning lease/session。
- 前端不需要高频下行；未来 jog 使用离散 start/stop。
- PointSet、SiteAccess、Material、Scheduler 写模型不保存 joint frames。

### 仍待决定，不能由旧分支实现倒推

1. **正式 Backend seam（#228）**：HTTP fact、Edge WS、SSE fanout、scheduler/device admission 分别在哪个进程/模块；latest cache 的进程和多副本约束。
2. **Exclusive 合同（#229）**：字段/术语、状态转换、busy 冲突错误、Authority→Edge 命令与 ACK、Edge/Backend 重启后的本轮简化行为。
3. **joint-state wire contract（#230）**：HTTP path/method/envelope、sequence/idempotency、WS notification 名称与最小 payload、cache key、SSE endpoint/event/首帧/heartbeat/reconnect/stale、旧 `push_joint_state` 兼容边界。
4. **选择性迁移与测试 seam（#227/#231）**：projector/model/scene/Card 的直接复用、改写或排除；两 Authority 的合同夹具和合并顺序。
5. **Feishu 权威对账**：取得读取权限后，核对当前 Protocol/Implementation/Testing revisions，并把本轮 supersession 链写回相应 feature 文档。

## Feishu OKF 访问限制

按 `docs/agents/domain.md` 先尝试读取协作指南，再访问 Protocol/Implementation/Testing 索引，但用户身份尚未授权：

```text
lark-cli docs +fetch --as user --doc IDO1wrptGiPZl3k6GnDcbqy5nMg
→ need_user_authorization
→ required scope: docx:document:readonly

lark-cli wiki +node-list --as user \
  --space-id 7498240950477668371 \
  --parent-node-token AaokwPX7viwZpTk52Vxcnw6jnCh --page-all
→ need_user_authorization
→ required scope: wiki:node:retrieve
```

因此没有读取或引用任何 Feishu 正文。以下自动同步页只记录为**指针**，不作为协议证据：

- [#214 Feishu snapshot](https://dptechnology.feishu.cn/wiki/F73tw4teRiuLJekesFccBr0gn2b)
- [#224 Feishu snapshot](https://dptechnology.feishu.cn/wiki/PGOUwS0LIieKeGk42UAcyZRXnfe)
- [#225 Feishu snapshot](https://dptechnology.feishu.cn/wiki/D9OIwoXHXiyS2fkBwNtchWL5n1e)
- [#226 Feishu snapshot](https://dptechnology.feishu.cn/wiki/T0ijwTTK8iBoHDkiPCkc6QyunGc)

## 本地 Context / ADR 核查

- Core `origin/main@c4fb5937` 没有根 `CONTEXT.md`、`CONTEXT-MAP.md` 或 `docs/adr/`。
- OS 当前本地合并基线的 `CONTEXT.md` 把 **Shared Interface** 定义为 Backend 与 Edge/Workspace Adapter 对前端展示的同一公共合同，把 **Authority** 定义为一次操作唯一可写 owner，把 **Control Plane** 定义为 local 或 backend 二选一；这与 #225 一致。该文件位于未推送的本地 commit `57aaf11a`，因此只记录 commit/path，不生成不可访问的 GitHub 链接。
- OS 唯一 ADR `docs/adr/0001-debug-launch-material-inference.md` 处理 Debug Launch 物料推断，不影响机械臂 Exclusive、joint telemetry 或模型拓扑。
- FE 基线没有 CONTEXT/ADR。

## 结论

历史决策并非整体作废：#214 的 PointSet/WorkCell 资产模型与 #224 的运动学身份、真实 JointState、latest/stale、只读边界仍是本轮基础。真正被 #225 改写的是**控制复杂度与传输拓扑**：机器人专属 commissioning session 收敛为通用简单 Exclusive；本地完整 `push_joint_state` WebSocket 收敛为 Edge HTTP fact + existing WS notification + Authority memory latest + independent frontend SSE。后续 spec/tickets 应引用这份总账作为 decision context，但只能把 #225 的一行 gist/context pointer 写回 Wayfinder Map，不能把全部正文复制进 Map。
