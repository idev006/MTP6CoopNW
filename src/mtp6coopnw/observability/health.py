from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from mtp6coopnw.contracts import CheckResult, HealthState


class FreshnessState(StrEnum):
    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    STALE = "STALE"
    OFFLINE = "OFFLINE"


@dataclass(frozen=True, slots=True)
class HealthReport:
    component: str
    state: HealthState
    checked_at: datetime
    checks: tuple[CheckResult, ...] = ()
    message: str = ""
    dependencies: dict[str, HealthState] = field(default_factory=dict)


def classify_freshness(
    *,
    now: datetime,
    last_heartbeat: datetime | None,
    stale_after_seconds: int,
    offline_after_seconds: int,
) -> FreshnessState:
    if stale_after_seconds < 1:
        raise ValueError("stale_after_seconds must be >= 1")
    if offline_after_seconds <= stale_after_seconds:
        raise ValueError("offline_after_seconds must be greater than stale_after_seconds")
    if last_heartbeat is None:
        return FreshnessState.UNKNOWN

    age_seconds = (now - last_heartbeat).total_seconds()
    if age_seconds < 0:
        return FreshnessState.STALE
    if age_seconds >= offline_after_seconds:
        return FreshnessState.OFFLINE
    if age_seconds >= stale_after_seconds:
        return FreshnessState.STALE
    return FreshnessState.ONLINE
