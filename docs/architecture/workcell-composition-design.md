# 候选工作单元（WorkCell）组合定义、启动与分层动作设计

> 状态：协议定义中（Protocol Definition）
> 合同草案版本：`workcell-composition-draft-20260805-d2-provisioning-deferred`
> 父地图：[Core #181](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181)
> 历史来源：#181 拆票前最后一份完整正文（2026-08-04 17:18，Asia/Shanghai）
> 对齐范围：已纳入 D1–D3 的已接受决策；D1 与 D3 已全部冻结；D2-04 的动态物料边界已经冻结，D2-06 的真实物料预置执行链已明确推迟到 v2+，D2 其余 5 项及 D4、D5、迁移细节仍是候选设计。

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
| D2-01 | 已接受方向 | 物理位置和旋转进入 v1；候选局部位姿（LocalPose）与 `ui_layout` 分离。 |
| D2-02 | 已接受方向 | 内部相对位姿归定义；候选工作单元实例（WorkCell Instance）的根世界位姿归候选启用图（Activation Graph）。 |
| D2-04 | 已接受 | 选择 A：定义拥有固定结构、物料设计约束和只读投影；库存权威（Inventory Authority）独占真实物料（Material）与库位占用（SiteOccupancy）动态事实。 |
| D2-06 | 已决策延期 | v1 只描述和校验物料设计预期，不生成或执行真实物料预置命令；`command_id`、请求摘要、整批事务与持久回执的执行链推迟到 v2+。 |
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
| D4 | 待确认 | 嵌套公开边界、可查看性、可寻址性和设备注册表（Device Registry）投影细节。 |
| D5 | 部分接受 | v1 使用动作形态的组合工作流调用（CompositeWorkflowInvocation），在任务创建前静态展开；并发容量仍待确认。 |
| G1 | 待确认 | 遗留启动 JSON、trusted-exec 原型和真实 SZLab 夹具的迁移与退役门。 |

## 3. 设计边界与权威

### 3.1 候选工作单元定义（WorkCell Definition）

候选工作单元定义（WorkCell Definition）拥有：

- 稳定定义身份、revision、content digest 和公共合同 digest；
- 内部成员引用与稳定 `member_id`/alias；
- 候选定义包含关系（Definition Containment）；
- 库位（Site）绑定、内部连接和候选装配拓扑（Assembly Topology）；
- 内部成员相对候选局部位姿（LocalPose）；
- 公开端口、导出成员、公共动作（Action）和候选工作单元初始化合同（WorkCell Init Contract）；
- 随定义版本化、对所有启用一致且不敏感的私有固定配置和资产引用。

它不拥有真实在线状态、连接凭证明文、真实物料（Material）当前状态、库位占用
（SiteOccupancy）或工作流任务（WorkflowTask）状态。

### 3.2 候选工作单元实例（WorkCell Instance）

候选工作单元实例（WorkCell Instance）是某个候选启用图（Activation Graph）对精确已发布定义的
一次实例化。稳定 `instance_id`、根世界位姿、外部连接和 Edge/机器放置属于实例部署字段，不属于
公开 `InitParam`。Phase 0 使用 `instance_id = workcell.id`、单位根位姿、当前 Edge 和空外部连接；
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

`@workcell` 函数同时定义固定结构和公开启动合同。候选局部位姿（LocalPose）放在组合关系上，
不塞进设备工厂的初始化字段。

```python
from typing import Annotated

from unilabos.workcell import InitParam, Pose, WorkCell, workcell
from szlab_poly_studio.devices import mixer_robot, plc, pump_station


@workcell(
    id="szlab_poly_station",
    display_name="SZLab 聚合物工作站",
    version="1.0.0",
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
        plc_1, local_pose=Pose(position_mm=(0.0, 0.0, 0.0),
                               rotation_deg_xyz=(0.0, 0.0, 0.0)),
    )
    cell.assign_child_resource(
        robot, local_pose=Pose(position_mm=(1200.0, 350.0, 0.0),
                               rotation_deg_xyz=(0.0, 0.0, 90.0)),
    )
    cell.assign_child_resource(pump)
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
`public_contract_digest/init_param_schema/dependencies/assets`。`init_param_schema` 沿用 Backend
`{"config":{"properties":{...}}}` 形态；`dependencies[class]` 保存精确 `revision` 和
`content_digest`，不再为每个节点引入重复 `definition_ref`。

节点继续使用 `id/name/type/class/parent/children/pose/config/data`：

- `id` 是定义内稳定 `member_id`；`parent` 与 `children` 必须严格互逆；
- `children` 与 `config.sites` 的数组顺序具有语义，不在规范化时重排；
- `pose` 是物理位姿，`ui_layout` 只能存在独立展示 sidecar；
- `config` 只保存定义期固定 JSON 值；`data` 为现有结构兼容保留，但在定义中必须是 `{}`；
- 唯一必需的新节点字段是可选 `config_bindings`，其 `type` 仅允许 `member` 或
  `init_param`；候选启用解析器（Activation Resolver）将它降低为交给 OS/Backend 的普通 `config`；
- `config.sites[]` 继续使用 `label/content_type/position/size`，数组位置映射 Backend
  `sort_order`；禁止 `occupied_by/occupied_material_uuid`，因为它们是库位占用（SiteOccupancy）事实。

`links[*]` 保持 `id/source/target/type/port`，NetworkX 通过 `key="id"` 使用稳定边身份。
规范编码时 `nodes` 按 `id`、`links` 按 `id` 排序；`content_digest` 只排除
`graph.content_digest` 自身。source map 与 `ui_layout` 是绑定内容摘要的 sidecar，
诊断统一为 `code/path/source_span/message/hint`。

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
候选复合设备投影（Composite Device Projection）。设备注册表（Device Registry）只投影公共合同、
展示信息和活跃实例状态，不成为候选装配拓扑（Assembly Topology）的第二写权威。

一个已发布定义可以作为另一个候选工作单元定义（WorkCell Definition）的内部成员：

- 外层固定引用内层 exact revision/content digest，不复制一份可独立编辑的定义；
- 每层实例 alias 形成稳定 namespace，同一内层定义可以实例化多次；
- 发布前递归计算定义闭包并拒绝直接或间接循环；
- 外层只能连接内层公共端口、公共库位（Site）或显式导出成员；
- 内层升级不改写已发布外层，外层必须显式 re-link、preview、validate、publish。

候选可查看性（Inspectability）与候选可寻址性（Addressability）必须分离：授权维护者可以展开
私有成员用于诊断，但外层工作流（Workflow）仍不能直接寻址该成员。精确权限和 public/export/
re-export 合同由 [#185](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/185) 冻结。

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
- `.json` 进入遗留 JSON 解析器，`.graphml` 进入遗留 GraphML 解析器；
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

- 目录保留 `implementation.kind = workflow`，不冒充直接设备动作；
- 输入复用工作流输入合同（WorkflowInputContract）；
- 输出复用工作流结果记录（WorkflowResultRecord）；
- 物料边界复用物料占位符（ResourceSlot）；
- 父工作流（Workflow）中的调用是动作形态的组合工作流调用（CompositeWorkflowInvocation）；
- 在工作流任务（WorkflowTask）创建前静态展开到同一个执行计划（ExecutionPlan）；
- 不创建嵌套工作流任务（WorkflowTask），不复用遗留 `WorkstationBase.execute_workflow()`；
- 动作重试策略（ActionRetryPolicy）保持 `never`；
- 前端折叠只影响展示，不能删除内部工作流节点作业尝试（WorkflowNodeJobAttempt）、占用意图
  （ClaimIntent）、回执（Receipt）、source map 或物理结算（PhysicalSettlement）证据。

同一候选工作单元（WorkCell）的并发调用究竟允许内部节点交错、整次串行还是容量 N，仍由
[#186](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/186) 冻结。

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

- Package Manager Module：现有 Package Source 到 PackageCatalog 的唯一发现入口，增加定义种类而不复制扫描器；
- WorkCell Definition Module：以失败关闭 AST allowlist 拒绝动态控制流、任意调用/I/O 和未知节点，拥有 lowering、link、recursive closure、public contract、canonical codec、source map 和投影；
- 候选启用解析器（Activation Resolver）：通过唯一 `prepare_activation(...)` 接口把定义、可选请求、实例部署和 Secret Provider 降低为候选启用图与脱敏快照；
- Action Publication Module：复用既有动作（Action）与组合工作流调用（CompositeWorkflowInvocation）合同；
- ExecutionPlan Builder：继续由调度器（Scheduler）拥有唯一运行时 lowering；
- Registry Adapter：只从已发布定义生成候选复合设备投影（Composite Device Projection）；
- FE Adapter：消费规范 DTO，不解析 Python、不计算 closure/UUID、不执行 planner。

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
11. 两个工作流任务（WorkflowTask）并发调用同一实例：在 D5 容量合同冻结前失败关闭或使用明确单容量策略；
12. 内部取料后断电：相关物料、库位（Site）、作业执行占用（JobExecutionClaim）和栅栏保留不确定性并进入核对；
13. 遗留 JSON 含动态 `data`：测试 seed、推迟到 v2+ 的预置候选与运行时权威事实分别迁移，v1 不执行预置且重启不得覆盖库存权威。

## 12. 非目标

- 不让前端执行或静态解释 Python；
- 不让运行时 import/exec 作者源码作为生产发现合同；
- 不把候选工作单元（WorkCell）当成物料（Material）或第二套库存（Inventory）；
- 不让设备注册表（Device Registry）成为候选装配拓扑（Assembly Topology）的写权威；
- 不自动公开全部内部成员或内部动作（Action）；
- 不根据工作流（Workflow）节点数量自动发布动作（Action）；
- 不在 v1 支持 `optional`、`variant`、动态拓扑或运行时改图；
- 不在 v1 生成或执行真实物料预置命令，也不为其增加 `command_id`、请求摘要、整批事务或回执存储；
- 不在 driver、ROS callback 或前端中运行第二个 planner/调度器（Scheduler）；
- 不在本功能重定义动作合同、工作流组合、物料权威或调度权威。

## 13. 子议题与文档所有权

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

## 14. 验收门

- [ ] AST discovery 不 import/exec 作者源码、device driver 或 resource factory；
- [ ] Python 与规范定义图达到固定点，workspace/clean wheel digest 一致；
- [ ] 稳定成员、包含、连接、库位（Site）、资产、物理位姿和 `ui_layout` 分离通过 round-trip；
- [ ] 候选工作单元（WorkCell）可递归组合，多实例身份稳定，循环失败关闭；
- [ ] 私有成员默认不可寻址，export/re-export 只按稳定公共身份生效；
- [ ] 零参数、全默认、覆盖、必填缺失、Secret Provider 失败均在硬件副作用前得到确定结果；
- [ ] 零覆盖不创建空 params 记录，但始终生成持久、脱敏候选启用快照（Activation Snapshot）；
- [ ] 一次启用最多接受一个外部覆盖对象；多个来源同时出现时在硬件副作用前失败；
- [ ] Phase 0 通过 `-g/--graph` 启动 Python 定义，外部参数输入明确失败且仍持久化默认值快照；
- [ ] `-g/--graph` 只接受 `.py`、`.json`、`.graphml`；未知或无后缀失败，`.py` 不 import/exec 且只有一个顶层 `@workcell` 根定义；
- [ ] v1 可展示和校验物料设计预期，但候选工作单元（WorkCell）启用、重启和定义升级均不创建/移动真实物料（Material）或写库位占用（SiteOccupancy）；
- [ ] 已发布定义进入设备注册表（Device Registry）/Palette，Draft/Candidate 不进入；
- [ ] 工作流支持动作（Workflow-backed Action）保留 `implementation.kind`，静态进入唯一执行计划；
- [ ] 断电、部分物理成功、取消和执行未知不触发盲目物理重放（Blind Physical Replay）；
- [ ] 遗留 JSON 迁移不覆盖真实物料（Material）、库位占用（SiteOccupancy）、遥测、预留或占用事实；
- [ ] 最小仿真与真实 SZLab 夹具通过 OS/前端/设备链路跨仓验收；
- [ ] GitHub 决策、Feishu 协议文档、仓库实现和测试证据在接受时一致。

## 15. 资料来源

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
  result: aligned-design-document-draft
  human_reviewer: 昌珺涵
```
