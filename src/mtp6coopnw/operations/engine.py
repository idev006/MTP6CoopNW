from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from mtp6coopnw.contracts import OperationStage
from mtp6coopnw.policy import EffectivePolicy


@dataclass(frozen=True, slots=True)
class ActualState:
    host_enabled: bool
    internet_allowed: bool
    database_allowed: bool
    allowed_ports: tuple[int, ...]
    lan_reachable: bool = True
    control_reachable: bool = True


@dataclass(frozen=True, slots=True)
class PlannedChange:
    field: str
    before: Any
    after: Any


@dataclass(frozen=True, slots=True)
class OperationPlan:
    operation_id: str
    host_id: str
    created_at: datetime
    changes: tuple[PlannedChange, ...]
    verify_fields: tuple[str, ...]
    rollback: tuple[PlannedChange, ...]
    warnings: tuple[str, ...] = ()

    @property
    def noop(self) -> bool:
        return not self.changes


class PlanningError(ValueError):
    """Raised when interlocks do not allow a safe plan."""


@dataclass(slots=True)
class Planner:
    def plan(self, *, desired: EffectivePolicy, actual: ActualState) -> OperationPlan:
        mapping: dict[str, Any] = {
            "host_enabled": desired.host_enabled,
            "internet_allowed": desired.internet_allowed,
            "database_allowed": desired.database_allowed,
            "allowed_ports": desired.allowed_ports,
        }
        changes: list[PlannedChange] = []
        rollback: list[PlannedChange] = []
        for field_name, after in mapping.items():
            before = getattr(actual, field_name)
            if before != after:
                changes.append(PlannedChange(field_name, before, after))
                rollback.insert(0, PlannedChange(field_name, after, before))

        warnings: list[str] = []
        if not actual.lan_reachable or not actual.control_reachable:
            raise PlanningError("control/LAN reachability must be healthy before apply")
        if not desired.host_enabled:
            warnings.append("host_disable_requires_process_level_enforcement")

        return OperationPlan(
            operation_id=str(uuid4()),
            host_id=desired.host_id,
            created_at=desired.evaluated_at,
            changes=tuple(changes),
            verify_fields=tuple(change.field for change in changes),
            rollback=tuple(rollback),
            warnings=tuple(warnings),
        )


@dataclass(slots=True)
class MutableHost:
    state: ActualState
    fail_on_field: str | None = None
    fail_verification: bool = False

    def apply(self, change: PlannedChange) -> None:
        if self.fail_on_field == change.field:
            raise RuntimeError(f"simulated apply failure: {change.field}")
        data: dict[str, Any] = {
            "host_enabled": self.state.host_enabled,
            "internet_allowed": self.state.internet_allowed,
            "database_allowed": self.state.database_allowed,
            "allowed_ports": self.state.allowed_ports,
            "lan_reachable": self.state.lan_reachable,
            "control_reachable": self.state.control_reachable,
        }
        data[change.field] = change.after
        self.state = ActualState(**data)


@dataclass(frozen=True, slots=True)
class OperationResult:
    operation_id: str
    stage: OperationStage
    state: ActualState
    rolled_back: bool
    error: str | None = None
    history: tuple[OperationStage, ...] = ()


@dataclass(slots=True)
class OperationEngine:
    apply_timeout_seconds: int = 30
    verify_timeout_seconds: int = 20

    def execute(
        self,
        *,
        plan: OperationPlan,
        host: MutableHost,
        now: datetime,
        simulated_apply_seconds: int = 0,
        simulated_verify_seconds: int = 0,
    ) -> OperationResult:
        del now
        history = [
            OperationStage.REQUESTED,
            OperationStage.VALIDATING,
            OperationStage.PLANNING,
        ]
        before = host.state
        if plan.noop:
            history.extend([OperationStage.VERIFYING, OperationStage.COMPLETED])
            return OperationResult(
                plan.operation_id,
                OperationStage.COMPLETED,
                host.state,
                False,
                history=tuple(history),
            )

        history.append(OperationStage.APPLYING)
        if simulated_apply_seconds > self.apply_timeout_seconds:
            history.append(OperationStage.TIMED_OUT)
            return OperationResult(
                plan.operation_id,
                OperationStage.TIMED_OUT,
                host.state,
                False,
                "apply timeout",
                tuple(history),
            )

        try:
            for change in plan.changes:
                host.apply(change)
        except Exception as exc:
            history.extend([OperationStage.FAILED, OperationStage.ROLLING_BACK])
            self._restore(host, before)
            history.append(OperationStage.ROLLED_BACK)
            return OperationResult(
                plan.operation_id,
                OperationStage.ROLLED_BACK,
                host.state,
                True,
                str(exc),
                tuple(history),
            )

        history.append(OperationStage.VERIFYING)
        if simulated_verify_seconds > self.verify_timeout_seconds or host.fail_verification:
            history.extend([OperationStage.FAILED, OperationStage.ROLLING_BACK])
            self._restore(host, before)
            history.append(OperationStage.ROLLED_BACK)
            return OperationResult(
                plan.operation_id,
                OperationStage.ROLLED_BACK,
                host.state,
                True,
                "verification failed",
                tuple(history),
            )

        for change in plan.changes:
            if getattr(host.state, change.field) != change.after:
                history.extend([OperationStage.FAILED, OperationStage.ROLLING_BACK])
                self._restore(host, before)
                history.append(OperationStage.ROLLED_BACK)
                return OperationResult(
                    plan.operation_id,
                    OperationStage.ROLLED_BACK,
                    host.state,
                    True,
                    "read-back mismatch",
                    tuple(history),
                )
        if not host.state.lan_reachable or not host.state.control_reachable:
            history.extend([OperationStage.FAILED, OperationStage.ROLLING_BACK])
            self._restore(host, before)
            history.append(OperationStage.ROLLED_BACK)
            return OperationResult(
                plan.operation_id,
                OperationStage.ROLLED_BACK,
                host.state,
                True,
                "control-channel interlock",
                tuple(history),
            )

        history.append(OperationStage.COMPLETED)
        return OperationResult(
            plan.operation_id,
            OperationStage.COMPLETED,
            host.state,
            False,
            history=tuple(history),
        )

    @staticmethod
    def _restore(host: MutableHost, before: ActualState) -> None:
        host.state = before
