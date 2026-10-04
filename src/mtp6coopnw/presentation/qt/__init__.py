"""PySide6 desktop presentation shell.

This package contains rendering/input mechanics only. Business/control logic
remains behind Facade and Presenter/ViewModel contracts.
"""

from mtp6coopnw.presentation.qt.main_window import MainWindow

__all__ = ["MainWindow"]
