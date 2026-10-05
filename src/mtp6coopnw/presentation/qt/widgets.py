from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class MetricCard(QFrame):
    """Small presentation-only metric card."""

    def __init__(self, title: str, value: str = "0", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str | int) -> None:
        self.value_label.setText(str(value))


class StatePill(QLabel):
    """Text-first state indicator. Color is supplemental, never the only signal."""

    def __init__(self, text: str = "UNKNOWN", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(74)
        self._apply(text)

    def set_state(self, value: str) -> None:
        self.setText(value)
        self._apply(value)

    def _apply(self, value: str) -> None:
        palette = {
            "ONLINE": ("#067647", "#ecfdf3"),
            "HEALTHY": ("#067647", "#ecfdf3"),
            "COMPLETED": ("#067647", "#ecfdf3"),
            "STALE": ("#b54708", "#fffaeb"),
            "WARNING": ("#b54708", "#fffaeb"),
            "DEGRADED": ("#b54708", "#fffaeb"),
            "OFFLINE": ("#b42318", "#fef3f2"),
            "FAULT": ("#b42318", "#fef3f2"),
            "ROLLED_BACK": ("#b42318", "#fef3f2"),
            "UNKNOWN": ("#475467", "#f2f4f7"),
        }
        fg, bg = palette.get(value.upper(), ("#475467", "#f2f4f7"))
        self.setStyleSheet(
            f"color:{fg}; background:{bg}; border-radius:10px; padding:3px 8px; font-weight:600;"
        )


class SectionHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        text = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setWordWrap(True)
        text.addWidget(title_label)
        if subtitle:
            text.addWidget(subtitle_label)
        row.addLayout(text, 1)
