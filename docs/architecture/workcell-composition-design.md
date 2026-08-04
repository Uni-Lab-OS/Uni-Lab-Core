# 候选工作单元（WorkCell）组合定义、启动与分层动作设计

> 状态：协议已冻结，待实现与跨仓验收
> 合同草案版本：`workcell-composition-draft-20260805-g1-frozen`
> 父地图：[Core #181](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181)
> 历史来源：#181 拆票前最后一份完整正文（2026-08-04 17:18，Asia/Shanghai）
> 对齐范围：D1～D5 与 G1 的协议决策已全部收口；D2-06 的真实物料预置执行链已明确推迟到 v2+。后续工作是各仓实现与跨仓验收。

本文是候选工作单元（WorkCell）功能的独立、长期可维护设计文档。GitHub Issue 继续拥有
决策状态、负责人、讨论和验收权威；本文负责保存整体设计及各协议面的共同背景。若本文与已接受的
Issue 决策冲突，以 Issue 的最新已接受决策为准，并应立即修订本文。

候选工作单元（WorkCell）及本文中的若干派生术语尚未进入根规范词汇表（Canonical Glossary）。
在术语正式确认前，本文统一加“候选”前缀，不把候选名称传播为已冻结共享 Schema。

## 1. 目标

让一组设备、固定资源、库位（Site）、连接、物理位姿和内部工作流（Workflow）形成一个稳定、
可版本化、可嵌套的候选工作单元定义（WorkCell Definition）。人和 AI 可以用受限 Python、规范
JSON 或结构化画布创作同一语义定义；真实或仿真部署再按需绑定启动参数，生成可审计的候选启用快照
（Activation Snapshot）。

候选工作单元（WorkCell）还可以把内部工作流（Workflow）显式发布为公共动作（Action），但运行时
仍只有一个工作流任务（WorkflowTask）、一个不可变执行计划（ExecutionPlan）和一个调度器
（Scheduler）权威。

```text
Python / 规范 JSON / 结构化画布
              │ 单草稿、单时刻单写
              ▼
候选工作单元定义（WorkCell Definition）草稿
              │ compile / link / validate / canonicalize
              ▼
已发布候选工作单元定义（immutable revision + digest）
              │ zero/one activation request + secret reference
              ▼
候选启用解析器（Activation Resolver）
              ├─ 候选启用快照（Activation Snapshot）
              └─ 候选启用图（Activation Graph）与设备注册表（Device Registry）投影
              │ public workflow-backed action invocation
              ▼
唯一工作流任务（WorkflowTask）与执行计划（ExecutionPlan）
```

核心不变量：

```text
定义组合 ≠ 运行实例 ≠ 物料（Material）状态 ≠ 工作流任务（WorkflowTask）执行计划
可查看内部结构 ≠ 可以寻址内部成员
发现/注册定义 ≠ 实例化设备 ≠ 连接硬件
参数输入可以缺席 ≠ 候选启用快照（Activation Snapshot）可以缺席
```

## 2. 状态与决策台账

| 编号 | 状态 | 决策 |
| --- | --- | --- |
| D1-01 | 已接受 | 候选工作单元定义（WorkCell Definition）是一等、可版本化定义；启用实例拥有独立身份。 |
| D1-02 | 已接受 | v1 结构固定；不支持候选结构选择（StructuralChoice）、`optional`/`variant` 或动态拓扑。 |
| D1-03 | 已接受 | 保留 `@workcell` 函数语法，Python 定义文件可以直接作为 `-g/--graph` 启动输入。 |
| D1-04 | 已接受 | Python 与规范 JSON/结构化画布允许双向语义创作；同一草稿同一时刻只有一种可写模式。 |
| D1-05 | 已接受 | 不承诺源码字节无损；发布前必须满足 `graph -> Python -> graph` 规范 digest 固定点。 |
| D1-06～07 | 已接受 | 全部选择 A：受限 Python 使用失败关闭 AST allowlist；定义身份为 PackageCatalog fqid、单调 revision 与 digest，`id=` 是稳定 `member_id`。 |
| D1-08 | 已接受 | 选择 A：规范 JSON 直接采用现有字段优先的 NetworkX node-link 形态；精确依赖闭包、规范排序、source map 与结构化诊断失败关闭。 |
| D1-09～11 | 已接受 | 全部选择 A：单草稿 CAS/完整语义 diff；显式 `.py` 与 clean-wheel parity；Draft → Candidate → Published 原子失败关闭。 |
| D2-01 | 已接受（已修订） | 右手 Z-up；`pose.position` 使用毫米，`pose.rotation` 使用度与 XYZ 欧拉合同；2D/3D 编辑共用物理 `pose`，不增加节点级 `ui_layout`。 |
| D2-02 | 已接受 | 选择 A：父子组合统一使用 `assign_child_resource(..., pose=Pose(position=..., rotation=...))`；省略位姿规范化为恒等位姿。 |
| D2-03 | 已接受 | 选择 A：成员位姿始终相对父节点，以变换矩阵递归组合世界位姿；根世界位姿归候选启用图（Activation Graph）。 |
| D2-04 | 已接受 | 选择 A：定义拥有固定结构、物料设计约束和只读投影；库存权威（Inventory Authority）独占真实物料（Material）与库位占用（SiteOccupancy）动态事实。 |
| D2-05 | 已接受 | 选择 A：v1 复用 `config.sites[].label/content_type/position/size`；稳定 key、几何、允许类型与 Backend `sort_order` 投影在发布期校验。 |
| D2-06 | 已决策延期 | v1 只描述和校验物料设计预期，不生成或执行真实物料预置命令；`command_id`、请求摘要、整批事务与持久回执的执行链推迟到 v2+。 |
| D2-07 | 已接受（已修订） | 遗留毫米坐标统一迁移到物理 `pose`；离线适配器（Adapter）对等价重复告警、冲突失败，运行事实不进入定义。 |
| D3-01 | 已接受 | `workcell.py` 是必需作者制品；参数输入是按需存在的覆盖层；每次启用都生成候选启用快照（Activation Snapshot）。 |
| D3-02 | 已接受 | 选择 A：零覆盖不创建空 params 文件或持久记录；“无覆盖”以参数输入缺席表示，候选启用快照（Activation Snapshot）仍须持久化。 |
| D3-03 | 已接受 | 选择 A：一次启用最多接受一个外部覆盖对象；多个外部来源同时出现时失败，不做隐式叠加或优先级合并。 |
| D3-04 | 已接受 | 选择 A：Phase 0 仅实现 Python-only 零外部参数路径；完整 v1 保留 D3-03 的单一外部来源合同。 |
| D3-05 | 已接受 | 复用 `-g/--graph` 作为唯一启动定义来源参数，不新增 `--workcell`。 |
| D3-06 | 已接受 | 选择 A：`-g/--graph` 严格按 `.py`、`.json`、`.graphml` 后缀分派；未知或无后缀失败，不做内容探测。 |
| D3-07 | 已接受 | 选择 A：一个 `.py` 启动文件必须恰好声明一个顶层 `@workcell` 根定义；零个或多个失败，被引用的嵌套定义不计入。 |
| D3-08 | 已接受 | 选择 A：任意已登记设备作者句柄只消费已发布目录的 `init_param_schema.config`；现代 `@device` 由带类型的 `__init__` 静态生成，作者句柄不另建合同。 |
| D3-09～13 | 已接受 | 全部选择 A：公开参数使用封闭类型闭集；唯一外部输入规范化为候选启用请求（Activation Request）；v1 仅文件启动；实例部署字段与 `InitParam` 分离；敏感配置（Secret）只接受 `SecretRef`。 |
| D3-14～15 | 已接受 | 全部选择 A：Uni-Lab OS 原子持久化内容寻址候选启用快照（Activation Snapshot）；候选启用解析器（Activation Resolver）只公开 `prepare_activation(...)` 深模块接口。 |
| D4-01～07 | 已接受 | 全部选择 A：exact 嵌套闭包与确定性实例身份；封闭 `private`/`exported` 和显式 `re_export`；候选可查看性与候选可寻址性分离；公共能力只允许收窄；定义、目录、设备注册表与运行时投影权威分离；前端展开只影响视图；完整定义与公共合同使用双摘要。 |
| D5 | 已接受 | 显式工作流支持动作（Workflow-backed Action）复用既有工作流目录合同并静态降低；不同调用的内部作业可以交错，只由完整逐作业执行占用保护，不建立整次调用容量合同。 |
| G1-01～02 | 已接受（B′） | 永久支持 `.json`/`.graphml` 输入并无损保留遗留字段，但所有格式必须进入同一规范编译、校验、发布和启用链；兼容数据不获得运行权威。 |
| G1-03～08 | 已接受 | 全部选择 A：动态 `data` 分类隔离；最小仿真与 SZLab 双夹具；语义固定点；真实跨仓集成；失败场景；按仓交付子问题与 Core 总验收门。 |

## 3. 设计边界与权威

### 3.1 候选工作单元定义（WorkCell Definition）

候选工作单元定义（WorkCell Definition）拥有：

- 稳定定义身份、revision、content digest 和公共合同 digest；
- 内部成员引用与稳定 `member_id`/alias；
- 候选定义包含关系（Definition Containment）；
- 库位（Site）绑定、内部连接和候选装配拓扑（Assembly Topology）；
- 内部成员相对父节点的物理 `pose`；
- 公开端口、导出成员、公共动作（Action）和候选工作单元初始化合同（WorkCell Init Contract）；
- 随定义版本化、对所有启用一致且不敏感的私有固定配置和资产引用。

它不拥有真实在线状态、连接凭证明文、真实物料（Material）当前状态、库位占用
（SiteOccupancy）或工作流任务（WorkflowTask）状态。

### 3.2 候选工作单元实例（WorkCell Instance）

候选工作单元实例（WorkCell Instance）是某个候选启用图（Activation Graph）对精确已发布定义的
一次实例化。稳定 `instance_id`、根世界位姿、外部连接和 Edge/机器放置属于实例部署字段，不属于
公开 `InitParam`。Phase 0 使用 `instance_id = workcell.id`、恒等根位姿、当前 Edge 和空外部连接；
完整 v1 由唯一候选启用请求（Activation Request）提供。改变 `instance_id` 创建新实例；改变其他部署
字段为同一实例创建新快照。定义 revision 更新不得静默改变既有实例或已创建工作流任务（WorkflowTask）。

### 3.3 三种图必须分离

| 图 | 权威 | 包含 | 不包含 |
| --- | --- | --- | --- |
| 候选装配拓扑（Assembly Topology） | 已发布候选工作单元定义（WorkCell Definition） | 成员、包含、库位（Site）绑定、内部连接、相对位姿、公共合同 | 真实实例、凭证、物料（Material）当前状态、任务状态 |
| 候选启用图（Activation Graph） | 部署/启用权威 | 实例身份、根世界位姿、外部连接、机器放置、允许的参数覆盖 | 可变定义、工作流任务（WorkflowTask）有向无环图（DAG） |
| 执行计划（ExecutionPlan） | 工作流任务（WorkflowTask）/调度器（Scheduler）合同 | 某次任务的冻结拓扑、绑定、执行要求和占用意图（ClaimIntent） | 实时可用性、预留/占用事实和物理结果 |

### 3.4 物料与运行事实边界

资源模板（ResourceTemplate）、允许出现的固定资源结构、库位（Site）、允许模板、预期数量和目标
库位可以进入定义。真实物料（Material）UUID、条码、批次、当前数量、库存分配和库位占用
（SiteOccupancy）归库存权威（Inventory Authority），不得由 `workcell.py`、参数输入或每次重启覆盖。
候选工作单元实例（WorkCell Instance）可以查询或订阅这些事实形成只读物料投影，但投影和缓存均
不取得写权威。

任务物料准入（TaskMaterialAdmission）、任务物料预留（TaskMaterialReservation）、作业执行占用
（JobExecutionClaim）、设备遥测投影（DeviceTelemetryProjection）和物理结算（PhysicalSettlement）
继续留在各自运行权威中。动态物料缺失不阻止候选工作单元（WorkCell）启用；相关工作流任务
（WorkflowTask）是否可开始由任务物料准入（TaskMaterialAdmission）判定。安全必需且不可动态缺失的
固定反应器、废液桶等必须建模为固定结构成员或启用前置条件。

v1 只允许候选工作单元定义（WorkCell Definition）保存和校验模板、预期数量与目标库位（Site）等
设计预期，并在创作或检查界面展示差异。它不生成可执行的真实物料预置命令，不创建或移动真实物料
（Material），不写库位占用（SiteOccupancy），不扩展 `processed_command`，也不在候选启用快照
（Activation Snapshot）中记录预置命令或回执引用。首次安装所需的真实物料继续由操作者通过现有库存
权威（Inventory Authority）接口准备；候选工作单元（WorkCell）启用、重启和定义升级始终零物料写入。

#### 推迟到 v2+ 的目标机制

以下首次真实物料预置机制保留为 v2+ 候选目标，不属于 v1 实现范围或接受门。未来若重开，应采用
显式授权、可安全重试且逻辑效果至多一次的机制，而不是 `executed=true` 布尔标志：

1. 编译精确已发布定义，生成只含模板、数量和目标库位的规范计划及 `provisioning_digest`；生成计划
   本身没有副作用，候选工作单元启用也不会自动提交该计划。
2. 操作者检查计划与现场差异后显式授权。授权方创建并持久化一个不可变 `command_id`；请求同时携带
   `definition_digest`、`provisioning_digest`、候选工作单元实例身份和完整规范计划。`command_id` 是
   这次授权的身份，不能仅由库位或定义摘要推导，否则无法区分未来一次有意重新预置。
3. 单一库存权威（Inventory Authority）在幂等命令表中以 `command_id` 为主键，并保存完整请求的
   `request_digest`、状态、结果或错误、`receipt_id` 与处理时间。并发请求依靠数据库唯一约束串行化，
   禁止先查询再在事务外写入。
4. 认领命令、校验计划、生成真实物料（Material）UUID、写入所有物料和库位占用（SiteOccupancy）、
   台账、事务发件箱（Outbox）、回执（Receipt）及完成状态必须在库存权威的同一数据库事务中提交。
   任一条目失败则全部回滚，不允许留下部分预置。
5. 同一 `command_id` 与同一 `request_digest` 重放时，直接返回已持久化的原回执；同一 `command_id`
   携带不同摘要时以 `idempotency_conflict` 失败。进程在提交前崩溃则事务回滚，重试重新执行；在提交后、
   响应前崩溃则重试读取原回执，不再创建第二批物料。
6. 候选启用快照（Activation Snapshot）只记录计划摘要、`command_id` 和 `receipt_id` 引用，不复制真实
   物料或库位占用。重启只恢复既有库存事实，不扫描定义并重新提交预置命令。
7. 定义升级只生成计划差异。确需再次预置时，必须由操作者审阅差异、产生新的显式授权和新的
   `command_id`；旧命令永远不能被“重置为未执行”。生产重置与仿真清场使用独立显式命令或隔离库存
   命名空间（namespace），不复用启动语义。

上述保证精确限定为“库存逻辑效果至多一次 + 请求可安全重试”。如果计划包含机器人搬运等外部硬件
副作用，数据库事务无法回滚物理世界；这类步骤必须降低为工作流（Workflow），使用作业执行占用
（JobExecutionClaim）、变更集（ChangeSet）和回执（Receipt）结算，不得由物料预置命令直接声称
物理恰好一次（exactly-once）。

当前 Uni-Lab OS 的 `processed_command` 已具备 `command_id` 主键、同一事务内认领/业务写入/台账/
事务发件箱（Outbox）/结果持久化和重放返回，可作为实现接缝。它目前尚未持久化 `request_digest`，
因此未来实施 v2+ 预置合同前必须补齐“同身份不同内容拒绝”校验，并增加整批预置的领域命令和持久
回执；不能直接把现有单物料命令循环调用后宣称整批原子。这些改造均不得成为 v1 交付依赖。

## 4. 创作模型

### 4.1 Python 直接启动语法

`@workcell` 函数同时定义固定结构和公开启动合同。成员相对父节点的物理 `pose` 放在组合关系上，
不塞进设备工厂的初始化字段。

```python
from typing import Annotated

from unilabos.workcell import InitParam, Pose, WorkCell, workcell
from szlab_poly_studio.devices import mixer_robot, plc, pump_station


@workcell(
    id="szlab_poly_station",
    display_name="SZLab 聚合物工作站",
    version="1.0.0",
    layout_plane="XY",
)
def szlab_poly_station(
    *,
    auto_connect: Annotated[bool, InitParam(title="Start device connections")] = True,
    pump_timeout_s: Annotated[
        float, InitParam(title="Pump timeout", ge=0.1, le=30.0, unit="s")
    ] = 5.0,
) -> WorkCell:
    cell = WorkCell()
    plc_1 = plc(id="plc", url="opc.tcp://127.0.0.1:4840", auto_connect=auto_connect,
                csv_path="assets/szlab_plc_0730.csv")
    robot = mixer_robot(id="robot", plc_device=plc_1, auto_connect=auto_connect)
    pump = pump_station(id="pump", plc_device=plc_1, timeout_s=pump_timeout_s)
    cell.assign_child_resource(
        plc_1, pose=Pose(position=(0.0, 0.0, 0.0),
                         rotation=(0.0, 0.0, 0.0)),
    )
    cell.assign_child_resource(
        robot, pose=Pose(position=(1200.0, 350.0, 0.0),
                         rotation=(0.0, 0.0, 90.0)),
    )
    cell.assign_child_resource(
        pump, pose=Pose(position=(700.0, 350.0, 0.0),
                        rotation=(0.0, 0.0, 0.0)),
    )
    return cell
```

上例所有公开参数都有默认值，因此可以只提供 Python：

```bash
unilab --workspace . -g deployment/workcell.py --backend ros
```

没有公开 `InitParam` 时同样只需 Python。Phase 0 不接受外部参数；存在无默认值参数、现场覆盖或
敏感配置（Secret）引用的定义必须明确拒绝启用，后续切片再按 D3-03 接受单一外部覆盖对象。

### 4.2 v1 固定结构

v1 的参数只能绑定已声明的内部初始化字段，不能选择成员 class、definition revision、member alias、
父子关系、库位（Site）、导出成员或动作（Action）合同。`optional`、`variant`、循环生成和动态拓扑
不进入 v1；未来若有真实需求，应增加显式版本化 AST/IR 节点，而不是重新解释现有语法。

### 4.3 受控双向创作

同一候选工作单元定义草稿（WorkCell Definition Draft）可以在两种模式之间切换：

```text
Python 写模式
  -> compile / link / validate
  -> 候选定义图（Candidate Definition Graph）

规范 JSON / 结构化画布写模式
  -> schema / semantic validate
  -> generate normalized Python
  -> 完整 diff + 人工接受
  -> 重新 compile
  -> graph digest 固定点校验
```

约束：

- 同一草稿只有一个 `draft_revision` 和当前可写模式；保存携带 base revision/digest 做 CAS；
- 切换前编译、校验并展示完整语义 diff；冲突不自动合并或强制覆盖，必须显式 rebase；
- 语义往返不承诺注释、空行、局部变量风格和 import 排列的字节级无损；
- 稳定 `member_id`、引用、嵌套 definition digest 和 source map 不能靠变量名或数组顺序猜测；
- AI 可以修改 Python，也可以提交有类型图编辑/JSON Patch，但必须经过同一 compiler/generator/validator；
- 无效草稿可以保存和诊断，但不能替换最后一个有效候选图，也不能发布或启用。

### 4.4 现有字段优先的规范 JSON

已发布候选工作单元定义（WorkCell Definition）的规范 JSON 自身就是 NetworkX node-link
文档，不另套 `manifest/payload/assembly_graph` envelope：

```python
assembly_graph = nx.node_link_graph(
    document,
    edges="links",
    key="id",
)
```

顶层使用 `directed`、`multigraph`、`graph`、`nodes` 和 `links`。`graph` 保存
`schema_version/id/name/display_name/definition_fqid/version/revision/content_digest/`
`public_contract_digest/init_param_schema/dependencies/assets/layout_plane`。`init_param_schema` 沿用 Backend
`{"config":{"properties":{...}}}` 形态；`dependencies[class]` 保存精确 `revision` 和
`content_digest`，不再为每个节点引入重复 `definition_ref`。

节点继续使用 `id/name/type/class/parent/children/pose/config/data`：

- `id` 是定义内稳定 `member_id`；`parent` 与 `children` 必须严格互逆；
- `children` 与 `config.sites` 的数组顺序具有语义，不在规范化时重排；
- `pose` 是相对父节点的物理位姿；物理坐标固定为右手 Z-up，根坐标 X 向右、Y 远离工站正面、
  Z 向上；`position.{x,y,z}` 使用毫米，`rotation.{x,y,z}` 使用度；
- XYZ 欧拉角按列向量矩阵 `Rz(z) · Ry(y) · Rx(x)` 解释；拒绝 NaN/Infinity，将 `-0` 规范为 `0`，
  角度规范到 `[-180, 180)`，不做任意小数位舍入；
- 省略 `pose` 规范化为全零恒等位姿；物理可渲染成员省略时产生结构化告警，Python 生成器始终输出
  显式 `pose`；
- 2D 与 3D 编辑器共享同一物理 `pose`；候选工作单元定义（WorkCell Definition）不增加节点级
  `ui_layout`，也不保存第二套像素或显示坐标；
- `config` 只保存定义期固定 JSON 值；规范定义中的 `data` 必须是 `{}`。遗留非空 `data` 和未知字段只进入
  无损兼容保留层，不获得定义、启用或运行语义；
- 唯一必需的新节点字段是可选 `config_bindings`，其 `type` 仅允许 `member` 或
  `init_param`；候选启用解析器（Activation Resolver）将它降低为交给 OS/Backend 的普通 `config`；
- `config.sites[]` 继续使用 `label/content_type/position/size`，数组位置映射 Backend
  `sort_order`；`label` 在所属成员内唯一且稳定，`position/size` 使用毫米并相对所属成员根，v1 容量
  固定为 1；`content_type` 必须经 PackageCatalog 解析为 Backend 允许的资源模板（ResourceTemplate）
  UUID；禁止 `occupied_by/occupied_material_uuid`，因为它们是库位占用（SiteOccupancy）事实。首次
  物化后，持久 `Site.sort_order` 是传感器数组映射的权威顺序，运行时不得按名称或实时数组顺序重排。

`links[*]` 保持 `id/source/target/type/port`，NetworkX 通过 `key="id"` 使用稳定边身份。
规范编码时 `nodes` 按 `id`、`links` 按 `id` 排序；`content_digest` 只排除
`graph.content_digest` 自身，也不包含无损兼容保留层。`legacy_payload_digest` 单独覆盖规范化后的遗留保留
载荷；原始文件另记录字节摘要。source map 是绑定内容摘要的 sidecar，诊断统一为
`code/path/source_span/message/hint`。

### 4.5 物理布置编辑与 `layout_plane`

候选工作单元（WorkCell）的 2D 编辑器是毫米制物理布置编辑器，不是任意流程画布。2D 和 3D 读取、
编辑同一个 `pose`；2D 拖动直接修改所选平面对应的两个物理坐标，未显示的第三轴保持不变。候选工作
单元定义（WorkCell Definition）因此不保存节点级 `ui_layout`，也不从像素坐标推导毫米坐标。

定义级可选字段 `layout_plane` 只选择 2D 编辑器的观察/约束平面：

- `XY`：显示并编辑 X/Y，保持 Z；
- `XZ`：显示并编辑 X/Z，保持 Y；
- `YZ`：显示并编辑 Y/Z，保持 X；
- 省略：没有首选 2D 平面，编辑器可进入 3D 或要求用户选择平面。

Python 使用 `layout_plane: Literal["XY", "XZ", "YZ"] | None = None` 的语义；规范 JSON 仅在有首选
平面时保存 `graph.layout_plane`。UI 中的“None”选项规范化为 Python `None` / JSON 字段缺席，字符串
`"None"` 不是 wire enum，避免“字段缺席”和“字符串哨兵”形成两种空值。

`layout_plane` 不是第二坐标系，不改变右手 Z-up、父子变换、轴方向、单位或 Backend
`relative_position`，也不把未显示轴强制归零。嵌套定义各自拥有首选平面；编辑外层组合时使用外层
`layout_plane` 投影子候选工作单元实例（WorkCell Instance）的根 `pose`，进入内层编辑后使用内层值。

作者在草稿（Draft）中修改 `pose` 只改变数字模型，不直接产生硬件副作用，也不会自动搬动真实设备。
保存/发布会形成新的候选工作单元定义 revision；既有候选启用快照（Activation Snapshot）和正在运行的
工作流任务（WorkflowTask）继续固定旧 revision。只有显式重新启用后，新的 `pose` 才进入后续运行模型；
若动作（Action）使用这些坐标，后续执行会使用新模型，因此重新启用前仍必须校验测绘结果。

规范 JSON 示例：

```json
{
  "graph": {
    "id": "szlab_poly_station",
    "layout_plane": "XY"
  },
  "nodes": [
    {
      "id": "robot",
      "pose": {
        "position": {"x": 1200.0, "y": 350.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 90.0}
      }
    }
  ]
}
```

### 4.6 父子变换与遗留位置迁移

每个节点的 `pose` 永远相对其 `parent`。嵌套候选工作单元（WorkCell）的世界变换按矩阵递归组合：

```text
T_world(child) = T_world(parent) · T_parent(child)
```

欧拉角只作为定义输入和派生展示，不把矩阵组合结果反写为新的定义欧拉角。根世界位姿由候选启用图
（Activation Graph）拥有；未提供时使用恒等位姿。父子环、缺失父节点、同一成员出现两个父节点，
以及 `parent`/`children` 反向关系不一致，均在发布前失败。

遗留 `position`、`pose.position`、`position3d` 与 `rotation` 必须由离线适配器（Adapter）输出规范图和
迁移报告。来源唯一时才归一到 `pose`；多个来源等价时保留一份并告警；冲突时失败并报告精确 JSON
路径。遗留 2D 编辑器的毫米坐标也迁移到物理 `pose`，不分流到 `ui_layout`。若旧载荷只有两个坐标，
适配器必须结合已知 `layout_plane` 和另一条无歧义来源补足未显示轴；无法证明第三轴时失败，不静默归零。
`occupied_by`、真实物料（Material）身份和库位占用（SiteOccupancy）不得进入定义，只能由库存权威
（Inventory Authority）的独立迁移处理。非空 `data` 按分类报告处理：测试 seed 进入独立测试夹具，
运行时事实排除，无法分类的非空 `data` 原样进入无损兼容保留层，但发布与启用失败关闭，直到完成
分类；任何兼容保留值都不下发驱动。v1 不生成或接受可执行物料预置候选。

定义中不保存 Backend 运行实例字段 `uuid/resource_template_uuid/parent_uuid/relative_position`。
候选启用快照（Activation Snapshot）从实例 namespace 和 `member_id` 确定性派生
`uuid/parent_uuid`，经固定 PackageCatalog 将 `class` 解析为部署的
`resource_template_uuid`，并把 `pose` 投影为 Backend `relative_position`。这保证 workspace、
clean wheel 与缓存 archive 的定义摘要不被数据库 UUID 污染。

## 5. 发布、组合与设备注册表（Device Registry）

```text
Authoring Draft
  -> Candidate WorkCell Definition
  -> Definition Link（exact dependency closure + cycle check）
  -> Published WorkCell Definition（immutable revision + digest）
       ├── PackageCatalog entry
       ├── Composite Device Projection
       ├── Palette projection
       └── activation resolver input
```

草稿（Draft）可变；候选定义（Candidate）是绑定草稿 revision、诊断和规范摘要的不可变编译结果；已发布定义（Published Definition）是唯一可被引用或启用的不可变 revision。发布以 CAS 锁定草稿，
重新编译精确闭包并验证 digest 固定点后原子提交定义、公共合同、source map 与目录。任一步失败均保留
旧 Published 与可诊断 Draft，不产生部分发布。Draft/Candidate 不进入设备注册表（Device Registry）；Published 才能产生
候选复合设备投影（Composite Device Projection）。

D4-05 与 D4-07 把四类权威和两个摘要分开：

- 不可变 Published 制品拥有完整候选装配拓扑（Assembly Topology）、精确依赖闭包、完整检查图和 source map；
- PackageCatalog 只索引定义 fqid、revision、`definition_digest`、`public_contract_digest` 和公共合同；
- 设备注册表（Device Registry）只保存从 Published 制品派生的候选复合设备投影（Composite Device Projection），不成为装配图的第二写权威；
- 候选启用运行时拥有活跃候选工作单元实例（WorkCell Instance）的状态，设备注册表（Device Registry）只接收只读实例投影；前端不拥有上述事实；
- `definition_digest` 覆盖完整定义、私有实现和 exact dependency closure；`public_contract_digest` 只覆盖可寻址公共边界；
- 私有实现变化必须产生新 revision 和 `definition_digest`，但公共合同不变时可以保留 `public_contract_digest`；外层仍须显式 re-link/re-publish；
- 摘要不同只证明内容不同，兼容性由结构化合同比较判断，不能把 digest 差异直接解释为破坏性变化。

一个已发布定义可以作为另一个候选工作单元定义（WorkCell Definition）的内部成员。D4-01 接受以下
闭包与身份合同：

- 每条嵌套边固定内层 `definition_fqid`、revision、`definition_digest` 和外层稳定 `member_id`，不复制一份可独立编辑的定义；
- 完整 `member_id` 路径形成稳定 namespace，同一内层定义可以实例化多次；
- 子成员运行 UUID 以根候选工作单元实例（WorkCell Instance）UUID 与完整 `member_id` 路径确定性 UUIDv5 派生；同一实例重启保持稳定，不同实例隔离；
- 发布前按精确定义 revision 身份递归计算闭包并拒绝直接或间接循环；
- 外层只能连接内层公共端口、公共库位（Site）或显式导出成员；
- 内层升级不改写已发布外层，外层必须显式 re-link、preview、validate、publish。

外层为内层实例声明的 `pose` 相对外层父节点；内层成员继续相对内层根。世界位姿只通过上述矩阵合同
递归派生，不把内层定义拍平成绝对坐标，也不把候选启用图（Activation Graph）的根世界位姿写回定义。

D4-02 与 D4-03 规定：

- 本地符号的可见性是封闭的 `private | exported`；外层 `re_export` 是显式命名映射，只能转导内层已经 `exported` 的符号；
- 通配符、自动传递导出、重名、目标缺失和把 `private` 提权都在发布前失败；
- 候选可查看性（Inspectability，候选术语）与候选可寻址性（Addressability，候选术语）严格分离；
- 授权维护者可以按需读取私有成员的只读诊断投影，但不会因此获得可供外层工作流（Workflow）、连接或初始化绑定使用的地址；
- 只有显式公共边界拥有稳定可寻址句柄；v1 不提供绕过公共边界的诊断直控。

D4-04 使用显式公共导出表：

- 公共端口保持方向和类型兼容；
- 公共库位（Site）使用稳定外部句柄一对一映射一个已经导出的内部库位（Site）；
- 公共动作（Action）只能导出已发布内部动作（Action）或工作流支持动作（Workflow-backed Action）；
- 能力收窄可以绑定或隐藏已经固定的输入、缩小枚举/数值范围和减少能力集合，但不得扩大输入域、改变单位或方向、重解释效果语义或凭空增加内部能力；
- 任一公共映射缺失、不兼容或越权都拒绝发布。

D4-06 规定 Palette 只列出 Published 定义。折叠/展开是用户界面视图状态，不进入规范定义摘要，也不
改变物理 `pose`、运行拓扑或可寻址性。授权私有检查图只读、按需加载；活跃实例状态作为独立运行时
叠层显示。源码导航使用“定义摘要 + package 内相对路径 + source span”，禁止个人绝对路径，并从公共
投影稳定定位到对应定义源码。

## 6. 启动参数与候选启用快照（Activation Snapshot）

### 6.1 制品模型

一个候选工作单元（WorkCell）项目具有：

1. 必需作者制品 `workcell.py`：拥有固定结构、相对位姿、私有固定配置和候选工作单元初始化合同；
2. 按需存在的参数覆盖：小型强类型 JSON、表单提交或持久部署记录，只保存公开参数覆盖和敏感配置（Secret）引用；
3. 每次成功启用都生成的系统制品：候选启用快照（Activation Snapshot）。

D3-02 选择 A：零覆盖时不创建或持久化空 `{}` 参数记录。“无覆盖”就是参数输入缺席。候选启用快照
（Activation Snapshot）仍须生成和持久化，记录默认值解析结果、定义/目录指纹、实例身份、根位姿、
来源和降低结果。它不得保存敏感配置（Secret）明文。

### 6.2 公开与私有初始化字段

任意已登记设备作者句柄都只消费已发布目录的 `init_param_schema.config`。现代 `@device` 的该合同
由带类型的驱动 `__init__` 静态生成并在发布时冻结；遗留 YAML 只能为遗留设备生成同一字段，不能作为
并行覆盖层。候选工作单元初始化合同（WorkCell Init Contract）只由 `@workcell` 的公开 `InitParam` 派生。

- 固定、非敏感且对该定义所有启用一致的站内设备值可以写在 Python 定义中；
- 随物理安装变化、需要外部选择或属于敏感配置（Secret）的值必须提升为公开 `InitParam`；
- 外部不能用 `members.plc.config.*` 或 `devices.plc.url` 一类深路径覆盖私有字段；
- 外层候选工作单元（WorkCell）只能绑定内层的公开参数，不能越过内层合同；
- v1 类型闭集为 JSON 标量、`Literal`/Enum、`Optional[T]`、有界同质 `list[T]`、封闭 `TypedDict`/
  冻结 dataclass 和 `Secret[str]`；禁止 `Any`、无类型 `dict`、任意对象及除 `Optional` 外的 union；
- 约束只由 `Annotated[..., InitParam(...)]` 声明；一个公开参数可以 fan-out 到多个兼容目标；
- fan-out 必须同时满足所有目标 Schema，不做字符串、数字或单位隐式转换；安全交集为空即失败。

### 6.3 参数来源

已接受的 D3-03=A 合同是“定义默认值 + 零或一个外部覆盖对象”。存在覆盖时，params 文档、持久部署
记录或 UI/API 提交只能选一个来源，并规范化为封闭候选启用请求（Activation Request）：顶层只有
`schema_version`、必需 `definition_digest`、`instance` 和 `params`；`params` 再按候选工作单元初始化合同
（WorkCell Init Contract）封闭校验。零外部输入时整个对象缺席；未知顶层字段、digest 不符或第二来源
都在硬件副作用前失败。候选启用快照（Activation Snapshot）记录每个最终值的来源。

D3-04=A 把 Phase 0 限定为 Python-only 零外部参数子集：只能启用零公开参数或全部参数已有默认值且
不依赖敏感配置（Secret）引用的定义。任何外部参数输入都必须明确报“尚未支持”，不能静默忽略；
系统仍须完成合同校验、默认值解析并持久化脱敏候选启用快照（Activation Snapshot）。

敏感配置（Secret）只接受封闭 `SecretRef {provider, key, version?}`。Secret Provider 作为候选启用解析器
（Activation Resolver）的内部 Adapter，在全部非敏感校验后、驱动构造前解析。定义、PackageCatalog、
设备注册表（Device Registry）、source map、日志、诊断和快照只保留引用、版本和指纹，不得包含明文。
v1 不支持热轮换；版本变化要求显式重新启用并生成新快照。

### 6.4 CLI 语义

目标 CLI 复用现有 `-g/--graph` 作为唯一启动定义来源参数，不新增 `--workcell`：

```bash
unilab \
  --workspace . \
  -g deployment/workcell.py \
  --backend ros

unilab \
  --workspace . \
  -g legacy/startup.json \
  --backend ros
```

已接受规则：

- `-g` 与 `--graph` 是同一参数的短/长形式，不能再增加并行启动来源参数；
- 文件必须位于显式 workspace 内并经过 containment/symlink 检查；
- `.py` 进入受限 AST 候选工作单元定义（WorkCell Definition）编译器，不 import/exec 作者源码，且必须恰好包含一个顶层 `@workcell` 根定义；
- `.json` 与 `.graphml` 是永久支持的兼容作者输入；各自 Adapter 只负责解析、分类和无损保留，随后与
  `.py` 一样进入同一规范编译、链接、校验、发布和候选启用解析器（Activation Resolver）；
- 不保留第二套设备实例化或运行语义；禁止 trusted-exec、`eval`、任意 import/exec 和失败回退；
- 未知或无后缀直接失败，不做内容探测，也不把其他格式回退为 GraphML；
- v1 不实现 `catalog:`，生产也从 workspace/package 内显式文件启动；未来目录引用必须固定 exact revision/
  digest，禁止 `latest`，且不能与文件来源同时出现；
- Phase 0 出现任何外部参数输入时必须明确失败；
- `--config` 继续只配置 Uni-Lab OS 进程，不进入候选工作单元初始化合同；
- params 输入是 closed object，未知字段失败；命令行不得携带敏感配置（Secret）明文；
- `--check_mode` 在首个 driver import、构造和硬件连接前完成全部验证并退出。

### 6.5 启动顺序

候选启用解析器（Activation Resolver）是深模块（Deep Module），对调用方只公开
`prepare_activation(request) -> PreparedActivation | ActivationDiagnostics`。文件、目录、Secret Provider
和快照存储 Adapter 是内部 seam；CLI、UI/API 与 `--check_mode` 不能自行编排解析阶段。

```text
解析 OS 进程配置
  -> 编译显式 PackageCatalog
  -> 解析 `-g/--graph` 唯一启动定义来源
  -> link exact definition closure
  -> 解析可选参数覆盖与默认值
  -> 校验 internal init bindings
  -> 解析 secret references
  -> 降低为候选启用图（Activation Graph）
  -> 原子持久化候选启用快照（Activation Snapshot）
  -> 返回 PreparedActivation 或稳定 ActivationDiagnostics
  -> import/initialize selected drivers
```

Uni-Lab OS 是候选启用快照（Activation Snapshot）的本地写权威：在驱动创建前原子持久化不可变、
内容寻址快照；Backend 只接收副本/投影。快照包含定义/目录/请求/lowering digest、稳定实例部署、最终
非敏感值及来源、Secret 引用版本和候选启用图（Activation Graph）digest。输入变化要求显式重新启用；
重启只自动复用完全相同的 digest。Phase 0 收到外部输入可保留默认解析快照，但必须标记不可启用且不
产生 launch plan。诊断固定为 `code/path/source_span/message/hint`；任一失败都不得留下部分 driver、
部分设备注册表（Device Registry）实例或任何真实物料（Material）/库位占用（SiteOccupancy）写入。

## 7. 分层动作（Action）

内部设备动作（Action）默认只供候选工作单元实现使用，不自动暴露到外层。作者可以显式导出成员
能力，也可以把一个已发布内部工作流（Workflow）发布为公共动作（Action）。

v1 已接受运行模型：

- 作者只通过 `cell.expose_workflow_action(id=..., workflow=...)` 显式导出；节点数、设备数、函数名和
  `plc(...)` 一类示例调用都不产生隐式导出；
- `workflow` 必须解析到 PackageCatalog 中已发布工作流（Workflow）的精确 revision/digest；公共动作身份
  由候选工作单元定义（WorkCell Definition）fqid 与稳定 `action_id` 共同确定；
- 不引入 `implementation.kind`。目录复用既有 `type="workflow"`、`node_type="workflow"`、
  `schema.x-unilabos-workflow-contract`、模板/Handle 身份和候选工作单元（WorkCell）公共导出映射，
  因而不会冒充直接设备动作；
- 输入/输出分别复用工作流输入合同（WorkflowInputContract）与工作流结果记录
  （WorkflowResultRecord）；边界复用真实 Handle、物料占位符（ResourceSlot）和既有 `SiteSelector`，
  不新增候选工作单元（WorkCell）专属 entry/exit 模型，也不从名称、顺序、位姿或库位占用
  （SiteOccupancy）推断边界；
- 父工作流（Workflow）中的调用复用组合工作流调用（CompositeWorkflowInvocation）、真实边界句柄、
  UUIDv5 和 #178 既有边界映射合同；父已应用工作流图（Applied Workflow Graph）保存精确固定的内部展开图；
- 工作流任务（WorkflowTask）提交时，由唯一执行计划构建器（ExecutionPlan Builder）把内部节点降低为
  普通计划节点和工作流节点作业尝试（WorkflowNodeJobAttempt）；不创建宏作业、合成屏障、嵌套任务
  或第二调度权威；
- 不同调用同一候选工作单元实例（WorkCell Instance）时，内部作业允许交错；v1 不提供整次调用串行、
  容量 N、`max_concurrency` 或调用期许可合同；
- 每个普通内部作业都必须在派发前取得完整、持久、带栅栏的作业执行占用
  （JobExecutionClaim），覆盖具体执行设备、可能改变的全部物料（Material）和源/目标库位（Site）；
  若还存在未建模的共用门、轨道、安全区或机箱风险，该定义不得宣称并发安全，必须先把风险建模为
  可占用资源或另开版本化协议；
- 不增加调用级 mutex、semaphore、表或候选调用容量许可；逐作业执行占用只保护各自物理执行，
  不承诺同时存活的候选工作单元调用数量上限；
- 动作重试策略（ActionRetryPolicy）保持 `never`；取消、部分物理成功、执行未知、投递重放
  （DeliveryReplay）和物理结算（PhysicalSettlement）继续由每个真实内部作业的安全合同处理，不能把
  整次候选工作单元动作重新执行；
- 前端折叠只影响展示，不能删除内部工作流节点作业尝试（WorkflowNodeJobAttempt）、占用意图
  （ClaimIntent）、回执（Receipt）、source map 或物理结算（PhysicalSettlement）证据。

## 8. 推迟的候选计划生成器（Plan Generator）

拆票前设计包含候选计划生成器（Plan Generator），用于按显式输入和冻结拓扑生成不同数量、顺序或
并行组的动作调用。它不是 v1 门槛，只有静态工作流（Workflow）无法表达一个已验证真实需求时才重开。

若未来启用，至少满足：

- 只在工作流任务（WorkflowTask）提交前产生候选计划片段；
- 输入只来自冻结任务输入、精确候选工作单元定义和版本化规划快照；
- 禁止网络、任意文件 I/O、driver import、硬件连接、动态 import/eval 和全局可变状态；
- 输出经作用域、动作合同、有向无环图（DAG）、资源、安全和预算校验后 canonicalize/hash；
- 由唯一执行计划构建器合入执行计划（ExecutionPlan），任务提交后不得改图；
- live-state-sensitive planning、`amount="all"` 与任务物料准入（TaskMaterialAdmission）的时序必须另开决策。

## 9. 候选模块边界

以下是目标设计（Target Design），不是已实现文件树：

- 包管理模块（Package Manager Module）：现有包来源（Package Source）到 PackageCatalog 的唯一发现入口，增加定义种类而不复制扫描器；
- 候选工作单元定义模块（WorkCell Definition Module）：以失败关闭 AST allowlist 拒绝动态控制流、任意调用/I/O 和未知节点，拥有 lowering、link、recursive closure、public contract、canonical codec、source map 和投影；
- 位姿/变换模块（Pose/Transform Module）：统一拥有坐标单位、旋转顺序、数值规范化、父子矩阵组合、
  物理 `pose` 编解码和 `layout_plane` 投影约束，设备作者句柄与前端 Adapter 不重复实现坐标换算；
- 库位投影模块（Site Projection Module）：统一校验 `config.sites[]` 的稳定 key、几何、允许类型和顺序，并投影为 Backend
  库位（Site）；不接受库位占用（SiteOccupancy）写入；
- 候选启用解析器（Activation Resolver）：通过唯一 `prepare_activation(...)` 接口把定义、可选请求、实例部署和 Secret Provider 降低为候选启用图与脱敏快照；
- 动作发布模块（Action Publication Module）：复用既有动作（Action）与组合工作流调用（CompositeWorkflowInvocation）合同；
- 执行计划构建器（ExecutionPlan Builder）：继续由调度器（Scheduler）拥有唯一运行时 lowering；
- 注册表适配器（Registry Adapter）：只从已发布定义生成候选复合设备投影（Composite Device Projection）；
- 前端适配器（FE Adapter）：消费规范 DTO，不解析 Python、不计算 closure/UUID、不执行 planner。

编译阶段保持：Source discovery → Definition compilation → Definition linking → Publication → Activation
→ Invocation specialization → Plan validation/freeze。发布和启用的每个阶段都必须零部分写入。

## 10. 身份、版本与失败语义

- 定义机器身份为 `<class_namespace>.<@workcell.id>` 的 PackageCatalog fqid；装饰器 `version` 是作者语义元数据，发布权威另分配单调正整数 revision；
- 精确发布身份为 `{definition_fqid, revision, content_digest}`；内容摘要覆盖规范语义图及固定依赖/资产闭包，公共合同摘要只覆盖公开表面；
- `id=` 是定义局部稳定 `member_id`，变量名只属于 source map；运行 UUID 从外层实例 namespace 与成员身份确定性派生；
- 库位（Site）key、公共端口、导出 alias、公开参数名和动作名都是兼容面；
- 改 `instance_id` 创建新实例；改其他实例部署或启动值为同一实例创建新候选启用快照（Activation Snapshot），不产生新定义 revision；
- 修改定义或内层依赖产生新 definition revision，不能热切换既有任务；
- 重启只复用完全相同的快照 digest；任一输入或 Secret 版本变化都要求显式重新启用；
- 执行未知、部分物理成功或取消不得触发盲目物理重放（Blind Physical Replay）；
- 候选启用快照（Activation Snapshot）不是第二份工作流快照或执行计划（ExecutionPlan）。

## 11. 典型压测场景

1. Python 局部变量重命名：`member_id` 与内容语义不变，source map 可以变化；
2. Python → JSON → Python：注释可规范化，但图 digest、成员、连接、库位（Site）和位姿不变；
3. 零公开参数：只用 `workcell.py` 启动，不创建空 params 记录，但生成并持久化快照；
4. 全部参数有默认值：不提供参数输入，快照记录规范化默认值及来源；
5. Phase 0 提供外部参数输入：在 driver 构造前明确失败，不能静默忽略；
6. `-g/--graph` 输入未知或无后缀：在读取为任一图格式前失败，不能内容猜测或回退为 GraphML；
7. 完整 v1 多个外部参数来源同时出现：失败且不按来源优先级隐式合并；
8. 私有 PLC 地址：外部深路径覆盖失败；需要现场变化时必须提升为公开 `InitParam`；
9. Secret Provider 不可用：在 driver 构造前失败，错误和快照不泄漏明文；
10. 内层 definition 升级：不改变外层已发布 revision，必须显式 re-link/re-publish；
11. 两个工作流任务（WorkflowTask）并发调用同一实例：内部作业可以交错；每个可派发作业必须原子取得
    覆盖设备、物料（Material）与源/目标库位（Site）的完整作业执行占用（JobExecutionClaim）。定义中
    存在未建模共用物理风险时，发布或并发安全校验失败关闭；
12. 内部取料后断电：相关物料、库位（Site）、作业执行占用（JobExecutionClaim）和栅栏保留不确定性并进入核对；
13. 遗留 JSON 同时含 `position`、`position3d` 和 `rotation`：等价重复告警，冲突坐标失败并给出精确路径；
14. 在 `layout_plane="XY"` 的 2D 编辑器拖动成员：直接修改 `pose.position.x/y`，保持 Z 不变；发布产生新
    definition revision，但既有候选启用快照（Activation Snapshot）和工作流任务（WorkflowTask）不变；
15. 父节点绕 Z 轴旋转后包含子节点：世界位姿由矩阵递归组合，不能用位置和欧拉角逐分量相加；
16. 遗留 JSON 含动态 `data` 或 `occupied_by`：测试 seed 与运行时权威事实分别迁移，无法分类的非空
    `data` 无损保留但阻止发布/启用；v1 不产生可执行物料预置候选且重启不得覆盖库存权威。

## 12. G1 永久兼容与跨仓验收合同

G1-01 与 G1-02 的 B 选择按 B′ 冻结：永久保留输入格式和原始信息，不永久保留两套语义。兼容适配器（Adapter）
必须无损保存旧节点对象、`uuid`、非空 `data` 和未知字段，并输出分类报告；只有已知且通过校验的字段
进入规范语义。显式、可校验的旧 `uuid` 可用于实例接管，但不得污染 `content_digest`；未知字段只可
round-trip，不可下发驱动、覆盖库存权威（Inventory Authority）或成为候选启用快照（Activation Snapshot）
的运行参数。无法分类的非空 `data` 即使已无损保存，也必须阻止发布与启用；已知字段之间冲突仍失败关闭。

跨格式固定点同时检查两条摘要：`content_digest` 证明 JSON → 规范图 → Python → 规范图的定义语义一致；
`legacy_payload_digest` 证明兼容保留载荷没有丢失。workspace、clean wheel 和缓存 archive 的语义摘要
必须一致；源码格式、source map 和兼容保留载荷不进入 `content_digest`。

验收使用两个固定夹具：最小本地仿真夹具，以及固定来源 commit/原始摘要的 SZLab
`deployment/graphs/szlab-local-debug.json` 真实复杂度夹具。每个夹具保存作者 Python、规范 JSON、兼容
保留 sidecar、迁移报告和预期双摘要。默认测试不得连接真实硬件。

跨仓测试必须通过真实编译器、SQLite、SSE、设备注册表（Device Registry）和本地仿真器，覆盖
`.py/.json/.graphml` 的 `-g/--graph` 启动、快照复用、敏感配置（Secret）、前端折叠/展开，以及工作流
支持动作（Workflow-backed Action）的成功、取消、容量交错、部分物理成功、断电和执行未知；不得用
路由 mock 替代集成证据，不得对整个动作调用做盲目物理重放（Blind Physical Replay）。

OS、前端和 SZLab 各自拥有仓库本地交付子问题，Core #187 只在所有子问题提供精确 commit、测试命令、
结果和对应文档 revision 后执行总验收。

## 13. 非目标

- 不让前端执行或静态解释 Python；
- 不让运行时 import/exec 作者源码作为生产发现合同；
- 不让 JSON/GraphML 永久兼容形成第二套编译、设备实例化或运行权威；
- 不把候选工作单元（WorkCell）当成物料（Material）或第二套库存（Inventory）；
- 不让设备注册表（Device Registry）成为候选装配拓扑（Assembly Topology）的写权威；
- 不自动公开全部内部成员或内部动作（Action）；
- 不根据工作流（Workflow）节点数量自动发布动作（Action）；
- 不在 v1 支持 `optional`、`variant`、动态拓扑或运行时改图；
- 不在 v1 生成或执行真实物料预置命令，也不为其增加 `command_id`、请求摘要、整批事务或回执存储；
- 不在 driver、ROS callback 或前端中运行第二个 planner/调度器（Scheduler）；
- 不在本功能重定义动作合同、工作流组合、物料权威或调度权威。

## 14. 子议题与文档所有权

| 子议题 | 所有范围 |
| --- | --- |
| [#182](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/182) | D1：定义身份、AST、规范图和双向创作 |
| [#183](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/183) | D2：装配拓扑、物理位姿与物料边界 |
| [#184](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/184) | D3：启用参数、启动解析与敏感配置（Secret） |
| [#185](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/185) | D4：嵌套组合、公开边界和设备注册表（Device Registry）投影 |
| [#186](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/186) | D5：工作流支持动作（Workflow-backed Action）、静态降低和并发 |
| [#187](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/187) | G1：遗留图迁移与跨仓验收 |

父地图 [#181](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181) 只维护 Outcome、已接受决策、
Frontier、Blocked、Fog 和跨票冲突。详细决策写入对应子议题，并同步修订本文相关章节。

## 15. 验收门

- [ ] AST discovery 不 import/exec 作者源码、device driver 或 resource factory；
- [ ] Python 与规范定义图达到固定点，workspace/clean wheel digest 一致；
- [ ] 稳定成员、包含、连接、库位（Site）、资产、`layout_plane` 和物理 `pose` 通过 round-trip；2D/3D
  编辑不存在第二套节点坐标；
- [ ] 候选工作单元（WorkCell）可递归组合，多实例身份稳定，循环失败关闭；
- [ ] 私有成员默认不可寻址，export/re-export 只按稳定公共身份生效；
- [ ] 零参数、全默认、覆盖、必填缺失、Secret Provider 失败均在硬件副作用前得到确定结果；
- [ ] 零覆盖不创建空 params 记录，但始终生成持久、脱敏候选启用快照（Activation Snapshot）；
- [ ] 一次启用最多接受一个外部覆盖对象；多个来源同时出现时在硬件副作用前失败；
- [ ] Phase 0 通过 `-g/--graph` 启动 Python 定义，外部参数输入明确失败且仍持久化默认值快照；
- [ ] `-g/--graph` 只接受 `.py`、`.json`、`.graphml`；未知或无后缀失败，`.py` 不 import/exec 且只有一个顶层 `@workcell` 根定义；
- [ ] `.json`/`.graphml` 无损保留旧字段但与 `.py` 共用单一编译、发布和启用链；未知兼容字段无运行权威；
- [ ] 无法分类的非空 `data` 在无损保留后仍阻止发布/启用，直到迁移矩阵完成分类；
- [ ] 语义 `content_digest` 与 `legacy_payload_digest` 分别达到固定点，workspace/clean wheel/cache 语义一致；
- [ ] v1 可展示和校验物料设计预期，但候选工作单元（WorkCell）启用、重启和定义升级均不创建/移动真实物料（Material）或写库位占用（SiteOccupancy）；
- [ ] 已发布定义进入设备注册表（Device Registry）/Palette，Draft/Candidate 不进入；
- [ ] 工作流支持动作（Workflow-backed Action）通过显式导出产生，使用 `node_type="workflow"` 与
  `x-unilabos-workflow-contract` 保留工作流（Workflow）身份，并静态进入唯一执行计划（ExecutionPlan）；
- [ ] 两个调用的内部作业可以交错，但每个作业必须取得完整作业执行占用（JobExecutionClaim）；v1 不存在
  整次调用串行、容量 N、`max_concurrency` 或调用期许可的暗含保证；
- [ ] 断电、部分物理成功、取消和执行未知不触发盲目物理重放（Blind Physical Replay）；
- [ ] 遗留 JSON 迁移不覆盖真实物料（Material）、库位占用（SiteOccupancy）、遥测、预留或占用事实；
- [ ] 最小仿真与真实 SZLab 夹具通过 OS/前端/设备链路跨仓验收；
- [ ] GitHub 决策、Feishu 协议文档、仓库实现和测试证据在接受时一致。

## 16. 资料来源

- [父地图 #181](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181)
- [领域设备包 PackageCatalog 与 Workspace 自动发现 #147](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/147)
- [动作（Action）有类型合同与结果提交 #135](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/135)
- [子工作流组合与边界 #136](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/136)
- [执行计划（ExecutionPlan）与调度生命周期 #164](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/164)
- [工作流（Workflow）投影与组合身份 #178](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/178)
- [Feishu OKF 工作流协议 revision 9](https://dptechnology.feishu.cn/wiki/Qa1EwFWB1iqx4OkfNXhcvTh3nPf)
- #181 正文编辑历史中的拆票前完整设计，以及 #181 的 Grill 01–04 评论。

## Agent report

```yaml
agent_report:
  stage: protocol-definition
  reporter: Codex
  execution_mode: agent
  agent_product: Codex
  agent_name: WorkCell independent design document alignment
  model: GPT-5
  input_refs:
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/182
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/183
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/184
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/185
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/186
    - https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/187
    - https://dptechnology.feishu.cn/wiki/Qa1EwFWB1iqx4OkfNXhcvTh3nPf
  result: g1-protocol-frozen-design
  human_reviewer: 昌珺涵
```
