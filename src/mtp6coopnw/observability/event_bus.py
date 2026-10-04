from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Condition, RLock
from typing import Any, Protocol
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ApplicationEvent:
    event_id: str
    sequence: int
    event_type: str
    timestamp: datetime
    source: str
    host_id: str | None = None
    operation_id: str | None = None
    correlation_id: str | None = None
    policy_revision: int | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "eventId": self.event_id,
            "sequence": self.sequence,
            "eventType": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": dict(self.data),
        }
        optional = {
            "hostId": self.host_id,
            "operationId": self.operation_id,
            "correlationId": self.correlation_id,
            "policyRevision": self.policy_revision,
        }
        payload.update({key: value for key, value in optional.items() if value is not None})
        return payload


@dataclass(frozen=True, slots=True)
class EventBatch:
    events: tuple[ApplicationEvent, ...]
    latest_sequence: int
    resync_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": [event.to_dict() for event in self.events],
            "latestSequence": self.latest_sequence,
            "resyncRequired": self.resync_required,
        }


class EventPublisher(Protocol):
    def publish(
        self,
        event_type: str,
        *,
        timestamp: datetime,
        source: str,
        host_id: str | None = None,
        operation_id: str | None = None,
        correlation_id: str | None = None,
        policy_revision: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> ApplicationEvent: ...


@dataclass(slots=True)
class InMemoryEventBus:
    """Thread-safe replayable event bus for Core/UI integration."""

    retention: int = 2048
    _events: deque[ApplicationEvent] = field(init=False)
    _sequence: int = field(default=0, init=False)
    _condition: Condition = field(init=False)

    def __post_init__(self) -> None:
        if self.retention < 1:
            raise ValueError("retention must be >= 1")
        self._events = deque(maxlen=self.retention)
        self._condition = Condition(RLock())

    @property
    def latest_sequence(self) -> int:
        with self._condition:
            return self._sequence

    def publish(
        self,
        event_type: str,
        *,
        timestamp: datetime,
        source: str,
        host_id: str | None = None,
        operation_id: str | None = None,
        correlation_id: str | None = None,
        policy_revision: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> ApplicationEvent:
        with self._condition:
            self._sequence += 1
            event = ApplicationEvent(
                event_id=str(uuid4()),
                sequence=self._sequence,
                event_type=event_type,
                timestamp=timestamp,
                source=source,
                host_id=host_id,
                operation_id=operation_id,
                correlation_id=correlation_id,
                policy_revision=policy_revision,
                data=dict(data or {}),
            )
            self._events.append(event)
            self._condition.notify_all()
            return event

    def read(self, *, after_sequence: int = 0, limit: int = 100) -> EventBatch:
        if after_sequence < 0:
            raise ValueError("after_sequence must be >= 0")
        if limit < 1:
            raise ValueError("limit must be >= 1")
        with self._condition:
            return self._read_locked(after_sequence=after_sequence, limit=limit)

    def wait(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> EventBatch:
        if timeout_seconds < 0:
            raise ValueError("timeout_seconds must be >= 0")
        with self._condition:
            batch = self._read_locked(after_sequence=after_sequence, limit=limit)
            if batch.events or batch.resync_required:
                return batch
            self._condition.wait(timeout_seconds)
            return self._read_locked(after_sequence=after_sequence, limit=limit)

    def _read_locked(self, *, after_sequence: int, limit: int) -> EventBatch:
        oldest = self._events[0].sequence if self._events else self._sequence + 1
        resync_required = after_sequence < oldest - 1
        events = tuple(
            event for event in self._events if event.sequence > after_sequence
        )[:limit]
        return EventBatch(
            events=events,
            latest_sequence=self._sequence,
            resync_required=resync_required,
        )
