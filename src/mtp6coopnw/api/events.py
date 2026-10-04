from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterator

from mtp6coopnw.api.facade import ReadOnlyControlFacade
from mtp6coopnw.observability import ApplicationEvent, InMemoryEventBus


@dataclass(slots=True)
class UiEventGateway:
    """Snapshot plus event-delta boundary for reactive UI adapters."""

    status: ReadOnlyControlFacade
    events: InMemoryEventBus

    def bootstrap(self) -> dict[str, Any]:
        snapshot = self.status.system_status()
        return {
            "snapshot": snapshot,
            "latestSequence": self.events.latest_sequence,
        }

    def next_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return self.events.wait(
            after_sequence=after_sequence,
            timeout_seconds=timeout_seconds,
            limit=limit,
        ).to_dict()


@dataclass(slots=True)
class SseEventGateway:
    """Server-Sent Events adapter with sequence IDs and reconnect support."""

    events: InMemoryEventBus

    def stream(
        self,
        *,
        after_sequence: int = 0,
        timeout_seconds: float = 15.0,
        limit: int = 100,
    ) -> Iterator[str]:
        sequence = after_sequence
        while True:
            batch = self.events.wait(
                after_sequence=sequence,
                timeout_seconds=timeout_seconds,
                limit=limit,
            )
            if batch.resync_required:
                yield (
                    "event: system.resync_required\n"
                    f"data: {json.dumps({'latestSequence': batch.latest_sequence})}\n\n"
                )
                return
            if not batch.events:
                yield ": keepalive\n\n"
                continue
            for event in batch.events:
                yield format_sse(event)
                sequence = event.sequence


def format_sse(event: ApplicationEvent) -> str:
    payload = json.dumps(
        event.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        f"id: {event.sequence}\n"
        f"event: {event.event_type}\n"
        f"data: {payload}\n\n"
    )
