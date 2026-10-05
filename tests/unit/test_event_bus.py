from __future__ import annotations

from datetime import UTC, datetime

from mtp6coopnw.api.events import format_sse
from mtp6coopnw.contracts import OperationStage
from mtp6coopnw.observability import InMemoryEventBus
from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.policy import PolicyEngine

NOW = datetime(2026, 10, 4, 15, 0, tzinfo=UTC)
POLICY = {
    "policy_revision": 1,
    "host": {"enabled": True},
    "internet": {"allowed": False},
    "database": {"allowed": True},
    "ports": {"managed": [1433]},
}


def test_event_bus_sequences_and_replays_deltas() -> None:
    bus = InMemoryEventBus(retention=4)
    first = bus.publish(
        "host.status_changed",
        timestamp=NOW,
        source="core",
        host_id="CLIENT-01",
        data={"from": "ONLINE", "to": "STALE"},
    )
    second = bus.publish(
        "alarm.raised",
        timestamp=NOW,
        source="core",
        host_id="CLIENT-01",
        data={"code": "AGENT_STALE"},
    )

    assert first.sequence == 1
    assert second.sequence == 2
    batch = bus.read(after_sequence=1)
    assert [event.event_type for event in batch.events] == ["alarm.raised"]
    assert batch.latest_sequence == 2
    assert batch.resync_required is False


def test_event_bus_detects_replay_gap_after_retention_rollover() -> None:
    bus = InMemoryEventBus(retention=2)
    for index in range(3):
        bus.publish(
            "test.event",
            timestamp=NOW,
            source="test",
            data={"index": index},
        )

    batch = bus.read(after_sequence=0)

    assert batch.resync_required is True
    assert [event.sequence for event in batch.events] == [2, 3]


def test_wait_returns_immediately_when_event_already_available() -> None:
    bus = InMemoryEventBus()
    bus.publish("ready", timestamp=NOW, source="test")

    batch = bus.wait(after_sequence=0, timeout_seconds=0.01)

    assert len(batch.events) == 1
    assert batch.events[0].event_type == "ready"


def test_sse_frame_contains_sequence_type_and_payload() -> None:
    bus = InMemoryEventBus()
    event = bus.publish(
        "host.telemetry_updated",
        timestamp=NOW,
        source="core",
        host_id="CLIENT-01",
    )

    frame = format_sse(event)

    assert "id: 1\n" in frame
    assert "event: host.telemetry_updated\n" in frame
    assert '"hostId":"CLIENT-01"' in frame


def test_operation_engine_publishes_stage_events() -> None:
    bus = InMemoryEventBus()
    desired = PolicyEngine().evaluate(
        host_id="CLIENT-01",
        now=NOW,
        policy=POLICY,
    )
    host = MutableHost(ActualState(True, True, True, (1433,)))
    plan = Planner().plan(desired=desired, actual=host.state)

    result = OperationEngine(event_publisher=bus).execute(
        plan=plan,
        host=host,
        now=NOW,
    )

    assert result.stage is OperationStage.COMPLETED
    stages = [
        event.data["stage"]
        for event in bus.read().events
        if event.event_type == "operation.stage_changed"
    ]
    assert stages == [
        "REQUESTED",
        "VALIDATING",
        "PLANNING",
        "APPLYING",
        "VERIFYING",
        "COMPLETED",
    ]
