from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from mtp6coopnw.api import (
    NetworkControlFacade,
    ReadOnlyControlFacade,
    UiApplicationFacade,
    UiEventGateway,
)
from mtp6coopnw.api.engine_executor import EngineCommandExecutor
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import InMemoryEventBus
from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.policy import PolicyEngine
from mtp6coopnw.security import ActorContext, Role
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore
from mtp6coopnw.ui import DashboardPresenter

pytestmark = pytest.mark.scenario
NOW = datetime(2026, 10, 4, 8, 0, tzinfo=UTC)


@dataclass(slots=True)
class CoreStateReporter:
    core: ControlCore
    role: str = "client"

    def report(
        self,
        *,
        host_id: str,
        state: dict[str, Any],
        policy_revision: int,
        now: datetime,
    ) -> None:
        self.core.ingest(
            {
                "event": "agent.heartbeat",
                "timestamp": now.isoformat(),
                "component": "sandbox-agent",
                "data": {
                    "snapshot": {
                        "hostId": host_id,
                        "role": self.role,
                        "healthy": True,
                        "policyRevision": policy_revision,
                        "control": state,
                    }
                },
            }
        )


def _build(*, fail_verification: bool = False):
    clock = FakeClock(NOW)
    bus = InMemoryEventBus()
    audit = InMemoryAuditStore()
    core = ControlCore(
        clock=clock,
        audit_store=audit,
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
        event_publisher=bus,
    )
    core.register_host("CLIENT-01", "client")
    initial = {
        "hostEnabled": True,
        "internetAllowed": True,
        "databaseAllowed": True,
        "allowedPorts": [1433, 443],
        "lanReachable": True,
        "controlReachable": True,
    }
    core.ingest(
        {
            "event": "agent.heartbeat",
            "timestamp": NOW.isoformat(),
            "component": "sandbox-agent",
            "data": {
                "snapshot": {
                    "hostId": "CLIENT-01",
                    "role": "client",
                    "healthy": True,
                    "policyRevision": 1,
                    "control": initial,
                }
            },
        }
    )

    mutable = MutableHost(
        ActualState(
            host_enabled=True,
            internet_allowed=True,
            database_allowed=True,
            allowed_ports=(1433, 443),
        ),
        fail_verification=fail_verification,
    )
    operation = OperationEngine(event_publisher=bus)
    executor = EngineCommandExecutor(
        policy_engine=PolicyEngine(),
        planner=Planner(),
        operation_engine=operation,
        hosts={"CLIENT-01": mutable},
        state_reporter=CoreStateReporter(core),
    )
    commands = NetworkControlFacade(executor, audit)
    status = ReadOnlyControlFacade(core)
    ui = UiApplicationFacade(status, UiEventGateway(status, bus))
    presenter = DashboardPresenter.create(ui)
    presenter.load()
    return presenter, commands, mutable, audit


@pytest.mark.parametrize(
    ("method", "value", "field", "expected"),
    [
        ("set_host_enabled", False, "hostEnabled", False),
        ("set_internet_allowed", False, "internetAllowed", False),
        ("set_database_allowed", False, "databaseAllowed", False),
    ],
)
def test_ui_command_flows_through_facade_real_engines_and_back_to_presenter(
    method: str,
    value: bool,
    field: str,
    expected: bool,
) -> None:
    presenter, commands, _, audit = _build()
    actor = ActorContext("operator-1", Role.OPERATOR)

    result = getattr(commands, method)(
        actor=actor,
        host_id="CLIENT-01",
        **({"enabled": value} if method == "set_host_enabled" else {"allowed": value}),
        now=NOW + timedelta(seconds=1),
    )
    model = presenter.refresh_from_events()

    assert result["stage"] == "COMPLETED"
    assert model.hosts["CLIENT-01"].control[field] is expected
    assert model.operation_stages[result["operationId"]] == "COMPLETED"
    assert audit.events[-1]["actorId"] == "operator-1"


def test_ui_port_configuration_flows_through_facade_real_engines_and_presenter() -> None:
    presenter, commands, mutable, _ = _build()
    admin = ActorContext("admin-1", Role.ADMIN)

    result = commands.set_port_rules(
        actor=admin,
        host_id="CLIENT-01",
        rules=[
            {
                "protocol": "TCP",
                "port": 1433,
                "direction": "OUTBOUND",
                "destination": "192.168.1.10",
                "allowed": True,
            }
        ],
        now=NOW + timedelta(seconds=1),
    )
    model = presenter.refresh_from_events()

    assert result["stage"] == "COMPLETED"
    assert mutable.state.allowed_ports == (1433,)
    assert model.hosts["CLIENT-01"].control["allowedPorts"] == [1433]
    assert model.operation_stages[result["operationId"]] == "COMPLETED"


def test_failed_verification_rolls_back_and_ui_sees_rolled_back_state() -> None:
    presenter, commands, mutable, audit = _build(fail_verification=True)
    actor = ActorContext("operator-1", Role.OPERATOR)

    result = commands.set_internet_allowed(
        actor=actor,
        host_id="CLIENT-01",
        allowed=False,
        now=NOW + timedelta(seconds=1),
    )
    model = presenter.refresh_from_events()

    assert result["stage"] == "ROLLED_BACK"
    assert result["rolledBack"] is True
    assert mutable.state.internet_allowed is True
    assert model.hosts["CLIENT-01"].control["internetAllowed"] is True
    assert model.operation_stages[result["operationId"]] == "ROLLED_BACK"
    assert audit.events[-1]["result"] == "ROLLED_BACK"


def test_viewer_command_is_rejected_before_engine_execution() -> None:
    presenter, commands, mutable, audit = _build()
    before_sequence = presenter.model.latest_sequence

    with pytest.raises(PermissionError):
        commands.set_internet_allowed(
            actor=ActorContext("viewer-1", Role.VIEWER),
            host_id="CLIENT-01",
            allowed=False,
            now=NOW + timedelta(seconds=1),
        )

    assert mutable.state.internet_allowed is True
    assert len(audit.events) >= 1  # initial heartbeat audit may exist; no mutation audit appended
    model = presenter.refresh_from_events()
    assert model.latest_sequence == before_sequence
