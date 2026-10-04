from __future__ import annotations

from typing import Any, NotRequired, Protocol, TypedDict


class ControlStatePayload(TypedDict):
    hostEnabled: bool
    internetAllowed: bool
    databaseAllowed: bool
    allowedPorts: list[int]


class ActionAvailabilityPayload(TypedDict):
    canViewDetails: bool
    canPlan: bool
    canApply: bool
    canRetry: bool
    canEnterMaintenance: bool


class HostCardPayload(TypedDict):
    hostId: str
    role: str
    freshness: str
    health: str
    policyRevision: int | None
    lastHeartbeat: str | None
    alarmCount: int
    control: ControlStatePayload
    actions: ActionAvailabilityPayload


class DashboardSummaryPayload(TypedDict):
    hostCount: int
    activeAlarmCount: int


class DashboardPayload(TypedDict):
    hosts: list[HostCardPayload]
    alarms: list[dict[str, Any]]
    summary: DashboardSummaryPayload
    latestSequence: int


class UiEventPayload(TypedDict):
    eventType: str
    sequence: int
    data: dict[str, Any]
    hostId: NotRequired[str]
    operationId: NotRequired[str]


class UiEventBatchPayload(TypedDict):
    events: list[UiEventPayload]
    latestSequence: int
    resyncRequired: bool


class DashboardBackend(Protocol):
    """Minimal UI/backend contract; intentionally independent from engines."""

    def bootstrap_dashboard(self) -> DashboardPayload: ...

    def next_ui_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> UiEventBatchPayload: ...
