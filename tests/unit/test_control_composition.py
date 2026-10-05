from __future__ import annotations

from datetime import UTC, datetime, timedelta

from mtp6coopnw.composition import ManagedHostSpec, compose_control_runtime
from mtp6coopnw.operations import ActualState
from mtp6coopnw.security import ActorContext, Role
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore

NOW = datetime(2026, 10, 4, 9, 0, tzinfo=UTC)


def _runtime():
    return compose_control_runtime(
        stale_after_seconds=10,
        offline_after_seconds=30,
        clock=FakeClock(NOW),
        audit_store=InMemoryAuditStore(),
        managed_hosts=(
            ManagedHostSpec(
                host_id="CLIENT-01",
                role="client",
                state=ActualState(
                    host_enabled=True,
                    internet_allowed=True,
                    database_allowed=True,
                    allowed_ports=(1433, 443),
                ),
            ),
        ),
    )


def test_composition_root_builds_complete_headless_ui_path() -> None:
    runtime = _runtime()

    model = runtime.presenter.load()

    host = model.hosts["CLIENT-01"]
    assert host.freshness == "ONLINE"
    assert host.health == "HEALTHY"
    assert host.control["internetAllowed"] is True
    assert host.actions["canApply"] is True


def test_composition_root_command_returns_to_presenter_through_events() -> None:
    runtime = _runtime()
    runtime.presenter.load()

    result = runtime.commands.set_internet_allowed(
        actor=ActorContext("operator-1", Role.OPERATOR),
        host_id="CLIENT-01",
        allowed=False,
        now=NOW + timedelta(seconds=1),
    )
    model = runtime.presenter.refresh_from_events()

    assert result["stage"] == "COMPLETED"
    assert runtime.hosts["CLIENT-01"].state.internet_allowed is False
    assert model.hosts["CLIENT-01"].control["internetAllowed"] is False
    assert model.operation_stages[result["operationId"]] == "COMPLETED"
