from __future__ import annotations

from dataclasses import dataclass

from mtp6coopnw.operations import (
    ActualState,
    MutableHost,
    OperationEngine,
    OperationResult,
    Planner,
)
from mtp6coopnw.policy import EffectivePolicy


@dataclass(frozen=True, slots=True)
class DriftReport:
    host_id: str
    drifted_fields: tuple[str, ...]

    @property
    def in_sync(self) -> bool:
        return not self.drifted_fields


def detect_drift(desired: EffectivePolicy, actual: ActualState) -> DriftReport:
    drift: list[str] = []
    for field in ("host_enabled", "internet_allowed", "database_allowed", "allowed_ports"):
        if getattr(desired, field) != getattr(actual, field):
            drift.append(field)
    return DriftReport(desired.host_id, tuple(drift))


@dataclass(slots=True)
class ReconciliationEngine:
    planner: Planner
    executor: OperationEngine

    def reconcile(self, *, desired: EffectivePolicy, host: MutableHost) -> OperationResult:
        plan = self.planner.plan(desired=desired, actual=host.state)
        return self.executor.execute(plan=plan, host=host, now=desired.evaluated_at)
