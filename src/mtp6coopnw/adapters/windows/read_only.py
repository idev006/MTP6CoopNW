from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mtp6coopnw.adapters.windows.powershell import PowerShellReadOnlyBridge


@dataclass(slots=True)
class PowerShellNetworkPort:
    bridge: PowerShellReadOnlyBridge
    interface_alias: str | None = None

    def get_state(self) -> dict[str, Any]:
        parameters: dict[str, Any] = {}
        if self.interface_alias:
            parameters["InterfaceAlias"] = self.interface_alias
        result = self.bridge.invoke("network.state", parameters)
        return {"interfaces": _as_list(result)}


@dataclass(slots=True)
class PowerShellFirewallPort:
    bridge: PowerShellReadOnlyBridge
    prefix: str = "MTP6CoopNW-"

    def get_state(self) -> dict[str, Any]:
        result = self.bridge.invoke(
            "firewall.managed_state",
            {"Prefix": self.prefix},
        )
        return {"managed_rules": _as_list(result)}


@dataclass(slots=True)
class PowerShellSqlPort:
    bridge: PowerShellReadOnlyBridge
    computer_name: str
    port: int = 1433
    service_name: str = "MSSQLSERVER"

    def get_state(self) -> dict[str, Any]:
        service = self.bridge.invoke(
            "sql.service_state",
            {"ServiceName": self.service_name},
        )
        tcp = self.bridge.invoke(
            "sql.tcp_test",
            {"ComputerName": self.computer_name, "Port": self.port},
        )
        return {"service": service, "tcp": tcp}


@dataclass(slots=True)
class PowerShellServicePort:
    bridge: PowerShellReadOnlyBridge
    names: tuple[str, ...]

    def get_state(self) -> dict[str, Any]:
        result = self.bridge.invoke("services.state", {"Name": list(self.names)})
        return {"services": _as_list(result)}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
