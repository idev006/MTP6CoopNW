from __future__ import annotations

from dataclasses import dataclass

from mtp6coopnw.contracts import HostState


@dataclass(frozen=True, slots=True)
class StateContext:
    online: bool
    healthy: bool | None
    host_enabled: bool
    maintenance: bool = False
    schedule_blocked: bool = False
    recovering: bool = False


def resolve_host_state(context: StateContext) -> HostState:
    if not context.online:
        return HostState.OFFLINE
    if context.recovering:
        return HostState.RECOVERY
    if context.healthy is False:
        return HostState.FAULT
    if context.maintenance:
        return HostState.MAINTENANCE
    if not context.host_enabled:
        return HostState.DISABLED
    if context.schedule_blocked:
        return HostState.SCHEDULE_BLOCKED
    if context.healthy is None:
        return HostState.WARNING
    return HostState.NORMAL
