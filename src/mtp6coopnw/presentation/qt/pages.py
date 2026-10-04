from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from mtp6coopnw.presentation.qt.widgets import MetricCard, SectionHeader, StatePill


class OverviewPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 24, 26, 24)
        outer.setSpacing(18)
        outer.addWidget(
            SectionHeader(
                "Network Control Overview",
                "สถานะจาก Facades / Engines แบบ near-real-time — UI ไม่มี business logic",
            )
        )

        metrics = QHBoxLayout()
        self.host_count = MetricCard("Managed Hosts")
        self.online_count = MetricCard("Online")
        self.alarm_count = MetricCard("Active Alarms")
        self.last_operation = MetricCard("Last Operation", "—")
        for card in (self.host_count, self.online_count, self.alarm_count, self.last_operation):
            metrics.addWidget(card)
        outer.addLayout(metrics)

        content = QHBoxLayout()
        content.setSpacing(16)
        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.addWidget(QLabel("Managed Hosts"))
        self.host_table = QTableWidget(0, 7)
        self.host_table.setObjectName("OverviewHostTable")
        self.host_table.setHorizontalHeaderLabels(
            ["Host", "Role", "Freshness", "Health", "Internet", "Database", "Alarms"]
        )
        self.host_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.host_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.host_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.host_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.host_table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.host_table)
        content.addWidget(table_card, 3)

        control_card = QFrame()
        control_card.setObjectName("Card")
        control_card.setMinimumWidth(320)
        controls = QVBoxLayout(control_card)
        controls.setContentsMargins(18, 18, 18, 18)
        controls.setSpacing(14)
        controls.addWidget(QLabel("Selected Host Control"))
        self.selected_host = QLabel("Select a host")
        self.selected_host.setStyleSheet("font-size:18px;font-weight:700;")
        controls.addWidget(self.selected_host)
        state_row = QHBoxLayout()
        self.freshness = StatePill()
        self.health = StatePill()
        state_row.addWidget(self.freshness)
        state_row.addWidget(self.health)
        state_row.addStretch(1)
        controls.addLayout(state_row)
        self.selected_meta = QLabel("—")
        self.selected_meta.setObjectName("PageSubtitle")
        controls.addWidget(self.selected_meta)
        self.host_enabled = QCheckBox("Host enabled")
        self.internet_allowed = QCheckBox("Internet allowed")
        self.database_allowed = QCheckBox("Database access allowed")
        controls.addWidget(self.host_enabled)
        controls.addWidget(self.internet_allowed)
        controls.addWidget(self.database_allowed)
        self.port_summary = QLabel("Allowed ports: —")
        self.port_summary.setWordWrap(True)
        controls.addWidget(self.port_summary)
        self.refresh_button = QPushButton("Refresh from Facade")
        self.refresh_button.setObjectName("SecondaryButton")
        controls.addWidget(self.refresh_button)
        controls.addStretch(1)
        safety = QLabel(
            "คำสั่งถูกตรวจ authorization/interlock ที่ backend อีกครั้ง "
            "สถานะปุ่มใน UI ไม่ใช่ security boundary"
        )
        safety.setWordWrap(True)
        safety.setObjectName("HintText")
        controls.addWidget(safety)
        content.addWidget(control_card, 1)
        outer.addLayout(content, 1)


class HostsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(
            SectionHeader(
                "Hosts",
                "มุมมองสถานะ Desired/Actual ที่ UI รับจาก Facade; ไม่มีการอ่าน Windows โดยตรง",
            )
        )
        self.search = QLineEdit()
        self.search.setPlaceholderText("ค้นหา Host ID หรือ Role")
        self.search.setClearButtonEnabled(True)
        layout.addWidget(self.search)
        self.table = QTableWidget(0, 9)
        self.table.setObjectName("HostsTable")
        self.table.setHorizontalHeaderLabels(
            ["Host", "Role", "Freshness", "Health", "Policy Rev", "Host", "Internet", "Database", "Allowed Ports"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)


class PoliciesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(
            SectionHeader(
                "Policies & Schedule",
                "หน้ากากสำหรับ policy/schedule use cases; กฎ priority และ schedule อยู่ใน Engines",
            )
        )
        note = QFrame()
        note.setObjectName("InfoCard")
        note_layout = QVBoxLayout(note)
        note_layout.addWidget(QLabel("Facade-driven policy workspace"))
        detail = QLabel(
            "UI จะแสดง Effective Policy, Schedule, Maintenance, Manual Override และ Preview/Dry-run "
            "เมื่อ Application Facade เปิด contract ที่เกี่ยวข้องครบถ้วน โดย Qt จะไม่คำนวณ policy เอง"
        )
        detail.setWordWrap(True)
        detail.setObjectName("HintText")
        note_layout.addWidget(detail)
        layout.addWidget(note)

        grid = QGridLayout()
        self.effective_policy = MetricCard("Effective Policy", "Facade")
        self.schedule_state = MetricCard("Schedule", "Engine")
        self.maintenance_state = MetricCard("Maintenance", "Engine")
        self.override_state = MetricCard("Override", "Engine")
        grid.addWidget(self.effective_policy, 0, 0)
        grid.addWidget(self.schedule_state, 0, 1)
        grid.addWidget(self.maintenance_state, 1, 0)
        grid.addWidget(self.override_state, 1, 1)
        layout.addLayout(grid)

        preview_box = QGroupBox("Preview / Dry-run")
        preview_layout = QVBoxLayout(preview_box)
        preview_layout.addWidget(
            QLabel("Current → Desired → Planned Changes → Interlocks → Verification → Rollback")
        )
        layout.addWidget(preview_box)
        layout.addStretch(1)


class AlarmsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(
            SectionHeader(
                "Alarms",
                "สรุป alarm จาก presentation state; lifecycle acknowledge/clear ต้องผ่าน Facade",
            )
        )
        self.summary = QLabel("Active alarms: 0")
        self.summary.setStyleSheet("font-size:16px;font-weight:600;")
        layout.addWidget(self.summary)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Host", "Alarm Count", "Freshness", "Health"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)
        hint = QLabel("Alarm details and acknowledge/clear bind only through a stable Alarm Facade contract.")
        hint.setObjectName("HintText")
        hint.setWordWrap(True)
        layout.addWidget(hint)


class AuditPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(
            SectionHeader(
                "Audit & History",
                "หน้าจออ่านประวัติคำสั่งและผลลัพธ์; Qt ไม่อ่าน AuditStore โดยตรง",
            )
        )
        card = QFrame()
        card.setObjectName("InfoCard")
        box = QVBoxLayout(card)
        box.addWidget(QLabel("Audit Query Facade required"))
        text = QLabel(
            "หน้านี้จะเปิดใช้งานเมื่อมี read-only Audit Query contract ที่คืน actor / action / target / timestamp / operation / result แบบ typed DTO"
        )
        text.setWordWrap(True)
        text.setObjectName("HintText")
        box.addWidget(text)
        layout.addWidget(card)
        layout.addStretch(1)


class SystemPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(
            SectionHeader(
                "System",
                "สถานะ presentation/event synchronization; diagnostics เชิงระบบต้องมาจาก Facade",
            )
        )
        metrics = QHBoxLayout()
        self.sequence = MetricCard("Event Sequence", "0")
        self.resyncs = MetricCard("Resync Count", "0")
        self.hosts = MetricCard("Hosts", "0")
        self.alarms = MetricCard("Alarms", "0")
        for card in (self.sequence, self.resyncs, self.hosts, self.alarms):
            metrics.addWidget(card)
        layout.addLayout(metrics)
        note = QLabel(
            "Core/Agent/Adapter/mTLS diagnostics จะถูกเพิ่มผ่าน System/Diagnostics Facade; presentation layer จะไม่ import infrastructure โดยตรง"
        )
        note.setWordWrap(True)
        note.setObjectName("HintText")
        layout.addWidget(note)
        layout.addStretch(1)
