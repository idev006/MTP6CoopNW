from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.adapters import (
    AuditStore,
    ClockPort,
    FirewallPort,
    NetworkPort,
    PolicyStore,
    ServicePort,
    SqlPort,
    TransportPort,
)
from mtp6coopnw.observability import EventRecord, MetricRegistry


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    host_id: str
    role: str
    version: str


@dataclass(frozen=True, slots=True)
class AgentSnapshot:
    host_id: str
    role: str
    captured_at: datetime
    policy_revision: int | None
    network: dict[str, Any]
    firewall: dict[str, Any]
    sql: dict[str, Any]
    services: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def healthy(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostId": self.host_id,
            "role": self.role,
            "capturedAt": self.captured_at.isoformat(),
            "policyRevision": self.policy_revision,
            "network": self.network,
            "firewall": self.firewall,
            "sql": self.sql,
            "services": self.services,
            "healthy": self.healthy,
            "errors": list(self.errors),
        }


@dataclass(slots=True)
class ReadOnlyAgent:
    identity: AgentIdentity
    clock: ClockPort
    network: NetworkPort
    firewall: FirewallPort
    sql: SqlPort
    services: ServicePort
    policy_store: PolicyStore
    audit_store: AuditStore
    transport: TransportPort
    metrics: MetricRegistry = field(default_factory=MetricRegistry)

    def self_test(self) -> AgentSnapshot:
        return self.collect_status()

    def collect_status(self) -> AgentSnapshot:
        errors: list[str] = []
        network = self._read_adapter("network", self.network.get_state, errors)
        firewall = self._read_adapter("firewall", self.firewall.get_state, errors)
        sql = self._read_adapter("sql", self.sql.get_state, errors)
        services = self._read_adapter("services", self.services.get_state, errors)

        policy = self.policy_store.get(self.identity.host_id)
        revision = _policy_revision(policy)

        snapshot = AgentSnapshot(
            host_id=self.identity.host_id,
            role=self.identity.role,
            captured_at=self.clock.now(),
            policy_revision=revision,
            network=network,
            firewall=firewall,
            sql=sql,
            services=services,
            errors=tuple(errors),
        )
        self.metrics.increment("agent.status.collect.count")
        if errors:
            self.metrics.increment("agent.status.collect.error.count")
        return snapshot

    def heartbeat(self) -> AgentSnapshot:
        snapshot = self.collect_status()
        event = EventRecord(
            event="agent.heartbeat",
            timestamp=self.clock.now(),
            component="agent",
            host_id=self.identity.host_id,
            policy_revision=snapshot.policy_revision,
            result="SUCCESS" if snapshot.healthy else "DEGRADED",
            data={"snapshot": snapshot.to_dict(), "agentVersion": self.identity.version},
        )
        payload = event.to_dict()
        self.transport.send("CORE", payload)
        self.audit_store.append(payload)
        self.metrics.increment("agent.heartbeat.count")
        return snapshot

    def reconcile_read_only(self) -> AgentSnapshot:
        snapshot = self.collect_status()
        event = EventRecord(
            event="reconcile.completed",
            timestamp=self.clock.now(),
            component="agent",
            host_id=self.identity.host_id,
            policy_revision=snapshot.policy_revision,
            result="READ_ONLY",
            data={"snapshot": snapshot.to_dict()},
        )
        payload = event.to_dict()
        self.audit_store.append(payload)
        self.metrics.increment("agent.reconcile.read_only.count")
        return snapshot

    def run_once(self) -> AgentSnapshot:
        snapshot = self.reconcile_read_only()
        return self.heartbeat() if snapshot.healthy else snapshot

    def _read_adapter(
        self,
        name: str,
        reader: Any,
        errors: list[str],
    ) -> dict[str, Any]:
        try:
            value = reader()
        except Exception as exc:
            errors.append(f"{name}:{type(exc).__name__}")
            return {"error": type(exc).__name__}

        if not isinstance(value, dict):
            errors.append(f"{name}:InvalidResult")
            return {"error": "InvalidResult"}
        return value


def _policy_revision(policy: dict[str, Any] | None) -> int | None:
    if not policy:
        return None
    value = policy.get("policy_revision", policy.get("revision"))
    return value if isinstance(value, int) and not isinstance(value, bool) else None
