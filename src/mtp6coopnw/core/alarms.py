from __future__ import annotations

from dataclasses import dataclass

from mtp6coopnw.core.registry import HostView
from mtp6coopnw.observability import FreshnessState


@dataclass(frozen=True, slots=True)
class CentralAlarm:
    host_id: str
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "hostId": self.host_id,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


def alarms_for_host(view: HostView) -> tuple[CentralAlarm, ...]:
    alarms: list[CentralAlarm] = []

    if view.freshness is FreshnessState.STALE:
        alarms.append(
            CentralAlarm(
                host_id=view.host_id,
                code="AGENT_STALE",
                severity="WARNING",
                message="Agent heartbeat is stale.",
            )
        )
    elif view.freshness is FreshnessState.OFFLINE:
        alarms.append(
            CentralAlarm(
                host_id=view.host_id,
                code="AGENT_OFFLINE",
                severity="FAULT",
                message="Agent heartbeat timed out.",
            )
        )

    if view.healthy is False:
        alarms.append(
            CentralAlarm(
                host_id=view.host_id,
                code="AGENT_DEGRADED",
                severity="WARNING",
                message="Agent reported one or more read-only adapter errors.",
            )
        )

    return tuple(alarms)
