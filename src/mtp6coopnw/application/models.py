from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ControlState:
    host_enabled: bool
    internet_allowed: bool
    database_allowed: bool
    allowed_ports: tuple[int, ...]
    lan_reachable: bool
    control_reachable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostEnabled": self.host_enabled,
            "internetAllowed": self.internet_allowed,
            "databaseAllowed": self.database_allowed,
            "allowedPorts": list(self.allowed_ports),
            "lanReachable": self.lan_reachable,
            "controlReachable": self.control_reachable,
        }


@dataclass(frozen=True, slots=True)
class CommandExecutionResult:
    """Typed internal result for a state-changing application command."""

    operation_id: str
    stage: str
    rolled_back: bool
    error: str | None
    policy_revision: int
    state: ControlState

    def to_dict(self) -> dict[str, Any]:
        return {
            "operationId": self.operation_id,
            "stage": self.stage,
            "rolledBack": self.rolled_back,
            "error": self.error,
            "policyRevision": self.policy_revision,
            "state": self.state.to_dict(),
        }
