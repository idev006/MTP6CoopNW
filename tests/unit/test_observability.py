from __future__ import annotations

import io
import json
import logging
from datetime import UTC, datetime, timedelta

import pytest

from mtp6coopnw.contracts import HealthState
from mtp6coopnw.observability import (
    AuditEvent,
    EventRecord,
    FreshnessState,
    HealthReport,
    MetricRegistry,
    classify_freshness,
    create_logger,
    redact_mapping,
)


NOW = datetime(2026, 10, 3, 8, 0, tzinfo=UTC)


def test_redaction_is_recursive() -> None:
    value = {
        "username": "operator",
        "password": "secret-value",
        "nested": {"token": "abc", "safe": "ok"},
        "items": [{"api_key": "xyz"}],
    }

    redacted = redact_mapping(value)

    assert redacted["username"] == "operator"
    assert redacted["password"] == "***REDACTED***"
    assert redacted["nested"]["token"] == "***REDACTED***"
    assert redacted["nested"]["safe"] == "ok"
    assert redacted["items"][0]["api_key"] == "***REDACTED***"


def test_structured_logger_outputs_json_and_redacts_secret() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = create_logger("mtp6-test-structured", handler)

    event = EventRecord(
        event="policy.received",
        timestamp=NOW,
        component="agent",
        host_id="CLIENT-01",
        data={"password": "do-not-log", "revision": 9},
    )
    logger.emit(event)

    payload = json.loads(stream.getvalue())
    assert payload["event"] == "policy.received"
    assert payload["hostId"] == "CLIENT-01"
    assert payload["data"]["password"] == "***REDACTED***"
    assert payload["data"]["revision"] == 9


@pytest.mark.parametrize(
    ("age_seconds", "expected"),
    [
        (0, FreshnessState.ONLINE),
        (9, FreshnessState.ONLINE),
        (10, FreshnessState.STALE),
        (29, FreshnessState.STALE),
        (30, FreshnessState.OFFLINE),
    ],
)
def test_freshness_thresholds(age_seconds: int, expected: FreshnessState) -> None:
    state = classify_freshness(
        now=NOW,
        last_heartbeat=NOW - timedelta(seconds=age_seconds),
        stale_after_seconds=10,
        offline_after_seconds=30,
    )
    assert state is expected


def test_freshness_without_heartbeat_is_unknown() -> None:
    assert (
        classify_freshness(
            now=NOW,
            last_heartbeat=None,
            stale_after_seconds=10,
            offline_after_seconds=30,
        )
        is FreshnessState.UNKNOWN
    )


def test_metric_registry_tracks_counter_and_gauge() -> None:
    metrics = MetricRegistry()
    metrics.increment("heartbeat.count")
    metrics.increment("heartbeat.count", 2)
    metrics.set_gauge("agent.online", 5)

    snapshot = metrics.snapshot()
    assert snapshot["counters"]["heartbeat.count"] == 3
    assert snapshot["gauges"]["agent.online"] == 5


def test_health_and_audit_models_are_serializable() -> None:
    report = HealthReport(
        component="core",
        state=HealthState.HEALTHY,
        checked_at=NOW,
        message="ready",
    )
    event = AuditEvent(
        event="policy.applied",
        actor="operator",
        target="CLIENT-01",
        timestamp=NOW,
        result="SUCCESS",
    )

    assert report.state is HealthState.HEALTHY
    assert event.to_dict()["result"] == "SUCCESS"
