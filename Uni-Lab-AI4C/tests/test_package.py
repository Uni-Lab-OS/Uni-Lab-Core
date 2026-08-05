from __future__ import annotations

import json
from pathlib import Path

from unilabos.registry.registry import Registry
from unilabos.workflow.authoring_engine import WorkflowAuthoringEngine

WORKFLOW_UUID = "315a8273-e38c-5add-a655-bb7228fe077f"


def _scan(root: Path) -> tuple[set[str], set[str]]:
    """扫描指定包根目录下的设备与资源定义。

    参数：``root`` 是 AI4C Python 包目录。返回：设备和资源业务名集合。
    异常：注册表（Registry）源码无效时向上传播扫描异常。
    安全：关闭缓存读写，只执行本地 AST（抽象语法树）扫描。
    """

    registry = Registry()
    registry._load_config_cache = lambda: {}
    registry._save_config_cache = lambda _cache: None
    registry._run_ast_scan(devices_dirs=[root], external_only=True)
    devices = {
        key
        for key, value in registry.device_type_registry.items()
        if Path(str(value.get("file_path") or "/")).resolve().is_relative_to(root.resolve())
    }
    resources = {
        key
        for key, value in registry.resource_type_registry.items()
        if Path(str(value.get("file_path") or "/")).resolve().is_relative_to(root.resolve())
    }
    return devices, resources


def _applied_graph() -> dict:
    """构造首次编译使用的空工作流图（Workflow Graph）。"""

    return {
        "workflow": {
            "uuid": WORKFLOW_UUID,
            "name": "AI4C 孔板搬运联调",
            "tags": [],
            "description": "",
            "meta_data": {},
            "revision": 1,
        },
        "nodes": [],
        "edges": [],
        "node_templates": [],
        "handle_templates": [],
    }


def test_repository_is_one_distribution_with_one_import_package(repo_root: Path) -> None:
    assert not (repo_root / "packages").exists()
    assert (repo_root / "pyproject.toml").is_file()
    assert (repo_root / "ai4c_robot" / "__init__.py").is_file()
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "ai4c-robot"' in pyproject
    assert 'include = ["ai4c_robot*"]' in pyproject
    assert "unilabos.model_bundles" not in pyproject


def test_registry_discovers_both_ai4c_devices(repo_root: Path) -> None:
    devices, resources = _scan(repo_root / "ai4c_robot")
    assert devices == {"AI4C_plc", "AI4C_robot_arm"}
    assert resources == set()


def test_profile_and_workflow_are_self_contained(
    repo_root: Path,
    profile,
    authoring_catalog,
) -> None:
    """配置与工作流源码（Workflow Source）应由当前公开编译器独立编译。"""

    profile_root = repo_root / "ai4c_robot" / "profiles" / "default"
    assert profile["profile_id"] == "ai4c_robot"
    assert (profile_root / "device.yaml").is_file()
    authoring_catalog.require_action(
        "ai4c_robot.devices.ai4c_robot_arm.device:AI4CRobotArmDevice",
        "pick_well_plate_from_loading_rack",
    )

    source = repo_root / "ai4c_robot" / "workflows" / "ai4c_canvas_workflow.py"
    result = WorkflowAuthoringEngine(catalog=authoring_catalog).compile(
        workflow_uuid=WORKFLOW_UUID,
        workflow_revision=1,
        python_source=source.read_text(encoding="utf-8"),
        source_uri="package://ai4c_robot/workflows/ai4c_canvas_workflow.py",
        applied_graph=_applied_graph(),
    )
    assert result.valid and result.graph is not None, result.diagnostics
    assert result.graph["workflow"]["uuid"] == WORKFLOW_UUID
    assert len(result.graph["nodes"]) == 8
    assert len(result.graph["edges"]) == 7


def test_debug_graph_is_ai4c_only_and_safe_by_default(repo_root: Path) -> None:
    graph = json.loads(
        (repo_root / "deployment" / "graphs" / "ai4c-local-debug.json").read_text(
            encoding="utf-8"
        )
    )
    assert {node["class"] for node in graph["nodes"]} == {
        "AI4C_plc",
        "AI4C_robot_arm",
    }
    plc = next(node for node in graph["nodes"] if node["class"] == "AI4C_plc")
    assert plc["config"]["auto_connect"] is False


def test_migration_manifest_points_to_local_workflow(repo_root: Path) -> None:
    import yaml

    migration_root = repo_root / "migration"
    manifest = yaml.safe_load(
        (migration_root / "manifest.yaml").read_text(encoding="utf-8")
    )
    assert len(manifest["presets"]) == 1
    entry = manifest["presets"][0]
    assert (migration_root / entry["legacy_preset"]).is_file()
    assert (migration_root / entry["legacy_runtime"]).is_file()
    assert (migration_root / entry["python_source"]).resolve().is_file()
