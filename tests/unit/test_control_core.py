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


def test_degraded_agent_produces_central_alarm() -> None:
    core = _core()
    core.ingest(
        {
            "event": "agent.heartbeat",
            "timestamp": NOW.isoformat(),
            "data": {
                "snapshot": {
                    "hostId": "CLIENT-01",
                    "role": "client",
                    "capturedAt": NOW.isoformat(),
                    "policyRevision": 5,
                    "healthy": False,
                }
            },
        }
    )

    alarms = core.list_alarms()

    assert len(alarms) == 1
    assert alarms[0].code == "AGENT_DEGRADED"


def test_freshness_uses_core_receipt_time_not_agent_clock() -> None:
    core = _core()
    future_agent_time = NOW + timedelta(hours=3)
    core.ingest(
        {
            "event": "agent.heartbeat",
            "timestamp": future_agent_time.isoformat(),
            "data": {
                "snapshot": {
                    "hostId": "CLIENT-01",
                    "role": "client",
                    "capturedAt": future_agent_time.isoformat(),
                    "healthy": True,
                }
            },
        }
    )

    assert core.host("CLIENT-01").freshness is FreshnessState.ONLINE
    assert core.host("CLIENT-01").last_heartbeat == NOW
