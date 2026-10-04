from __future__ import annotations

from datetime import UTC, datetime

import pytest

from mtp6coopnw.agent import AgentIdentity
from mtp6coopnw.composition import (
    AgentPorts,
    CoreCompositionSettings,
    compose_read_only_agent,
    compose_read_only_core,
)
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

NOW = datetime(2026, 10, 4, 14, 0, tzinfo=UTC)


def test_core_composition_exposes_facade_without_ui_dependency() -> None:
    clock = FakeClock(NOW)
    audit = InMemoryAuditStore()
    facade = compose_read_only_core(
        settings=CoreCompositionSettings(
            stale_after_seconds=10,
            offline_after_seconds=30,
        ),
        clock=clock,
        audit_store=audit,
    )

    facade.register_host("CLIENT-01", "client")
    status = facade.system_status()

    assert status["summary"]["hostCount"] == 1
    assert status["alarms"][0]["code"] == "AGENT_NEVER_SEEN"


def test_core_composition_rejects_invalid_freshness_thresholds() -> None:
    with pytest.raises(ValueError, match="greater than"):
        CoreCompositionSettings(stale_after_seconds=10, offline_after_seconds=10)


def test_agent_composition_accepts_replaceable_fake_ports() -> None:
    clock = FakeClock(NOW)
    transport = FakeTransport()
    policies = InMemoryPolicyStore()
    policies.save("CLIENT-01", {"policy_revision": 12})

    agent = compose_read_only_agent(
        identity=AgentIdentity(
            host_id="CLIENT-01",
            role="client",
            version="0.1.0.dev0",
        ),
        clock=clock,
        ports=AgentPorts(
            network=FakeNetworkAdapter(),
            firewall=FakeFirewallAdapter(allowed_ports={1433}),
            sql=FakeSqlAdapter(),
            services=FakeServiceAdapter(),
            policy_store=policies,
            audit_store=InMemoryAuditStore(),
            transport=transport,
        ),
    )

    snapshot = agent.run_once()

    assert snapshot.healthy is True
    assert snapshot.policy_revision == 12
    assert transport.sent[-1][1]["event"] == "agent.heartbeat"


def test_agent_composition_can_swap_one_port_without_engine_change() -> None:
    clock = FakeClock(NOW)
    transport = FakeTransport()
    network = FakeNetworkAdapter(lan_reachable=False, internet_reachable=False)

    agent = compose_read_only_agent(
        identity=AgentIdentity(
            host_id="CLIENT-02",
            role="client",
            version="0.1.0.dev0",
        ),
        clock=clock,
        ports=AgentPorts(
            network=network,
            firewall=FakeFirewallAdapter(),
            sql=FakeSqlAdapter(),
            services=FakeServiceAdapter(),
            policy_store=InMemoryPolicyStore(),
            audit_store=InMemoryAuditStore(),
            transport=transport,
        ),
    )

    snapshot = agent.run_once()

    assert snapshot.network["lan_reachable"] is False
    assert snapshot.network["internet_reachable"] is False
    assert transport.sent[-1][1]["data"]["snapshot"]["network"] == snapshot.network
