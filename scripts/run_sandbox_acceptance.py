from __future__ import annotations

import json
from datetime import UTC, datetime

from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.pilot import PilotSimulator
from mtp6coopnw.policy import PolicyDecision, PolicyEngine, VersionedPolicyStore
from mtp6coopnw.reconciliation import ReconciliationEngine, detect_drift

NOW = datetime(2026, 10, 5, 1, 0, tzinfo=UTC)
BASE = {
    "policy_revision": 1,
    "host": {"enabled": True},
    "internet": {"allowed": True},
    "database": {"allowed": True},
    "ports": {"managed": [1433]},
}


def run() -> dict[str, object]:
    checks: dict[str, bool] = {}
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
    checks["six_hosts_online"] = all(
        simulator.freshness(host_id) == "ONLINE" for host_id in simulator.hosts
    )
    simulator.advance(30)
    checks["site_outage_offline"] = all(
        simulator.freshness(host_id) == "OFFLINE" for host_id in simulator.hosts
    )

    policy_v2 = {**BASE, "policy_revision": 2, "internet": {"allowed": False}}
    checks["client_reconcile"] = (
        simulator.apply_policy("CLIENT-01", policy_v2) == "COMPLETED"
    )
    maintenance = PolicyDecision(
        "maintenance",
        30,
        internet_allowed=True,
        database_allowed=True,
    )
    checks["db_maintenance"] = (
        simulator.apply_policy(
            "DB-SERVER",
            policy_v2,
            maintenance=maintenance,
        )
        == "COMPLETED"
    )

    store = VersionedPolicyStore()
    checks["revision_accept"] = store.accept("C", BASE) == "ACCEPTED"
    checks["revision_duplicate"] = store.accept("C", BASE) == "DUPLICATE"
    checks["revision_conflict"] = (
        store.accept("C", {**BASE, "internet": {"allowed": False}}) == "CONFLICT"
    )

    engine = PolicyEngine()
    desired = engine.evaluate(host_id="ROLLBACK", now=NOW, policy=policy_v2)
    before = ActualState(True, True, True, (1433,))
    host = MutableHost(before, fail_verification=True)
    plan = Planner().plan(desired=desired, actual=host.state)
    result = OperationEngine().execute(plan=plan, host=host, now=NOW)
    checks["rollback_on_verify_failure"] = result.rolled_back and host.state == before

    reconciled_host = MutableHost(ActualState(True, True, True, (1433,)))
    result = ReconciliationEngine(Planner(), OperationEngine()).reconcile(
        desired=desired,
        host=reconciled_host,
    )
    checks["drift_reconciled"] = (
        result.stage.value == "COMPLETED"
        and detect_drift(desired, reconciled_host.state).in_sync
    )

    passed = sum(checks.values())
    return {
        "suite": "MTP6CoopNW sandbox acceptance",
        "passed": passed,
        "total": len(checks),
        "success": passed == len(checks),
        "checks": checks,
    }


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["success"] else 1)
