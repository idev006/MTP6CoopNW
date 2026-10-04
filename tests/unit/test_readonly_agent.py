from __future__ import annotations

from datetime import UTC, datetime

from mtp6coopnw.agent import AgentIdentity, ReadOnlyAgent
from mtp6coopnw.observability import MetricRegistry
from mtp6coopnw.testing import (
    FakeClock,
    FakeFirewallAdapter,
    FakeNetworkAdapter,
    FakeServiceAdapter,
    FakeSqlAdapter,
    FakeTransport,
    InMemoryAuditStore,
    InMemoryPolicyStore,
)

NOW = datetime(2026, 10, 3, 9, 0, tzinfo=UTC)


def _agent() -> tuple[
    ReadOnlyAgent,
    FakeTransport,
    InMemoryAuditStore,
    InMemoryPolicyStore,
]:
    transport = FakeTransport()
    audit = InMemoryAuditStore()
    policies = InMemoryPolicyStore()
    policies.save("CLIENT-01", {"policy_revision": 12})
    agent = ReadOnlyAgent(
        identity=AgentIdentity(
            host_id="CLIENT-01",
            role="client",
            version="0.1.0.dev0",
        ),
        clock=FakeClock(NOW),
        network=FakeNetworkAdapter(),
        firewall=FakeFirewallAdapter(allowed_ports={1433}),
        sql=FakeSqlAdapter(),
        services=FakeServiceAdapter(services={"MSSQLSERVER": "Running"}),
        policy_store=policies,
        audit_store=audit,
        transport=transport,
        metrics=MetricRegistry(),
    )
    return agent, transport, audit, policies


def test_heartbeat_reports_snapshot_and_policy_revision() -> None:
    agent, transport, audit, _ = _agent()

    snapshot = agent.heartbeat()

    assert snapshot.healthy is True
    assert snapshot.policy_revision == 12
    assert snapshot.firewall["allowed_ports"] == [1433]
    assert transport.sent[-1][0] == "CORE"
    assert transport.sent[-1][1]["event"] == "agent.heartbeat"
    assert audit.events[-1]["event"] == "agent.heartbeat"
    assert agent.metrics.counters["agent.heartbeat.count"] == 1


def test_read_only_reconcile_does_not_change_fake_adapter_state() -> None:
    agent, _, audit, _ = _agent()
    before = agent.firewall.get_state()

    snapshot = agent.reconcile_read_only()
    after = agent.firewall.get_state()

    assert snapshot.healthy is True
    assert before == after
    assert audit.events[-1]["result"] == "READ_ONLY"


class FailingSqlAdapter:
    def get_state(self) -> dict[str, object]:
        raise RuntimeError("simulated adapter failure")


def test_adapter_failure_produces_degraded_snapshot() -> None:
    agent, transport, _, _ = _agent()
    agent.sql = FailingSqlAdapter()

    snapshot = agent.heartbeat()

    assert snapshot.healthy is False
    assert "sql:RuntimeError" in snapshot.errors
    assert transport.sent[-1][1]["result"] == "DEGRADED"


def test_run_once_reports_healthy_snapshot() -> None:
    agent, transport, _, _ = _agent()

    snapshot = agent.run_once()

    assert snapshot.healthy is True
    assert transport.sent[-1][1]["event"] == "agent.heartbeat"
    assert transport.sent[-1][1]["result"] == "SUCCESS"
    assert transport.sent[-1][1]["data"]["snapshot"]["healthy"] is True


def test_run_once_reports_degraded_snapshot_when_adapter_fails() -> None:
    agent, transport, audit, _ = _agent()
    agent.sql = FailingSqlAdapter()

    snapshot = agent.run_once()

    assert snapshot.healthy is False
    assert "sql:RuntimeError" in snapshot.errors
    assert transport.sent[-1][1]["event"] == "agent.heartbeat"
    assert transport.sent[-1][1]["result"] == "DEGRADED"
    assert transport.sent[-1][1]["data"]["snapshot"]["healthy"] is False
    assert audit.events[-1]["event"] == "agent.heartbeat"
    assert agent.metrics.counters["agent.heartbeat.count"] == 1
