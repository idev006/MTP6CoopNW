from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mtp6coopnw.presentation.qt.pages import (
    AlarmsPage,
    AuditPage,
    HostsPage,
    OverviewPage,
    PoliciesPage,
    SystemPage,
)
from mtp6coopnw.presentation.qt.theme import APP_STYLESHEET
from mtp6coopnw.ui import DashboardPresenter, DashboardViewModel, HostCardViewModel


class OperatorActions(Protocol):
    def set_host_enabled(self, host_id: str, enabled: bool) -> dict[str, Any]: ...
    def set_internet_allowed(self, host_id: str, allowed: bool) -> dict[str, Any]: ...
    def set_database_allowed(self, host_id: str, allowed: bool) -> dict[str, Any]: ...


class MainWindow(QMainWindow):
    """Concrete PySide6 shell over Facade + Presenter/ViewModel contracts only."""

    def __init__(
        self,
        *,
        presenter: DashboardPresenter,
        actions: OperatorActions,
        event_interval_ms: int = 500,
    ) -> None:
        super().__init__()
        self.presenter = presenter
        self.actions = actions
        self._updating_controls = False
        self._selected_host_id: str | None = None

        self.setWindowTitle("MTP6CoopNW Control Center")
        self.resize(1440, 860)
        self.setMinimumSize(1120, 700)
        self.setStyleSheet(APP_STYLESHEET)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)
        self.overview = OverviewPage()
        self.hosts_page = HostsPage()
        self.policies_page = PoliciesPage()
        self.alarms_page = AlarmsPage()
        self.audit_page = AuditPage()
        self.system_page = SystemPage()
        for page in (
            self.overview,
            self.hosts_page,
            self.policies_page,
            self.alarms_page,
            self.audit_page,
            self.system_page,
        ):
            self.stack.addWidget(page)

        self._wire_actions()
        self.statusBar().showMessage("Ready")
        self._render(self.presenter.load())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._drain_events)
        self.timer.start(max(100, event_interval_ms))

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(228)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(6)
        brand = QLabel("MTP6CoopNW")
        brand.setObjectName("Brand")
        layout.addWidget(brand)
        sub = QLabel("Control Center")
        sub.setObjectName("BrandSubtitle")
        layout.addWidget(sub)

        self.nav_buttons: list[QPushButton] = []
        labels = (
            "Overview",
            "Hosts",
            "Policies & Schedule",
            "Alarms",
            "Audit & History",
            "System",
        )
        for index, text in enumerate(labels):
            button = QPushButton(text)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, i=index: self._navigate(i))
            self.nav_buttons.append(button)
            layout.addWidget(button)
        self.nav_buttons[0].setChecked(True)
        layout.addStretch(1)
        footer = QLabel("Engine-first\nFacade-driven UI")
        footer.setObjectName("SidebarFooter")
        layout.addWidget(footer)
        return sidebar

    def _wire_actions(self) -> None:
        self.overview.host_table.itemSelectionChanged.connect(self._on_host_selected)
        self.overview.refresh_button.clicked.connect(self._force_reload)
        self.overview.host_enabled.toggled.connect(self._change_host_enabled)
        self.overview.internet_allowed.toggled.connect(self._change_internet)
        self.overview.database_allowed.toggled.connect(self._change_database)
        self.hosts_page.search.textChanged.connect(self._render_host_inventory)

    def _navigate(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def _drain_events(self) -> None:
        try:
            self._render(self.presenter.refresh_from_events(timeout_seconds=0.0, limit=100))
        except Exception as exc:
            self.statusBar().showMessage(f"Event update failed: {exc}")

    def _force_reload(self) -> None:
        try:
            self._render(self.presenter.load())
            self.statusBar().showMessage("Snapshot reloaded from Facade")
        except Exception as exc:
            self._show_error("Refresh failed", str(exc))

    def _render(self, model: DashboardViewModel) -> None:
        hosts = sorted(model.hosts.values(), key=lambda item: item.host_id)
        self._render_overview_table(hosts)
        self._render_host_inventory()
        self._render_alarm_summary(hosts, model)
        self._render_system(model)

        self.overview.host_count.set_value(len(hosts))
        self.overview.online_count.set_value(sum(h.freshness == "ONLINE" for h in hosts))
        self.overview.alarm_count.set_value(model.active_alarm_count)
        if model.operation_stages:
            self.overview.last_operation.set_value(next(reversed(model.operation_stages.values())))
        else:
            self.overview.last_operation.set_value("—")

        if self._selected_host_id in model.hosts:
            self._select_host_in_table(self._selected_host_id or "")
            self._render_selected(model.hosts[self._selected_host_id or ""])
        elif hosts:
            self._selected_host_id = hosts[0].host_id
            self._select_host_in_table(hosts[0].host_id)
            self._render_selected(hosts[0])
        else:
            self._render_no_selection()

    def _render_overview_table(self, hosts: list[HostCardViewModel]) -> None:
        table = self.overview.host_table
        table.setRowCount(len(hosts))
        for row, host in enumerate(hosts):
            values = (
                host.host_id,
                host.role,
                host.freshness,
                host.health,
                "ON" if host.control["internetAllowed"] else "OFF",
                "ON" if host.control["databaseAllowed"] else "OFF",
                str(host.alarm_count),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                table.setItem(row, column, item)

    def _render_host_inventory(self) -> None:
        needle = self.hosts_page.search.text().strip().lower()
        hosts = sorted(self.presenter.model.hosts.values(), key=lambda item: item.host_id)
        if needle:
            hosts = [
                host
                for host in hosts
                if needle in host.host_id.lower() or needle in host.role.lower()
            ]
        table = self.hosts_page.table
        table.setRowCount(len(hosts))
        for row, host in enumerate(hosts):
            values = (
                host.host_id,
                host.role,
                host.freshness,
                host.health,
                str(host.policy_revision or "—"),
                "ON" if host.control["hostEnabled"] else "OFF",
                "ON" if host.control["internetAllowed"] else "OFF",
                "ON" if host.control["databaseAllowed"] else "OFF",
                ", ".join(str(p) for p in host.control["allowedPorts"]) or "—",
            )
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))

    def _render_alarm_summary(
        self, hosts: list[HostCardViewModel], model: DashboardViewModel
    ) -> None:
        self.alarms_page.summary.setText(f"Active alarms: {model.active_alarm_count}")
        alarm_hosts = [host for host in hosts if host.alarm_count > 0]
        table = self.alarms_page.table
        table.setRowCount(len(alarm_hosts))
        for row, host in enumerate(alarm_hosts):
            for column, value in enumerate(
                (host.host_id, str(host.alarm_count), host.freshness, host.health)
            ):
                table.setItem(row, column, QTableWidgetItem(value))

    def _render_system(self, model: DashboardViewModel) -> None:
        self.system_page.sequence.set_value(model.latest_sequence)
        self.system_page.resyncs.set_value(model.resync_count)
        self.system_page.hosts.set_value(len(model.hosts))
        self.system_page.alarms.set_value(model.active_alarm_count)

    def _select_host_in_table(self, host_id: str) -> None:
        for row in range(self.overview.host_table.rowCount()):
            item = self.overview.host_table.item(row, 0)
            if item is not None and item.text() == host_id:
                self.overview.host_table.selectRow(row)
                return

    def _on_host_selected(self) -> None:
        rows = self.overview.host_table.selectionModel().selectedRows()
        if not rows:
            return
        item = self.overview.host_table.item(rows[0].row(), 0)
        if item is None:
            return
        self._selected_host_id = item.text()
        host = self.presenter.model.hosts.get(self._selected_host_id)
        if host is not None:
            self._render_selected(host)

    def _render_selected(self, host: HostCardViewModel) -> None:
        self._updating_controls = True
        try:
            self.overview.selected_host.setText(host.host_id)
            self.overview.freshness.set_state(host.freshness)
            self.overview.health.set_state(host.health)
            self.overview.selected_meta.setText(
                f"{host.role} • policy r{host.policy_revision or '—'} • alarms {host.alarm_count}"
            )
            self.overview.host_enabled.setChecked(host.control["hostEnabled"])
            self.overview.internet_allowed.setChecked(host.control["internetAllowed"])
            self.overview.database_allowed.setChecked(host.control["databaseAllowed"])
            ports = ", ".join(str(port) for port in host.control["allowedPorts"]) or "none"
            self.overview.port_summary.setText(f"Allowed ports: {ports}")
            can_apply = host.actions["canApply"]
            self.overview.host_enabled.setEnabled(can_apply)
            self.overview.internet_allowed.setEnabled(can_apply)
            self.overview.database_allowed.setEnabled(can_apply)
        finally:
            self._updating_controls = False

    def _render_no_selection(self) -> None:
        self._updating_controls = True
        try:
            self.overview.selected_host.setText("No managed host")
            self.overview.freshness.set_state("UNKNOWN")
            self.overview.health.set_state("UNKNOWN")
            self.overview.selected_meta.setText("—")
            for control in (
                self.overview.host_enabled,
                self.overview.internet_allowed,
                self.overview.database_allowed,
            ):
                control.setChecked(False)
                control.setEnabled(False)
            self.overview.port_summary.setText("Allowed ports: —")
        finally:
            self._updating_controls = False

    def _change_host_enabled(self, enabled: bool) -> None:
        if self._updating_controls or self._selected_host_id is None:
            return
        if not enabled:
            answer = QMessageBox.question(
                self,
                "Confirm host disable",
                f"Disable logical access for {self._selected_host_id}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                self._render_selected(self.presenter.model.hosts[self._selected_host_id])
                return
        self._execute_action(
            "Host control",
            lambda: self.actions.set_host_enabled(self._selected_host_id or "", enabled),
        )

    def _change_internet(self, allowed: bool) -> None:
        if self._updating_controls or self._selected_host_id is None:
            return
        self._execute_action(
            "Internet control",
            lambda: self.actions.set_internet_allowed(self._selected_host_id or "", allowed),
        )

    def _change_database(self, allowed: bool) -> None:
        if self._updating_controls or self._selected_host_id is None:
            return
        self._execute_action(
            "Database control",
            lambda: self.actions.set_database_allowed(self._selected_host_id or "", allowed),
        )

    def _execute_action(self, title: str, action: Callable[[], dict[str, Any]]) -> None:
        try:
            result = action()
            stage = str(result.get("stage", "UNKNOWN"))
            self.statusBar().showMessage(
                f"{title}: {stage} • operation {result.get('operationId', '—')}"
            )
            self._drain_events()
        except Exception as exc:
            self._show_error(title, str(exc))
            if self._selected_host_id in self.presenter.model.hosts:
                self._render_selected(self.presenter.model.hosts[self._selected_host_id])

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)
        self.statusBar().showMessage(f"{title}: failed")
