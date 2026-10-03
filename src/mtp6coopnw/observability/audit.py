from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event: str
    actor: str
    target: str
    timestamp: datetime
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    policy_revision: int | None = None
    before: dict[str, Any] = field(default_factory=dict)
    after: dict[str, Any] = field(default_factory=dict)
    result: str = "UNKNOWN"
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "actor": self.actor,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "correlationId": self.correlation_id,
            "policyRevision": self.policy_revision,
            "before": dict(self.before),
            "after": dict(self.after),
            "result": self.result,
            "errorCode": self.error_code,
        }
