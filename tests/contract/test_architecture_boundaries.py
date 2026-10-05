from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "mtp6coopnw"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _python_files(folder: Path) -> list[Path]:
    return list(folder.rglob("*.py"))


def test_ui_layer_does_not_import_engines_core_or_adapters() -> None:
    forbidden = (
        "mtp6coopnw.adapters",
        "mtp6coopnw.core",
        "mtp6coopnw.operations",
        "mtp6coopnw.policy",
        "mtp6coopnw.reconciliation",
    )
    violations: list[str] = []
    for path in _python_files(SRC / "ui"):
        for module in _imports(path):
            if module.startswith(forbidden):
                violations.append(f"{path.relative_to(ROOT)} -> {module}")
    assert violations == []


def test_domain_layers_do_not_import_ui_or_web_frameworks() -> None:
    forbidden = ("mtp6coopnw.ui", "fastapi", "flask", "django")
    domain_folders = ("core", "policy", "operations", "reconciliation")
    violations: list[str] = []
    for folder_name in domain_folders:
        for path in _python_files(SRC / folder_name):
            for module in _imports(path):
                if module.startswith(forbidden):
                    violations.append(f"{path.relative_to(ROOT)} -> {module}")
    assert violations == []


def test_application_contract_layer_does_not_import_ui_or_infrastructure() -> None:
    forbidden = ("mtp6coopnw.ui", "mtp6coopnw.adapters")
    violations: list[str] = []
    for path in _python_files(SRC / "application"):
        for module in _imports(path):
            if module.startswith(forbidden):
                violations.append(f"{path.relative_to(ROOT)} -> {module}")
    assert violations == []
