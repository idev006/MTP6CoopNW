from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from mtp6coopnw.testing import FakeClock, SimulatedHost, SimulationRuntime

NOW = datetime(2026, 10, 3, 7, 0, tzinfo=UTC)


@pytest.fixture
def runtime() -> SimulationRuntime:
    env = SimulationRuntime(clock=FakeClock(NOW))
    env.add_host(SimulatedHost(host_id="CLIENT-01", role="client"))
    env.add_host(SimulatedHost(host_id="DB-SERVER", role="database_server"))
    return env


@pytest.mark.scenario
def test_heartbeat_updates_state_and_transport(runtime: SimulationRuntime) -> None:
    snapshot = runtime.heartbeat("CLIENT-01")

    assert snapshot["online"] is True
    assert snapshot["last_heartbeat"] == NOW
    assert runtime.audit_store.events[-1]["event"] == "agent.heartbeat"
    assert runtime.transport.sent[-1][0] == "CORE"


@pytest.mark.scenario
def test_access_policy_can_be_simulated_without_windows(runtime: SimulationRuntime) -> None:
    snapshot = runtime.apply_access(
        "CLIENT-01",
        internet_allowed=False,
        database_allowed=True,
        allowed_ports={1433},
    )

    firewall = snapshot["firewall"]
    assert firewall["internet_allowed"] is False
    assert firewall["database_allowed"] is True
    assert firewall["allowed_ports"] == [1433]


@pytest.mark.scenario
def test_database_outage_is_observable(runtime: SimulationRuntime) -> None:
    runtime.set_sql_reachable("DB-SERVER", False)

    snapshot = runtime.hosts["DB-SERVER"].snapshot()
    assert snapshot["sql"]["reachable"] is False


@pytest.mark.scenario
def test_offline_host_rejects_heartbeat(runtime: SimulationRuntime) -> None:
    runtime.set_host_online("CLIENT-01", False)

    with pytest.raises(ConnectionError, match="offline"):
        runtime.heartbeat("CLIENT-01")


@pytest.mark.scenario
def test_fake_clock_advances_deterministically(runtime: SimulationRuntime) -> None:
    runtime.clock.advance(timedelta(seconds=5))
    assert runtime.clock.now() == NOW + timedelta(seconds=5)


@pytest.mark.scenario
def test_policy_store_uses_copy_semantics(runtime: SimulationRuntime) -> None:
    policy = {"revision": 2, "internet": {"allowed": False}}
    runtime.policy_store.save("CLIENT-01", policy)

    loaded = runtime.policy_store.get("CLIENT-01")
    assert loaded is not None
    loaded["internet"]["allowed"] = True

    stored = runtime.policy_store.get("CLIENT-01")
    assert stored is not None
    assert stored["internet"]["allowed"] is False
