# 候选工作单元（WorkCell）组合定义、启动与分层动作设计

> 状态：协议定义中（Protocol Definition）  
> 合同草案版本：`workcell-composition-draft-20260804-d3-05`  
> 父地图：[Core #181](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/181)  
> 历史来源：#181 拆票前最后一份完整正文（2026-08-04 17:18，Asia/Shanghai）  
> 对齐范围：已纳入 D1–D3 的已接受决策，截止 D3-05；D4、D5 与迁移细节仍是候选设计。

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
              │ optional parameter override + secret reference
              ▼
候选启用快照（Activation Snapshot）
              │ lowering
              ▼
候选启用图（Activation Graph）与设备注册表（Device Registry）投影
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
| D2-01 | 已接受方向 | 物理位置和旋转进入 v1；候选局部位姿（LocalPose）与 `ui_layout` 分离。 |
| D2-02 | 已接受方向 | 内部相对位姿归定义；候选工作单元实例（WorkCell Instance）的根世界位姿归候选启用图（Activation Graph）。 |
| D3-01 | 已接受 | `workcell.py` 是必需作者制品；参数输入是按需存在的覆盖层；每次启用都生成候选启用快照（Activation Snapshot）。 |
| D3-02 | 已接受 | 选择 A：零覆盖不创建空 params 文件或持久记录；“无覆盖”以参数输入缺席表示，候选启用快照（Activation Snapshot）仍须持久化。 |
| D3-03 | 已接受 | 选择 A：一次启用最多接受一个外部覆盖对象；多个外部来源同时出现时失败，不做隐式叠加或优先级合并。 |
| D3-04 | 已接受 | 选择 A：Phase 0 仅实现 Python-only 零外部参数路径；完整 v1 保留 D3-03 的单一外部来源合同。 |
| D3-05 | 已接受 | 复用 `-g/--graph` 作为唯一启动定义来源参数，不新增 `--workcell`。 |
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
一次实例化。它拥有稳定实例身份、根世界位姿、外部连接、机器/Edge 放置和已解析启动值。
定义 revision 更新不得静默改变既有实例或已创建工作流任务（WorkflowTask）。

### 3.3 三种图必须分离

| 图 | 权威 | 包含 | 不包含 |
| --- | --- | --- | --- |
| 候选装配拓扑（Assembly Topology） | 已发布候选工作单元定义（WorkCell Definition） | 成员、包含、库位（Site）绑定、内部连接、相对位姿、公共合同 | 真实实例、凭证、物料（Material）当前状态、任务状态 |
| 候选启用图（Activation Graph） | 部署/启用权威 | 实例身份、根世界位姿、外部连接、机器放置、允许的参数覆盖 | 可变定义、工作流任务（WorkflowTask）有向无环图（DAG） |
| 执行计划（ExecutionPlan） | 工作流任务（WorkflowTask）/调度器（Scheduler）合同 | 某次任务的冻结拓扑、绑定、执行要求和占用意图（ClaimIntent） | 实时可用性、预留/占用事实和物理结果 |

### 3.4 物料与运行事实边界

资源模板（ResourceTemplate）、允许出现的固定资源结构和库位（Site）可以进入定义。真实物料
（Material）UUID、条码、当前数量、库存分配和库位占用（SiteOccupancy）归库存权威
（Inventory Authority），不得由 `workcell.py`、params 输入或每次重启覆盖。

任务物料预留（TaskMaterialReservation）、作业执行占用（JobExecutionClaim）、设备遥测投影
（DeviceTelemetryProjection）和物理结算（PhysicalSettlement）继续留在各自运行权威中。
首次预置真实物料若确有必要，必须成为显式、一次性、幂等且有持久回执的 bootstrap/provision
操作；该合同仍由 [#183](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/183) 继续确认。

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
    auto_connect: Annotated[
        bool,
        InitParam(title="Start device connections"),
    ] = True,
    pump_timeout_s: Annotated[
        float,
        InitParam(title="Pump timeout", ge=0.1, le=30.0, unit="s"),
    ] = 5.0,
) -> WorkCell:
    cell = WorkCell()

    plc_1 = plc(
        id="plc",
        url="opc.tcp://127.0.0.1:4840",
        auto_connect=auto_connect,
        csv_path="assets/szlab_plc_0730.csv",
    )
    robot = mixer_robot(
        id="robot",
        plc_device=plc_1,
        auto_connect=auto_connect,
    )
    pump = pump_station(
        id="pump",
        plc_device=plc_1,
        timeout_s=pump_timeout_s,
    )

    cell.assign_child_resource(
        plc_1,
        local_pose=Pose(
            position_mm=(0.0, 0.0, 0.0),
            rotation_deg_xyz=(0.0, 0.0, 0.0),
        ),
    )
    cell.assign_child_resource(
        robot,
        local_pose=Pose(
            position_mm=(1200.0, 350.0, 0.0),
            rotation_deg_xyz=(0.0, 0.0, 90.0),
        ),
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

- 同一草稿同一时刻只有一种可写模式；切换前必须处理 dirty 状态；
- 不做两份文本的自动增量合并或强制覆盖；
- 语义往返不承诺注释、空行、局部变量风格和 import 排列的字节级无损；
- 稳定 `member_id`、引用、嵌套 definition digest 和 source map 不能靠变量名或数组顺序猜测；
- AI 可以修改 Python，也可以提交有类型图编辑/JSON Patch，但必须经过同一 compiler/generator/validator；
- 无效草稿可以保存和诊断，但不能发布、启用或替换最后一个有效 revision。

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

发布必须原子失败关闭。Draft/Candidate 不进入设备注册表（Device Registry）；Published 才能产生
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

候选设备初始化合同（Device Init Contract）描述叶子设备构造/连接前可接受字段的类型、默认值、
范围、单位和敏感性。候选工作单元初始化合同（WorkCell Init Contract）只由 `@workcell` 函数签名
中的公开 `InitParam` 派生。

- 固定、非敏感且对该定义所有启用一致的站内设备值可以写在 Python 定义中；
- 随物理安装变化、需要外部选择或属于敏感配置（Secret）的值必须提升为公开 `InitParam`；
- 外部不能用 `members.plc.config.*` 或 `devices.plc.url` 一类深路径覆盖私有字段；
- 外层候选工作单元（WorkCell）只能绑定内层的公开参数，不能越过内层合同；
- 一个公开参数可以 fan-out 到多个兼容目标；有效约束是所有目标合同的安全交集；
- 未使用参数、未知目标、重复来源、空约束交集和类型/单位不兼容必须在发布或启用前失败。

### 6.3 参数来源

已接受的 D3-03=A 合同是“定义默认值 + 零或一个外部覆盖对象”。一次启用可以完全没有外部来源；
存在覆盖时，只能从 params 文档、持久部署记录或 UI/API 提交等入口中选择一个规范化对象。多个来源
同时出现必须在硬件副作用前失败，不做隐式 merge，也不存在 CLI、文件和记录之间的优先级。候选启用
快照（Activation Snapshot）必须记录每个最终值来自定义固定值、默认值还是该唯一覆盖对象。

D3-04=A 把 Phase 0 限定为 Python-only 零外部参数子集：只能启用零公开参数或全部参数已有默认值且
不依赖敏感配置（Secret）引用的定义。任何外部参数输入都必须明确报“尚未支持”，不能静默忽略；
系统仍须完成合同校验、默认值解析并持久化脱敏候选启用快照（Activation Snapshot）。

敏感配置（Secret）只能以 reference 流转。定义、PackageCatalog、设备注册表（Device Registry）、
source map、日志、诊断和候选启用快照（Activation Snapshot）不得包含明文。Secret Provider 应在
结构、Schema、绑定和定义闭包全部验证成功后、首个驱动构造前解析 reference；错误必须脱敏。

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

候选规则：

- `-g` 与 `--graph` 是同一参数的短/长形式，不能再增加并行启动来源参数；
- 文件必须位于显式 workspace 内并经过 containment/symlink 检查；
- Python、遗留 JSON/GraphML 与未来目录引用的精确识别规则继续由 [#184](https://github.com/Uni-Lab-OS/Uni-Lab-Core/issues/184) Grill；
- Phase 0 出现任何外部参数输入时必须明确失败；
- `--config` 继续只配置 Uni-Lab OS 进程，不进入候选工作单元初始化合同；
- params 输入是 closed object，未知字段失败；命令行不得携带敏感配置（Secret）明文；
- `--check_mode` 在首个 driver import、构造和硬件连接前完成全部验证并退出。

### 6.5 启动顺序

```text
解析 OS 进程配置
  -> 编译显式 PackageCatalog
  -> 解析 `-g/--graph` 唯一启动定义来源
  -> link exact definition closure
  -> 解析可选参数覆盖与默认值
  -> 校验 internal init bindings
  -> 解析 secret references
  -> 冻结候选启用快照（Activation Snapshot）
  -> 降低为候选启用图（Activation Graph）
  -> 显式一次性 bootstrap（若存在且获授权）
  -> import/initialize selected drivers
```

任一 source、definition、parameter、binding 或 secret 失败都必须发生在硬件副作用前；失败启动不能
留下部分 driver、部分设备注册表（Device Registry）实例或部分物料 bootstrap。

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
- WorkCell Definition Module：拥有 AST lowering、link、recursive closure、public contract、canonical codec、source map 和投影；
- 候选启用解析器（activation resolver）：把定义、可选覆盖、实例身份和 Secret Provider 降低为候选启用图与脱敏快照；
- Action Publication Module：复用既有动作（Action）与组合工作流调用（CompositeWorkflowInvocation）合同；
- ExecutionPlan Builder：继续由调度器（Scheduler）拥有唯一运行时 lowering；
- Registry Adapter：只从已发布定义生成候选复合设备投影（Composite Device Projection）；
- FE Adapter：消费规范 DTO，不解析 Python、不计算 closure/UUID、不执行 planner。

编译阶段保持：Source discovery → Definition compilation → Definition linking → Publication → Activation
→ Invocation specialization → Plan validation/freeze。发布和启用的每个阶段都必须零部分写入。

## 10. 身份、版本与失败语义

- 定义机器身份使用 PackageCatalog fqid；显示名可独立修改；
- 已发布 revision/content digest 不原地改写，外层固定 exact resolved digest；
- 内部成员使用定义局部稳定身份，运行 UUID 从外层实例 namespace 与成员身份确定性派生；
- 库位（Site）key、公共端口、导出 alias、公开参数名和动作名都是兼容面；
- 修改启动值产生新候选启用快照（Activation Snapshot），不产生新定义 revision；
- 修改定义或内层依赖产生新 definition revision，不能热切换既有任务；
- 执行未知、部分物理成功或取消不得触发盲目物理重放（Blind Physical Replay）；
- 候选启用快照（Activation Snapshot）不是第二份工作流快照或执行计划（ExecutionPlan）。

## 11. 典型压测场景

1. Python 局部变量重命名：稳定成员身份不变，否则要求显式迁移；
2. Python → JSON → Python：注释可规范化，但图 digest、成员、连接、库位（Site）和位姿不变；
3. 零公开参数：只用 `workcell.py` 启动，不创建空 params 记录，但生成并持久化快照；
4. 全部参数有默认值：不提供参数输入，快照记录规范化默认值及来源；
5. Phase 0 提供外部参数输入：在 driver 构造前明确失败，不能静默忽略；
6. 完整 v1 多个外部参数来源同时出现：失败且不按来源优先级隐式合并；
7. 私有 PLC 地址：外部深路径覆盖失败；需要现场变化时必须提升为公开 `InitParam`；
8. Secret Provider 不可用：在 driver 构造前失败，错误和快照不泄漏明文；
9. 内层 definition 升级：不改变外层已发布 revision，必须显式 re-link/re-publish；
10. 两个工作流任务（WorkflowTask）并发调用同一实例：在 D5 容量合同冻结前失败关闭或使用明确单容量策略；
11. 内部取料后断电：相关物料、库位（Site）、作业执行占用（JobExecutionClaim）和栅栏保留不确定性并进入核对；
12. 遗留 JSON 含动态 `data`：测试 seed、一次性 bootstrap 与运行时权威事实分别迁移，重启不得覆盖库存权威。

## 12. 非目标

- 不让前端执行或静态解释 Python；
- 不让运行时 import/exec 作者源码作为生产发现合同；
- 不把候选工作单元（WorkCell）当成物料（Material）或第二套库存（Inventory）；
- 不让设备注册表（Device Registry）成为候选装配拓扑（Assembly Topology）的写权威；
- 不自动公开全部内部成员或内部动作（Action）；
- 不根据工作流（Workflow）节点数量自动发布动作（Action）；
- 不在 v1 支持 `optional`、`variant`、动态拓扑或运行时改图；
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
