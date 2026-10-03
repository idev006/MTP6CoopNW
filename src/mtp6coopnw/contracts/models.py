from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.contracts.enums import AlarmSeverity, HealthState, HostState, OperationStage


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    passed: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CommandResult:
    success: bool
    operation: str
    target: str
    correlation_id: str
    timestamp: datetime
    policy_revision: int | None = None
    state_before: str | None = None
    state_after: str | None = None
    checks: tuple[CheckResult, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[ErrorDetail, ...] = ()


@dataclass(frozen=True, slots=True)
class OperationStatus:
    operation_id: str
    operation: str
    target: str
    current_stage: OperationStage
    stage_started_at: datetime
    correlation_id: str
    stage_deadline: datetime | None = None
    cancellable: bool = False
    rollback_available: bool = False
    percent_hint: int | None = None
    last_message: str = ""
    error_code: str | None = None


@dataclass(frozen=True, slots=True)
class Alarm:
    alarm_id: str
    severity: AlarmSeverity
    code: str
    message: str
    source: str
    raised_at: datetime
    active: bool = True


@dataclass(frozen=True, slots=True)
class HostStatus:
    host_id: str
    health: HealthState
    state: HostState
    online: bool
    last_heartbeat: datetime | None
    policy_revision: int | None
    schedule_state: str | None = None
    internet_allowed: bool | None = None
    internet_actual: bool | None = None
    database_allowed: bool | None = None
    database_actual: bool | None = None
    managed_ports: tuple[int, ...] = ()
    alarms: tuple[Alarm, ...] = ()
    last_operation: OperationStatus | None = None
