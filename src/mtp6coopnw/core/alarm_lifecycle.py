from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class AlarmState:
    host_id: str
    code: str
    raised_at: datetime
    active: bool = True
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    cleared_at: datetime | None = None


@dataclass(slots=True)
class AlarmLifecycleStore:
    alarms: dict[tuple[str, str], AlarmState] = field(default_factory=dict)

    def raise_alarm(
        self,
        host_id: str,
        code: str,
        now: datetime,
    ) -> tuple[AlarmState, bool]:
        key = (host_id, code)
        existing = self.alarms.get(key)
        if existing is not None and existing.active:
            return existing, False
        state = AlarmState(host_id=host_id, code=code, raised_at=now)
        self.alarms[key] = state
        return state, True

    def acknowledge(
        self,
        host_id: str,
        code: str,
        actor_id: str,
        now: datetime,
    ) -> AlarmState:
        state = self.alarms[(host_id, code)]
        if not state.active:
            raise ValueError("cannot acknowledge cleared alarm")
        state.acknowledged_by = actor_id
        state.acknowledged_at = now
        return state

    def clear(
        self,
        host_id: str,
        code: str,
        now: datetime,
    ) -> tuple[AlarmState, bool]:
        state = self.alarms[(host_id, code)]
        if not state.active:
            return state, False
        state.active = False
        state.cleared_at = now
        return state, True
