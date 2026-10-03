from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.observability import EventRecord, MetricRegistry
from mtp6coopnw.testing.fakes import (
    FakeClock,
    FakeFirewallAdapter,
    FakeNetworkAdapter,
    FakeServiceAdapter,
    FakeSqlAdapter,
    FakeTransport,
    InMemoryAuditStore,
    InMemoryPolicyStore,
)


@dataclass(slots=True)
class SimulatedHost:
    host_id: str
    role: str
    network: FakeNetworkAdapter = field(default_factory=FakeNetworkAdapter)
    firewall: FakeFirewallAdapter = field(default_factory=FakeFirewallAdapter)
    sql: FakeSqlAdapter = field(default_factory=FakeSqlAdapter)
    services: FakeServiceAdapter = field(default_factory=FakeServiceAdapter)
    online: bool = True
    last_heartbeat: datetime | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "role": self.role,
            "online": self.online,
            "last_heartbeat": self.last_heartbeat,
            "network": self.network.get_state(),
            "firewall": self.firewall.get_state(),
            "sql": self.sql.get_state(),
            "services": self.services.get_state(),
        }


@dataclass(slots=True)
class SimulationRuntime:
    clock: FakeClock
    policy_store: InMemoryPolicyStore = field(default_factory=InMemoryPolicyStore)
    audit_store: InMemoryAuditStore = field(default_factory=InMemoryAuditStore)
    transport: FakeTransport = field(default_factory=FakeTransport)
    metrics: MetricRegistry = field(default_factory=MetricRegistry)
    events: list[EventRecord] = field(default_factory=list)
    hosts: dict[str, SimulatedHost] = field(default_factory=dict)

    def add_host(self, host: SimulatedHost) -> None:
        if host.host_id in self.hosts:
            raise ValueError(f"Host already exists: {host.host_id}")
        self.hosts[host.host_id] = host

    def heartbeat(self, host_id: str) -> dict[str, Any]:
        host = self.hosts[host_id]
        if not host.online:
            raise ConnectionError(f"Host is offline: {host_id}")

        now = self.clock.now()
        host.last_heartbeat = now
        event = EventRecord(
            event="agent.heartbeat",
            timestamp=now,
            component="simulation",
            host_id=host_id,
            result="SUCCESS",
        )
        self._record(event)
        self.metrics.increment("agent.heartbeat.count")
        return host.snapshot()

    def apply_access(
        self,
        host_id: str,
        *,
        internet_allowed: bool | None = None,
        database_allowed: bool | None = None,
        allowed_ports: set[int] | None = None,
    ) -> dict[str, Any]:
        host = self.hosts[host_id]
        if not host.online:
            raise ConnectionError(f"Host is offline: {host_id}")

        before = host.firewall.get_state()
        host.firewall.apply_access(
            internet_allowed=internet_allowed,
            database_allowed=database_allowed,
            allowed_ports=allowed_ports,
        )
        after = host.firewall.get_state()

        event = EventRecord(
            event="simulation.access_applied",
            timestamp=self.clock.now(),
            component="simulation",
            host_id=host_id,
            operation="ApplyAccess",
            result="SUCCESS",
            data={"before": before, "after": after},
        )
        self._record(event)
        self.metrics.increment("simulation.access_applied.count")
        return host.snapshot()

    def set_sql_reachable(self, host_id: str, reachable: bool) -> None:
        self.hosts[host_id].sql.reachable = reachable

    def set_host_online(self, host_id: str, online: bool) -> None:
        self.hosts[host_id].online = online

    def _record(self, event: EventRecord) -> None:
        payload = event.to_dict()
        self.events.append(event)
        self.audit_store.append(payload)
        self.transport.send("CORE", payload)
