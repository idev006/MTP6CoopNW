from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from mtp6coopnw.core import (
    ControlCore,
    HostRegistry,
    PolicyRegistry,
    TelemetryIngestError,
)
from mtp6coopnw.observability import FreshnessState
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore

NOW = datetime(2026, 10, 3, 10, 30, tzinfo=UTC)


def _core() -> ControlCore:
    return ControlCore(
        clock=FakeClock(NOW),
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
    )


def _heartbeat(
    *,
    timestamp: datetime = NOW,
    host_id: str = "CLIENT-01",
    role: str = "client",
    policy_revision: int = 5,
    healthy: bool | None = True,
) -> dict[str, object]:
    snapshot: dict[str, object] = {
        "hostId": host_id,
        "role": role,
        "capturedAt": timestamp.isoformat(),
        "policyRevision": policy_revision,
    }
    if healthy is not None:
        snapshot["healthy"] = healthy

    return {
        "event": "agent.heartbeat",
        "timestamp": timestamp.isoformat(),
        "data": {"snapshot": snapshot},
    }


def test_rejects_unknown_telemetry_event() -> None:
    core = _core()

    with pytest.raises(TelemetryIngestError, match="Unsupported event"):
        core.ingest({"event": "shell.command"})


def test_rejects_heartbeat_without_snapshot() -> None:
    core = _core()

    with pytest.raises(TelemetryIngestError, match="data.snapshot"):
        core.ingest(
            {
                "event": "agent.heartbeat",
                "timestamp": NOW.isoformat(),
                "data": {},
            }
        )


def test_rejects_unknown_host_role() -> None:
    core = _core()

    with pytest.raises(TelemetryIngestError, match="Unsupported host role"):
        core.ingest(_heartbeat(role="administrator"))


def test_degraded_agent_produces_central_alarm() -> None:
    core = _core()
    core.ingest(_heartbeat(healthy=False))

    alarms = core.list_alarms()

    assert len(alarms) == 1
    assert alarms[0].code == "AGENT_DEGRADED"


def test_freshness_uses_core_receipt_time_not_agent_clock() -> None:
    core = _core()
    future_agent_time = NOW + timedelta(hours=3)
    core.ingest(_heartbeat(timestamp=future_agent_time))

    assert core.host("CLIENT-01").freshness is FreshnessState.ONLINE
    assert core.host("CLIENT-01").last_heartbeat == NOW


def test_rejects_stale_heartbeat_without_regressing_snapshot() -> None:
    core = _core()
    newer = NOW + timedelta(seconds=5)
    core.ingest(_heartbeat(timestamp=newer, policy_revision=9))

    with pytest.raises(TelemetryIngestError, match="Stale heartbeat"):
        core.ingest(_heartbeat(timestamp=NOW, policy_revision=3))

    view = core.host("CLIENT-01")
    assert view.policy_revision == 9
    assert view.snapshot["policyRevision"] == 9


def test_duplicate_heartbeat_is_idempotent() -> None:
    core = _core()
    event = _heartbeat(policy_revision=7)

    core.ingest(event)
    core.ingest(event)

    assert core.host("CLIENT-01").policy_revision == 7


def test_same_timestamp_with_different_payload_is_rejected() -> None:
    core = _core()
    core.ingest(_heartbeat(policy_revision=7))

    with pytest.raises(TelemetryIngestError, match="Conflicting heartbeat"):
        core.ingest(_heartbeat(policy_revision=8))

    assert core.host("CLIENT-01").policy_revision == 7


def test_registered_but_never_seen_host_raises_alarm() -> None:
    core = _core()
    core.register_host("CLIENT-01", "client")

    alarms = core.list_alarms()

    assert [alarm.code for alarm in alarms] == ["AGENT_NEVER_SEEN"]


def test_missing_health_raises_unknown_health_alarm() -> None:
    core = _core()
    core.ingest(_heartbeat(healthy=None))

    alarms = core.list_alarms()

    assert [alarm.code for alarm in alarms] == ["AGENT_HEALTH_UNKNOWN"]
