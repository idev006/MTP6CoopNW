from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Protocol

from mtp6coopnw.application.models import CommandExecutionResult
from mtp6coopnw.observability import EventBatch
from mtp6coopnw.operations import (
    ActualState,
    MutableHost,
    OperationPlan,
    OperationResult,
)
from mtp6coopnw.policy import EffectivePolicy, PolicyDecision, ScheduleRule


class PolicyEvaluationService(Protocol):
    """Programming contract exposed by a policy engine implementation."""

    def evaluate(
        self,
        *,
        host_id: str,
        now: datetime,
        policy: dict[str, Any],
        schedules: Iterable[ScheduleRule] = (),
        maintenance: PolicyDecision | None = None,
        manual_override: PolicyDecision | None = None,
        emergency: PolicyDecision | None = None,
        safety: PolicyDecision | None = None,
    ) -> EffectivePolicy: ...


class PlanningService(Protocol):
    """Programming contract exposed by a planning engine implementation."""

    def plan(self, *, desired: EffectivePolicy, actual: ActualState) -> OperationPlan: ...


class OperationService(Protocol):
    """Programming contract exposed by an operation engine implementation."""

    def execute(
        self,
        *,
        plan: OperationPlan,
        host: MutableHost,
        now: datetime,
        simulated_apply_seconds: int = 0,
        simulated_verify_seconds: int = 0,
    ) -> OperationResult: ...


class CommandExecutionService(Protocol):
    """Application service that executes a presentation-originated control intent."""

    def apply(
        self,
        *,
        host_id: str,
        desired: dict[str, Any],
        now: datetime,
    ) -> CommandExecutionResult: ...


class StatusQueryService(Protocol):
    """Read-only application contract consumed by presentation facades."""

    def system_status(self) -> dict[str, Any]: ...

    def list_hosts(self) -> list[dict[str, Any]]: ...

    def get_host(self, host_id: str) -> dict[str, Any]: ...

    def get_alarms(self) -> list[dict[str, str]]: ...

    def get_policy(self, host_id: str) -> dict[str, Any] | None: ...


class EventStream(Protocol):
    """Replayable application-event stream contract."""

    @property
    def latest_sequence(self) -> int: ...

    def wait(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> EventBatch: ...


class UiEventService(Protocol):
    """Snapshot/event contract consumed by a UI facade."""

    def bootstrap(self) -> dict[str, Any]: ...

    def next_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> dict[str, Any]: ...


class AuditSink(Protocol):
    def append(self, event: dict[str, Any]) -> None: ...


class StateReporter(Protocol):
    def report(
        self,
        *,
        host_id: str,
        state: dict[str, Any],
        policy_revision: int,
        now: datetime,
    ) -> None: ...
