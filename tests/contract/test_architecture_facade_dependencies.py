from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "src" / "mtp6coopnw" / "api"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_ui_facade_depends_on_application_contracts_not_concrete_core() -> None:
    imports = _imports(API / "ui.py")
    assert "mtp6coopnw.application" in imports
    assert "mtp6coopnw.core" not in imports
    assert "mtp6coopnw.operations" not in imports
    assert "mtp6coopnw.policy" not in imports


def test_control_facade_uses_application_engine_protocols() -> None:
    imports = _imports(API / "control.py")
    assert "mtp6coopnw.application" in imports
    assert "mtp6coopnw.policy" in imports  # DTO/value types only
    source = (API / "control.py").read_text(encoding="utf-8")
    assert "policy_engine: PolicyEvaluationService" in source
    assert "planner: PlanningService" in source
    assert "operation_engine: OperationService" in source


def test_command_facade_uses_command_execution_service_protocol() -> None:
    source = (API / "commands.py").read_text(encoding="utf-8")
    assert "executor: CommandExecutionService" in source
    assert "EngineCommandExecutor" not in source
