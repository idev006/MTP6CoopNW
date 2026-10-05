from __future__ import annotations

from dataclasses import dataclass

from mtp6coopnw.adapters import AuditStore, ClockPort
from mtp6coopnw.api import ReadOnlyControlFacade
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.observability import EventPublisher


@dataclass(frozen=True, slots=True)
class CoreCompositionSettings:
    stale_after_seconds: int
    offline_after_seconds: int

    def __post_init__(self) -> None:
        if self.stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be >= 1")
        if self.offline_after_seconds <= self.stale_after_seconds:
            raise ValueError(
                "offline_after_seconds must be greater than stale_after_seconds"
            )


def compose_read_only_core(
    *,
    settings: CoreCompositionSettings,
    clock: ClockPort,
    audit_store: AuditStore,
    policy_registry: PolicyRegistry | None = None,
    event_publisher: EventPublisher | None = None,
) -> ReadOnlyControlFacade:
    """Assemble the headless read-only Core behind its stable facade."""
    core = ControlCore(
        clock=clock,
        audit_store=audit_store,
        hosts=HostRegistry(
            stale_after_seconds=settings.stale_after_seconds,
            offline_after_seconds=settings.offline_after_seconds,
        ),
        policies=policy_registry or PolicyRegistry(),
        event_publisher=event_publisher,
    )
    return ReadOnlyControlFacade(core)
