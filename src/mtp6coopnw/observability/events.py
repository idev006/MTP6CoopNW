from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class EventRecord:
    event: str
    timestamp: datetime
    component: str
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    host_id: str | None = None
    operation: str | None = None
    policy_revision: int | None = None
    result: str | None = None
    duration_ms: float | None = None
    error_code: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "event": self.event,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "correlationId": self.correlation_id,
        }
        optional = {
            "hostId": self.host_id,
            "operation": self.operation,
            "policyRevision": self.policy_revision,
            "result": self.result,
            "durationMs": self.duration_ms,
            "errorCode": self.error_code,
        }
        payload.update({key: value for key, value in optional.items() if value is not None})
        if self.data:
            payload["data"] = dict(self.data)
        return payload
