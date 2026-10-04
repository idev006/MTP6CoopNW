from __future__ import annotations

from datetime import UTC, datetime

import pytest

from mtp6coopnw.api import ReadOnlyControlFacade, UiEventGateway
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import InMemoryEventBus
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore

pytestmark = pytest.mark.scenario

NOW = datetime(2026, 10, 4, 15, 0, tzinfo=UTC)


def _system() -> tuple[ControlCore, UiEventGateway, FakeClock]:
    clock = FakeClock(NOW)
    bus = InMemoryEventBus()
    core = ControlCore(
        clock=clock,
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
        event_publisher=bus,
    )
    facade = ReadOnlyControlFacade(core)
    return core, UiEventGateway(facade, bus), clock


def test_ui_bootstraps_snapshot_then_receives_only_changes() -> None:
    core, gateway, _ = _system()
    core.register_host("CLIENT-01", "client")

    bootstrap = gateway.bootstrap()
    sequence = bootstrap["latestSequence"]
    assert bootstrap["snapshot"]["summary"]["hostCount"] == 1

    core.set_policy_read_only("CLIENT-01", {"policy_revision": 1})
    delta = gateway.next_events(
        after_sequence=sequence,
        timeout_seconds=0,
    )

    assert delta["resyncRequired"] is False
    assert [event["eventType"] for event in delta["events"]] == ["policy.staged"]


def test_heartbeat_pushes_status_event_without_ui_status_polling() -> None:
    core, gateway, clock = _system()
    core.register_host("CLIENT-01", "client")
    baseline = gateway.bootstrap()["latestSequence"]

    heartbeat = {
        "event": "agent.heartbeat",
        "timestamp": clock.now().isoformat(),
        "component": "agent",
        "data": {
            "snapshot": {
                "hostId": "CLIENT-01",
                "role": "client",
                "healthy": True,
                "policyRevision": 1,
            }
        },
    }
    core.ingest(heartbeat)

    delta = gateway.next_events(after_sequence=baseline, timeout_seconds=0)
    assert any(
        event["eventType"] == "host.telemetry_updated"
        and event["hostId"] == "CLIENT-01"
        for event in delta["events"]
    )
