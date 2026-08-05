# Uni-Lab AI4C Robot

AI4C PLC 与机械臂领域设备包。仓库根同时是 Python distribution root 和目标
Uni-Lab-OS workspace root；根目录只构建一个 distribution `ai4c-robot`，唯一常规顶层
import package 是 `ai4c_robot`。

## 目录合同

```text
Uni-Lab-AI4C/
├── pyproject.toml
├── ai4c_robot/
│   ├── devices/
│   │   ├── ai4c_plc/
│   │   └── ai4c_robot_arm/
│   ├── workflows/
│   ├── profiles/default/
│   └── common/
├── deployment/
├── tests/
├── docs/
├── scripts/
└── migration/
```

设备和工作流由装饰器定义，不使用额外 package manifest 或模型发现 entry point。后续添加
设备模型时，资产放在 `ai4c_robot/devices/<device_id>/models/`，并通过同一设备的
`@device(model={...})` 绑定。

## 安装、检查和构建

```bash
python -m pip install -e . --no-deps
./scripts/check-package.sh
./scripts/build-package.sh
python -m pytest
```

`check-package.sh` 目前使用 OS 的兼容 `--devices` 入口；OS 实现 Issue #147 的
PackageCatalogCompiler 后，再切换为 `unilab --workspace .`。

本地离线 authoring bridge：

```bash
./scripts/start-authoring-bridge.sh
```

本地图以 `auto_connect: false` 创建 PLC，只有受控真机配置才能启用 OPC UA 连接。工作流 E2E
证据见 [`docs/WORKFLOW_E2E.md`](docs/WORKFLOW_E2E.md)。
