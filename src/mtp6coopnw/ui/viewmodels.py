from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class HostCardViewModel:
    host_id: str
    role: str
    freshness: str
    health: str
    policy_revision: int | None
    alarm_count: int
    actions: dict[str, bool]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "HostCardViewModel":
        revision = payload.get("policyRevision")
        return cls(
            host_id=str(payload["hostId"]),
            role=str(payload["role"]),
            freshness=str(payload["freshness"]),
            health=str(payload["health"]),
            policy_revision=revision if isinstance(revision, int) else None,
            alarm_count=int(payload.get("alarmCount", 0)),
            actions={
                str(key): bool(value)
                for key, value in dict(payload.get("actions", {})).items()
            },
        )


@dataclass(slots=True)
class DashboardViewModel:
    hosts: dict[str, HostCardViewModel] = field(default_factory=dict)
    active_alarm_count: int = 0
    latest_sequence: int = 0
    operation_stages: dict[str, str] = field(default_factory=dict)
    resync_count: int = 0
