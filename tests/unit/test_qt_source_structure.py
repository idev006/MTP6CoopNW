from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QT = ROOT / "src" / "mtp6coopnw" / "presentation" / "qt"


def test_qt_source_is_syntax_valid_without_importing_pyside() -> None:
    for path in QT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_main_window_exposes_all_primary_navigation_pages() -> None:
    source = (QT / "main_window.py").read_text(encoding="utf-8")
    for page in (
        "OverviewPage",
        "HostsPage",
        "PoliciesPage",
        "AlarmsPage",
        "AuditPage",
        "SystemPage",
    ):
        assert page in source
