from __future__ import annotations

from datetime import UTC, datetime

from mtp6coopnw.api import ReadOnlyControlFacade, UiApplicationFacade, UiEventGateway
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import InMemoryEventBus
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore

NOW = datetime(2026, 10, 4, 15, 0, tzinfo=UTC)


def test_ui_facade_returns_presentation_ready_host_cards() -> None:
    clock = FakeClock(NOW)
    bus = InMemoryEventBus()
    core = ControlCore(
        clock=clock,
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
        event_publisher=bus,
    )
    core.register_host("CLIENT-01", "client")
    core.ingest(
        {
            "event": "agent.heartbeat",
            "timestamp": NOW.isoformat(),
            "component": "agent",
            "data": {
                "snapshot": {
                    "hostId": "CLIENT-01",
                    "role": "client",
                    "healthy": True,
                    "policyRevision": 7,
                    "control": {
                        "hostEnabled": True,
                        "internetAllowed": False,
                        "databaseAllowed": True,
                        "allowedPorts": [1433],
                    },
                }
            },
        }
    )
    status = ReadOnlyControlFacade(core)
    gateway = UiEventGateway(status, bus)
    facade = UiApplicationFacade(status, gateway)

    payload = facade.bootstrap_dashboard()
    card = payload["hosts"][0]

    assert card["hostId"] == "CLIENT-01"
    assert card["health"] == "HEALTHY"
    assert card["policyRevision"] == 7
    assert card["control"]["internetAllowed"] is False
    assert card["control"]["allowedPorts"] == [1433]
    assert card["actions"]["canApply"] is True
    assert payload["latestSequence"] == bus.latest_sequence


def test_unknown_health_fails_closed_for_apply_actions() -> None:
    clock = FakeClock(NOW)
    bus = InMemoryEventBus()
    core = ControlCore(
        clock=clock,
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
        event_publisher=bus,
    )
    core.register_host("CLIENT-01", "client")
    core.ingest(
        {
            "event": "agent.heartbeat",
            "timestamp": NOW.isoformat(),
            "component": "agent",
            "data": {
                "snapshot": {
                    "hostId": "CLIENT-01",
                    "role": "client",
                    "policyRevision": 7,
                }
            },
        }
    )
    status = ReadOnlyControlFacade(core)
    facade = UiApplicationFacade(status, UiEventGateway(status, bus))

    card = facade.bootstrap_dashboard()["hosts"][0]

    assert card["health"] == "UNKNOWN"
    assert card["actions"]["canApply"] is False
    assert card["actions"]["canPlan"] is False
