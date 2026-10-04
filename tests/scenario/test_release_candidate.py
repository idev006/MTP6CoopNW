from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

import pytest

from mtp6coopnw.contracts import HostState, OperationStage
from mtp6coopnw.operations import (
    ActualState,
    MutableHost,
    OperationEngine,
    Planner,
    PlanningError,
    StateContext,
    resolve_host_state,
)
from mtp6coopnw.pilot import PilotSimulator
from mtp6coopnw.policy import (
    PolicyConflictError,
    PolicyDecision,
    PolicyEngine,
    ScheduleRule,
    VersionedPolicyStore,
)
from mtp6coopnw.reconciliation import ReconciliationEngine, detect_drift

NOW = datetime(2026, 10, 5, 1, 0, tzinfo=UTC)
BASE = {
    "policy_revision": 1,
    "host": {"enabled": True},
    "internet": {"allowed": True},
    "database": {"allowed": True},
    "ports": {"managed": [1433]},
}


def _desired(internet_allowed: bool) -> object:
    return PolicyEngine().evaluate(
        host_id="CLIENT-01",
        now=NOW,
        policy={
            **BASE,
            "internet": {"allowed": internet_allowed},
        },
    )


def test_schedule_exact_boundaries_and_overnight() -> None:
    office = ScheduleRule(
        "office",
        ("mon",),
        time(8, 0),
        time(17, 0),
        "Asia/Bangkok",
        internet_allowed=False,
    )
    assert office.active(NOW)
    assert not office.active(NOW - timedelta(seconds=1))
    assert not office.active(NOW + timedelta(hours=9))

    overnight = ScheduleRule(
        "overnight",
        ("mon",),
        time(22, 0),
        time(6, 0),
        "Asia/Bangkok",
        internet_allowed=False,
    )
    assert overnight.active(datetime(2026, 10, 5, 16, 0, tzinfo=UTC))
    assert overnight.active(datetime(2026, 10, 5, 22, 0, tzinfo=UTC))


def test_policy_priority_and_conflict() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        host_id="CLIENT-01",
        now=NOW,
        policy=BASE,
        emergency=PolicyDecision("emergency", 50, internet_allowed=True),
        safety=PolicyDecision("safety", 60, internet_allowed=False),
    )
    assert result.internet_allowed is False

    with pytest.raises(PolicyConflictError):
        engine.evaluate(
            host_id="CLIENT-01",
            now=NOW,
            policy=BASE,
            maintenance=PolicyDecision("a", 30, internet_allowed=True),
            manual_override=PolicyDecision("b", 30, internet_allowed=False),
        )


def test_policy_revision_replay_rules() -> None:
    store = VersionedPolicyStore()
    assert store.accept("CLIENT-01", BASE) == "ACCEPTED"
    assert store.accept("CLIENT-01", BASE) == "DUPLICATE"
    conflict = {**BASE, "internet": {"allowed": False}}
    assert store.accept("CLIENT-01", conflict) == "CONFLICT"
    newer = {**BASE, "policy_revision": 2}
    assert store.accept("CLIENT-01", newer) == "ACCEPTED"
    assert store.accept("CLIENT-01", BASE) == "STALE"


def test_planner_interlock_and_safe_fields() -> None:
    desired = _desired(False)
    with pytest.raises(PlanningError):
        Planner().plan(
            desired=desired,
            actual=ActualState(
                True,
                True,
                True,
                (1433,),
                control_reachable=False,
            ),
        )

    plan = Planner().plan(
        desired=desired,
        actual=ActualState(True, True, True, (1433,)),
    )
    assert {change.field for change in plan.changes} <= {
        "host_enabled",
        "internet_allowed",
        "database_allowed",
        "allowed_ports",
    }


def test_apply_verify_and_rollback() -> None:
    desired = _desired(False)
    before = ActualState(True, True, True, (1433,))
    host = MutableHost(before, fail_verification=True)
    plan = Planner().plan(desired=desired, actual=host.state)
    result = OperationEngine().execute(plan=plan, host=host, now=NOW)
    assert result.stage is OperationStage.ROLLED_BACK
    assert host.state == before


def test_operation_timeout_is_bounded() -> None:
    desired = _desired(False)
    host = MutableHost(ActualState(True, True, True, (1433,)))
    plan = Planner().plan(desired=desired, actual=host.state)
    result = OperationEngine(apply_timeout_seconds=5).execute(
        plan=plan,
        host=host,
        now=NOW,
        simulated_apply_seconds=6,
    )
    assert result.stage is OperationStage.TIMED_OUT


def test_reconciliation_removes_drift() -> None:
    desired = _desired(False)
    host = MutableHost(ActualState(True, True, True, (1433,)))
    assert not detect_drift(desired, host.state).in_sync
    result = ReconciliationEngine(Planner(), OperationEngine()).reconcile(
        desired=desired,
        host=host,
    )
    assert result.stage is OperationStage.COMPLETED
    assert detect_drift(desired, host.state).in_sync


def test_state_engine_priority() -> None:
    assert resolve_host_state(StateContext(False, True, True)) is HostState.OFFLINE
    assert resolve_host_state(StateContext(True, False, True)) is HostState.FAULT
    assert (
        resolve_host_state(StateContext(True, True, True, maintenance=True))
        is HostState.MAINTENANCE
    )
    assert resolve_host_state(StateContext(True, True, False)) is HostState.DISABLED
    assert resolve_host_state(StateContext(True, True, True)) is HostState.NORMAL


def test_six_host_site_outage_and_db_maintenance() -> None:
    simulator = PilotSimulator(NOW)
    simulator.add_host(
        "DB-SERVER",
        "database_server",
        ActualState(True, False, True, (1433,)),
    )
    for index in range(1, 6):
        simulator.add_host(
            f"CLIENT-{index:02d}",
            "client",
            ActualState(True, True, True, (1433,)),
        )
    for host_id in simulator.hosts:
        simulator.heartbeat(host_id)
    assert all(
        simulator.freshness(host_id) == "ONLINE" for host_id in simulator.hosts
    )

    maintenance = PolicyDecision(
        "maintenance",
        30,
        internet_allowed=True,
        database_allowed=True,
    )
    policy = {**BASE, "policy_revision": 2, "internet": {"allowed": False}}
    assert (
        simulator.apply_policy(
            "DB-SERVER",
            policy,
            maintenance=maintenance,
        )
        == "COMPLETED"
    )
    db_state = simulator.hosts["DB-SERVER"].runtime.state
    assert db_state.internet_allowed
    assert db_state.database_allowed
    assert db_state.lan_reachable

    simulator.advance(30)
    assert all(
        simulator.freshness(host_id) == "OFFLINE" for host_id in simulator.hosts
    )
