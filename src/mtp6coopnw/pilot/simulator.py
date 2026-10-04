from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.policy import (
    PolicyDecision,
    PolicyEngine,
    ScheduleRule,
    VersionedPolicyStore,
)
from mtp6coopnw.reconciliation import ReconciliationEngine, detect_drift


@dataclass(slots=True)
class PilotHost:
    host_id: str
    role: str
    runtime: MutableHost
    online: bool = True
    degraded: bool = False
    last_heartbeat: datetime | None = None


@dataclass(slots=True)
class PilotSimulator:
    now: datetime
    policy_store: VersionedPolicyStore = field(default_factory=VersionedPolicyStore)
    policy_engine: PolicyEngine = field(default_factory=PolicyEngine)
    planner: Planner = field(default_factory=Planner)
    operation_engine: OperationEngine = field(default_factory=OperationEngine)
    hosts: dict[str, PilotHost] = field(default_factory=dict)
    audit: list[dict[str, Any]] = field(default_factory=list)
    reconciler: ReconciliationEngine = field(init=False)

    def __post_init__(self) -> None:
        self.reconciler = ReconciliationEngine(self.planner, self.operation_engine)

    def add_host(self, host_id: str, role: str, state: ActualState) -> None:
        if host_id in self.hosts:
            raise ValueError("duplicate host")
        self.hosts[host_id] = PilotHost(host_id, role, MutableHost(state))

    def heartbeat(self, host_id: str) -> None:
        host = self.hosts[host_id]
        if not host.online:
            raise ConnectionError("host offline")
        host.last_heartbeat = self.now
        self.audit.append(
            {
                "event": "heartbeat",
                "hostId": host_id,
                "at": self.now.isoformat(),
                "degraded": host.degraded,
            }
        )

    def advance(self, seconds: int) -> None:
        self.now += timedelta(seconds=seconds)

    def freshness(self, host_id: str, stale: int = 10, offline: int = 30) -> str:
        heartbeat = self.hosts[host_id].last_heartbeat
        if heartbeat is None:
            return "UNKNOWN"
        age = (self.now - heartbeat).total_seconds()
        if age >= offline:
            return "OFFLINE"
        if age >= stale:
            return "STALE"
        return "ONLINE"

    def apply_policy(
        self,
        host_id: str,
        policy: dict[str, Any],
        *,
        schedules: tuple[ScheduleRule, ...] = (),
        maintenance: PolicyDecision | None = None,
        manual_override: PolicyDecision | None = None,
        emergency: PolicyDecision | None = None,
        safety: PolicyDecision | None = None,
    ) -> str:
        result = self.policy_store.accept(host_id, policy)
        if result not in {"ACCEPTED", "DUPLICATE"}:
            self.audit.append(
                {"event": "policy_rejected", "hostId": host_id, "result": result}
            )
            return result

        effective = self.policy_engine.evaluate(
            host_id=host_id,
            now=self.now,
            policy=policy,
            schedules=schedules,
            maintenance=maintenance,
            manual_override=manual_override,
            emergency=emergency,
            safety=safety,
        )
        host = self.hosts[host_id]
        before = detect_drift(effective, host.runtime.state)
        operation = self.reconciler.reconcile(desired=effective, host=host.runtime)
        after = detect_drift(effective, host.runtime.state)
        self.audit.append(
            {
                "event": "reconcile",
                "hostId": host_id,
                "policyRevision": effective.policy_revision,
                "beforeDrift": before.drifted_fields,
                "afterDrift": after.drifted_fields,
                "stage": operation.stage.value,
            }
        )
        return operation.stage.value
