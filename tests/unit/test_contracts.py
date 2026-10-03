from __future__ import annotations

from datetime import UTC, datetime

from mtp6coopnw.contracts import (
    Alarm,
    AlarmSeverity,
    HealthState,
    HostState,
    HostStatus,
    MessageEnvelope,
    OperationStage,
    OperationStatus,
)

NOW = datetime(2026, 10, 3, 6, 0, tzinfo=UTC)


def test_host_status_keeps_state_stage_and_health_separate() -> None:
    operation = OperationStatus(
        operation_id="op-1",
        operation="SetInternetAccess",
        target="CLIENT-01",
        current_stage=OperationStage.VERIFYING,
        stage_started_at=NOW,
        correlation_id="corr-1",
    )
    alarm = Alarm(
        alarm_id="alarm-1",
        severity=AlarmSeverity.WARNING,
        code="POLICY_DRIFT",
        message="Desired state differs from actual state.",
        source="CLIENT-01",
        raised_at=NOW,
    )

    status = HostStatus(
        host_id="CLIENT-01",
        health=HealthState.DEGRADED,
        state=HostState.WARNING,
        online=True,
        last_heartbeat=NOW,
        policy_revision=7,
        alarms=(alarm,),
        last_operation=operation,
    )

    assert status.state is HostState.WARNING
    assert status.last_operation is not None
    assert status.last_operation.current_stage is OperationStage.VERIFYING
    assert status.health is HealthState.DEGRADED


def test_message_envelope_generates_correlation_id() -> None:
    first = MessageEnvelope(
        message_type="heartbeat",
        source="CLIENT-01",
        target="CORE",
        created_at=NOW,
    )
    second = MessageEnvelope(
        message_type="heartbeat",
        source="CLIENT-02",
        target="CORE",
        created_at=NOW,
    )

    assert first.schema_version == 1
    assert first.correlation_id != second.correlation_id
