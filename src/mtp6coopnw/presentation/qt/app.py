from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any

from PySide6.QtWidgets import QApplication

from mtp6coopnw.presentation.qt.main_window import MainWindow
from mtp6coopnw.ui import DashboardPresenter


def run_desktop(
    *,
    presenter: DashboardPresenter,
    actions: Any,
    argv: Sequence[str] | None = None,
) -> int:
    """Run the Qt shell with already-composed presentation dependencies."""
    app = QApplication(list(argv) if argv is not None else sys.argv)
    window = MainWindow(presenter=presenter, actions=actions)
    window.show()
    return app.exec()
