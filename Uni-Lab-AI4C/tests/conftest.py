from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OS_ROOT = Path(
    os.environ.get("UNILAB_OS_ROOT", REPO_ROOT.parent / "Uni-Lab-OS")
).resolve()

for path in (OS_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """返回 AI4C 单分发包的仓库根目录。"""

    return REPO_ROOT


@pytest.fixture(scope="session")
def profile(repo_root: Path):
    """加载包内默认设备配置（Profile），验证其不依赖外部工作区。"""

    import yaml

    return yaml.safe_load(
        (
            repo_root
            / "ai4c_robot"
            / "profiles"
            / "default"
            / "package.yaml"
        ).read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def authoring_catalog(repo_root: Path, tmp_path_factory):
    """从 AI4C 设备注册表（Registry）生成现行工作流创作目录。

    参数：``repo_root`` 是被测分发根目录，``tmp_path_factory`` 提供隔离数据库。
    返回：本次测试会话内不可变的工作流创作目录（Authoring Catalog）快照。
    异常：设备动作合同（Action Contract）不完整时关闭式失败。
    安全：只扫描本地源码并写入 pytest 临时目录。
    """

    from unilabos.registry.registry import Registry
    from unilabos.registry.template_projection import RegistryTemplateProjection
    from unilabos.workflow.store import WorkflowStore

    registry = Registry()
    registry._load_config_cache = lambda: {}
    registry._save_config_cache = lambda _cache: None
    registry._run_ast_scan(
        devices_dirs=[repo_root / "ai4c_robot"],
        external_only=True,
    )
    projection = RegistryTemplateProjection(
        WorkflowStore(tmp_path_factory.mktemp("authoring") / "workflow.sqlite3"),
        authority_id="ai4c-test",
        resource_template_identity_resolver=lambda identity: str(
            uuid5(NAMESPACE_URL, f"ai4c:{identity}")
        ),
    )
    try:
        yield projection.refresh(registry)
    finally:
        projection.close()
