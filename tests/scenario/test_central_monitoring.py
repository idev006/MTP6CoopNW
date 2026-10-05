from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from mtp6coopnw.agent import AgentIdentity, ReadOnlyAgent
from mtp6coopnw.api import ReadOnlyControlApi
from mtp6coopnw.cli.status import render_status
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import FreshnessState
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

pytestmark = pytest.mark.scenario

NOW = datetime(2026, 10, 3, 10, 0, tzinfo=UTC)


def _agent(host_id: str, role: str, clock: FakeClock) -> tuple[ReadOnlyAgent, FakeTransport]:
    transport = FakeTransport()
    policies = InMemoryPolicyStore()
    policies.save(host_id, {"policy_revision": 3})

    agent = ReadOnlyAgent(
        identity=AgentIdentity(host_id=host_id, role=role, version="0.1.0.dev0"),
        clock=clock,
        network=FakeNetworkAdapter(),
        firewall=FakeFirewallAdapter(),
        sql=FakeSqlAdapter(),
        services=FakeServiceAdapter(),
        policy_store=policies,
        audit_store=InMemoryAuditStore(),
        transport=transport,
    )
    return agent, transport


def _core(clock: FakeClock) -> ControlCore:
    return ControlCore(
        clock=clock,
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
    )


def _heartbeat_into_core(
    core: ControlCore,
    agent: ReadOnlyAgent,
    transport: FakeTransport,
) -> None:
    agent.heartbeat()
    _, payload = transport.sent[-1]
    core.ingest(payload)


def test_six_host_site_is_visible_from_one_central_api() -> None:
    clock = FakeClock(NOW)
    core = _core(clock)
    api = ReadOnlyControlApi(core)

    host_specs = [
        ("DB-SERVER", "database_server"),
        ("CLIENT-01", "client"),
        ("CLIENT-02", "client"),
        ("CLIENT-03", "client"),
        ("CLIENT-04", "client"),
        ("CLIENT-05", "client"),
    ]
    for host_id, role in host_specs:
        agent, transport = _agent(host_id, role, clock)
        _heartbeat_into_core(core, agent, transport)

    hosts = api.list_hosts()

    assert [host["hostId"] for host in hosts] == [
        "CLIENT-01",
        "CLIENT-02",
        "CLIENT-03",
        "CLIENT-04",
        "CLIENT-05",
        "DB-SERVER",
    ]
    assert all(host["freshness"] == "ONLINE" for host in hosts)
    assert all(host["policyRevision"] == 3 for host in hosts)


def test_central_freshness_changes_without_new_agent_message() -> None:
    clock = FakeClock(NOW)
    core = _core(clock)
    agent, transport = _agent("CLIENT-01", "client", clock)
    _heartbeat_into_core(core, agent, transport)

    assert core.host("CLIENT-01").freshness is FreshnessState.ONLINE

    clock.advance(timedelta(seconds=10))
    assert core.host("CLIENT-01").freshness is FreshnessState.STALE
    assert core.list_alarms()[0].code == "AGENT_STALE"

    clock.advance(timedelta(seconds=20))
    assert core.host("CLIENT-01").freshness is FreshnessState.OFFLINE
    assert core.list_alarms()[0].code == "AGENT_OFFLINE"


def test_central_console_renders_hosts_and_alarms() -> None:
    clock = FakeClock(NOW)
    core = _core(clock)
    api = ReadOnlyControlApi(core)
    agent, transport = _agent("CLIENT-01", "client", clock)
    _heartbeat_into_core(core, agent, transport)

    output = render_status(api)

    assert "MTP6CoopNW Central Status" in output
    assert "CLIENT-01 | client | ONLINE | HEALTHY | 3" in output

    clock.advance(timedelta(seconds=30))
    output = render_status(api)
    assert "AGENT_OFFLINE" in output


def test_policy_can_be_staged_centrally_without_enforcement() -> None:
    clock = FakeClock(NOW)
    core = _core(clock)
    core.register_host("CLIENT-01", "client")

    core.set_policy_read_only(
        "CLIENT-01",
        {"policy_revision": 4, "internet": {"allowed": False}},
    )

    policy = core.get_policy("CLIENT-01")
    assert policy is not None
    assert policy["policy_revision"] == 4
    assert policy["internet"]["allowed"] is False


def test_all_hosts_converge_offline_after_site_outage_timeout() -> None:
    clock = FakeClock(NOW)
    core = _core(clock)

    for index in range(1, 6):
        agent, transport = _agent(f"CLIENT-{index:02d}", "client", clock)
        _heartbeat_into_core(core, agent, transport)

    database, database_transport = _agent("DB-SERVER", "database_server", clock)
    _heartbeat_into_core(core, database, database_transport)

    clock.advance(timedelta(seconds=30))

    assert all(view.freshness is FreshnessState.OFFLINE for view in core.list_hosts())
    assert len(core.list_alarms()) == 6
    assert all(alarm.code == "AGENT_OFFLINE" for alarm in core.list_alarms())
