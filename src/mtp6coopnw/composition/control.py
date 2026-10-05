from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mtp6coopnw.adapters import AuditStore, ClockPort
from mtp6coopnw.api import (
    EngineCommandExecutor,
    NetworkControlFacade,
    ReadOnlyControlFacade,
    UiApplicationFacade,
    UiEventGateway,
)
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import InMemoryEventBus
from mtp6coopnw.operations import ActualState, MutableHost, OperationEngine, Planner
from mtp6coopnw.policy import PolicyEngine
from mtp6coopnw.ui import DashboardPresenter


@dataclass(frozen=True, slots=True)
class ManagedHostSpec:
    host_id: str
    role: str
    state: ActualState


@dataclass(slots=True)
class CoreStateReporter:
    core: ControlCore
    roles: dict[str, str]

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
                "component": "application-service",
                "data": {
                    "snapshot": {
                        "hostId": host_id,
                        "role": self.roles[host_id],
                        "healthy": True,
                        "policyRevision": policy_revision,
                        "control": state,
                    }
                },
            }
        )


@dataclass(slots=True)
class ControlRuntime:
    """Composition-root product for a headless central-control runtime."""

    core: ControlCore
    status: ReadOnlyControlFacade
    commands: NetworkControlFacade
    ui: UiApplicationFacade
    presenter: DashboardPresenter
    events: InMemoryEventBus
    hosts: dict[str, MutableHost]


def compose_control_runtime(
    *,
    stale_after_seconds: int,
    offline_after_seconds: int,
    clock: ClockPort,
    audit_store: AuditStore,
    managed_hosts: tuple[ManagedHostSpec, ...],
    event_retention: int = 2048,
) -> ControlRuntime:
    """Assemble concrete application/domain components in one composition root.

    External operating-system effects remain behind MutableHost/reference state in
    this runtime. Production Windows/SQL adapters are injected by a production
    composition root after controlled integration acceptance.
    """
    if stale_after_seconds < 1:
        raise ValueError("stale_after_seconds must be >= 1")
    if offline_after_seconds <= stale_after_seconds:
        raise ValueError(
            "offline_after_seconds must be greater than stale_after_seconds"
        )

    events = InMemoryEventBus(retention=event_retention)
    core = ControlCore(
        clock=clock,
        audit_store=audit_store,
        hosts=HostRegistry(
            stale_after_seconds=stale_after_seconds,
            offline_after_seconds=offline_after_seconds,
        ),
        policies=PolicyRegistry(),
        event_publisher=events,
    )

    hosts: dict[str, MutableHost] = {}
    roles: dict[str, str] = {}
    for spec in managed_hosts:
        if spec.host_id in hosts:
            raise ValueError(f"duplicate managed host: {spec.host_id}")
        core.register_host(spec.host_id, spec.role)
        hosts[spec.host_id] = MutableHost(spec.state)
        roles[spec.host_id] = spec.role
        core.ingest(
            {
                "event": "agent.heartbeat",
                "timestamp": clock.now().isoformat(),
                "component": "composition-root",
                "data": {
                    "snapshot": {
                        "hostId": spec.host_id,
                        "role": spec.role,
                        "healthy": True,
                        "policyRevision": 1,
                        "control": _state_payload(spec.state),
                    }
                },
            }
        )

    operation = OperationEngine(event_publisher=events)
    executor = EngineCommandExecutor(
        policy_engine=PolicyEngine(),
        planner=Planner(),
        operation_engine=operation,
        hosts=hosts,
        state_reporter=CoreStateReporter(core=core, roles=roles),
    )
    commands = NetworkControlFacade(executor=executor, audit=audit_store)
    status = ReadOnlyControlFacade(core)
    event_gateway = UiEventGateway(status=status, events=events)
    ui = UiApplicationFacade(status=status, events=event_gateway)
    presenter = DashboardPresenter.create(ui)

    return ControlRuntime(
        core=core,
        status=status,
        commands=commands,
        ui=ui,
        presenter=presenter,
        events=events,
        hosts=hosts,
    )


def _state_payload(state: ActualState) -> dict[str, Any]:
    return {
        "hostEnabled": state.host_enabled,
        "internetAllowed": state.internet_allowed,
        "databaseAllowed": state.database_allowed,
        "allowedPorts": list(state.allowed_ports),
        "lanReachable": state.lan_reachable,
        "controlReachable": state.control_reachable,
    }
