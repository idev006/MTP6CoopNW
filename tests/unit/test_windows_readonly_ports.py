from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mtp6coopnw.adapters.windows import (
    PowerShellFirewallPort,
    PowerShellNetworkPort,
    PowerShellServicePort,
    PowerShellSqlPort,
)


@dataclass
class StubBridge:
    responses: dict[str, Any]
    calls: list[tuple[str, dict[str, Any]]] = field(default_factory=list)

    def invoke(
        self,
        operation: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        self.calls.append((operation, dict(parameters or {})))
        return self.responses.get(operation)


def test_network_port_normalizes_single_object_to_list() -> None:
    bridge = StubBridge(
        responses={"network.state": {"InterfaceAlias": "Ethernet"}}
    )
    port = PowerShellNetworkPort(bridge=bridge)  # type: ignore[arg-type]

    state = port.get_state()

    assert state["interfaces"] == [{"InterfaceAlias": "Ethernet"}]
    assert bridge.calls == [("network.state", {})]


def test_firewall_port_uses_project_prefix() -> None:
    bridge = StubBridge(responses={"firewall.managed_state": []})
    port = PowerShellFirewallPort(bridge=bridge)  # type: ignore[arg-type]

    state = port.get_state()

    assert state["managed_rules"] == []
    assert bridge.calls[-1][1]["Prefix"] == "MTP6CoopNW-"


def test_sql_port_combines_service_and_tcp_state() -> None:
    bridge = StubBridge(
        responses={
            "sql.service_state": {"Status": "Running"},
            "sql.tcp_test": {"TcpTestSucceeded": True},
        }
    )
    port = PowerShellSqlPort(
        bridge=bridge,  # type: ignore[arg-type]
        computer_name="192.168.1.10",
    )

    state = port.get_state()

    assert state["service"]["Status"] == "Running"
    assert state["tcp"]["TcpTestSucceeded"] is True
    assert bridge.calls[-1] == (
        "sql.tcp_test",
        {"ComputerName": "192.168.1.10", "Port": 1433},
    )


def test_service_port_passes_configured_names() -> None:
    bridge = StubBridge(responses={"services.state": []})
    port = PowerShellServicePort(
        bridge=bridge,  # type: ignore[arg-type]
        names=("MSSQLSERVER",),
    )

    port.get_state()

    assert bridge.calls[-1] == ("services.state", {"Name": ["MSSQLSERVER"]})
