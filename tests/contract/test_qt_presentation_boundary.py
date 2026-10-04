from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QT = ROOT / "src" / "mtp6coopnw" / "presentation" / "qt"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_qt_shell_does_not_import_engines_core_or_adapters() -> None:
    forbidden = (
        "mtp6coopnw.adapters",
        "mtp6coopnw.core",
        "mtp6coopnw.operations",
        "mtp6coopnw.policy",
        "mtp6coopnw.reconciliation",
        "mtp6coopnw.composition",
    )
    violations: list[str] = []
    for path in QT.rglob("*.py"):
        for module in _imports(path):
            if module.startswith(forbidden):
                violations.append(f"{path.name} -> {module}")
    assert violations == []


def test_qt_shell_depends_only_on_presentation_and_ui_contracts() -> None:
    allowed_project_prefixes = (
        "mtp6coopnw.presentation",
        "mtp6coopnw.ui",
    )
    violations: list[str] = []
    for path in QT.rglob("*.py"):
        for module in _imports(path):
            if module.startswith("mtp6coopnw.") and not module.startswith(
                allowed_project_prefixes
            ):
                violations.append(f"{path.name} -> {module}")
    assert violations == []
