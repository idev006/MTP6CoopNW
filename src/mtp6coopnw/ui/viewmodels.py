from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mtp6coopnw.ui.contracts import ActionAvailabilityPayload, ControlStatePayload


@dataclass(slots=True)
class HostCardViewModel:
    host_id: str
    role: str
    freshness: str
    health: str
    policy_revision: int | None
    alarm_count: int
    control: ControlStatePayload
    actions: ActionAvailabilityPayload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "HostCardViewModel":
        revision = payload.get("policyRevision")
        raw_control = payload.get("control", {})
        if not isinstance(raw_control, dict):
            raw_control = {}
        control: ControlStatePayload = {
            "hostEnabled": bool(raw_control.get("hostEnabled", True)),
            "internetAllowed": bool(raw_control.get("internetAllowed", False)),
            "databaseAllowed": bool(raw_control.get("databaseAllowed", False)),
            "allowedPorts": [
                int(port)
                for port in raw_control.get("allowedPorts", [])
                if isinstance(port, int) and not isinstance(port, bool)
            ],
        }

        raw_actions = payload.get("actions", {})
        if not isinstance(raw_actions, dict):
            raw_actions = {}
        actions: ActionAvailabilityPayload = {
            "canViewDetails": bool(raw_actions.get("canViewDetails", False)),
            "canPlan": bool(raw_actions.get("canPlan", False)),
            "canApply": bool(raw_actions.get("canApply", False)),
            "canRetry": bool(raw_actions.get("canRetry", False)),
            "canEnterMaintenance": bool(
                raw_actions.get("canEnterMaintenance", False)
            ),
        }

        return cls(
            host_id=str(payload["hostId"]),
            role=str(payload["role"]),
            freshness=str(payload["freshness"]),
            health=str(payload["health"]),
            policy_revision=revision if isinstance(revision, int) else None,
            alarm_count=int(payload.get("alarmCount", 0)),
            control=control,
            actions=actions,
        )


@dataclass(slots=True)
class DashboardViewModel:
    hosts: dict[str, HostCardViewModel] = field(default_factory=dict)
    active_alarm_count: int = 0
    latest_sequence: int = 0
    operation_stages: dict[str, str] = field(default_factory=dict)
    resync_count: int = 0
