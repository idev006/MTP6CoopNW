from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mtp6coopnw.observability import EventPublisher
from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.policy import PolicyDecision, PolicyEngine, ScheduleRule
from mtp6coopnw.reconciliation import detect_drift


@dataclass(slots=True)
class ControlApplicationFacade:
    """UI-independent facade for preview, plan, apply and reconcile use cases."""

    policy_engine: PolicyEngine
    planner: Planner
    operation_engine: OperationEngine
    event_publisher: EventPublisher | None = None

    def preview(
        self,
        *,
        host_id: str,
        now: datetime,
        policy: dict[str, Any],
        schedules: tuple[ScheduleRule, ...] = (),
        maintenance: PolicyDecision | None = None,
        manual_override: PolicyDecision | None = None,
        emergency: PolicyDecision | None = None,
        safety: PolicyDecision | None = None,
    ) -> dict[str, Any]:
        effective = self.policy_engine.evaluate(
            host_id=host_id,
            now=now,
            policy=policy,
            schedules=schedules,
            maintenance=maintenance,
            manual_override=manual_override,
            emergency=emergency,
            safety=safety,
        )
        self._publish(
            "policy.evaluated",
            timestamp=now,
            host_id=host_id,
            policy_revision=effective.policy_revision,
            data={
                "policyHash": effective.policy_hash,
                "winningSources": list(effective.winning_sources),
                "warnings": list(effective.warnings),
            },
        )
        return {
            "hostId": effective.host_id,
            "evaluatedAt": effective.evaluated_at.isoformat(),
            "policyRevision": effective.policy_revision,
            "policyHash": effective.policy_hash,
            "hostEnabled": effective.host_enabled,
            "internetAllowed": effective.internet_allowed,
            "databaseAllowed": effective.database_allowed,
            "allowedPorts": list(effective.allowed_ports),
            "winningSources": list(effective.winning_sources),
            "warnings": list(effective.warnings),
        }

    def plan(
        self,
        *,
        host_id: str,
        now: datetime,
        policy: dict[str, Any],
        actual: ActualState,
        schedules: tuple[ScheduleRule, ...] = (),
    ) -> dict[str, Any]:
        effective = self.policy_engine.evaluate(
            host_id=host_id,
            now=now,
            policy=policy,
            schedules=schedules,
        )
        plan = self.planner.plan(desired=effective, actual=actual)
        self._publish(
            "operation.plan_created",
            timestamp=now,
            host_id=host_id,
            operation_id=plan.operation_id,
            policy_revision=effective.policy_revision,
            data={
                "noop": plan.noop,
                "verifyFields": list(plan.verify_fields),
                "warnings": list(plan.warnings),
            },
        )
        return {
            "operationId": plan.operation_id,
            "hostId": plan.host_id,
            "noop": plan.noop,
            "changes": [
                {"field": change.field, "before": change.before, "after": change.after}
                for change in plan.changes
            ],
            "verifyFields": list(plan.verify_fields),
            "warnings": list(plan.warnings),
        }

    def reconcile(
        self,
        *,
        host_id: str,
        now: datetime,
        policy: dict[str, Any],
        host: MutableHost,
        schedules: tuple[ScheduleRule, ...] = (),
    ) -> dict[str, Any]:
        effective = self.policy_engine.evaluate(
            host_id=host_id,
            now=now,
            policy=policy,
            schedules=schedules,
        )
        before = detect_drift(effective, host.state)
        if not before.in_sync:
            self._publish(
                "drift.detected",
                timestamp=now,
                host_id=host_id,
                policy_revision=effective.policy_revision,
                data={"fields": list(before.drifted_fields)},
            )
        plan = self.planner.plan(desired=effective, actual=host.state)
        result = self.operation_engine.execute(plan=plan, host=host, now=now)
        after = detect_drift(effective, host.state)
        if before.drifted_fields and after.in_sync:
            self._publish(
                "drift.reconciled",
                timestamp=now,
                host_id=host_id,
                operation_id=result.operation_id,
                policy_revision=effective.policy_revision,
                data={"fields": list(before.drifted_fields)},
            )
        return {
            "operationId": result.operation_id,
            "stage": result.stage.value,
            "rolledBack": result.rolled_back,
            "error": result.error,
            "beforeDrift": list(before.drifted_fields),
            "afterDrift": list(after.drifted_fields),
        }

    def _publish(
        self,
        event_type: str,
        *,
        timestamp: datetime,
        host_id: str,
        operation_id: str | None = None,
        policy_revision: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        if self.event_publisher is None:
            return
        self.event_publisher.publish(
            event_type,
            timestamp=timestamp,
            source="application-facade",
            host_id=host_id,
            operation_id=operation_id,
            policy_revision=policy_revision,
            data=data,
        )
