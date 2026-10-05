from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mtp6coopnw.security.access import ActorContext


@dataclass(frozen=True, slots=True)
class MutationAuditEvent:
    actor_id: str
    actor_role: str
    action: str
    host_id: str
    timestamp: datetime
    result: str
    operation_id: str | None = None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "actorId": self.actor_id,
            "actorRole": self.actor_role,
            "action": self.action,
            "hostId": self.host_id,
            "timestamp": self.timestamp.isoformat(),
            "result": self.result,
            "operationId": self.operation_id,
            "details": dict(self.details or {}),
        }


def mutation_audit(
    *,
    actor: ActorContext,
    action: str,
    host_id: str,
    now: datetime,
    result: str,
    operation_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> MutationAuditEvent:
    return MutationAuditEvent(
        actor.actor_id,
        actor.role.value,
        action,
        host_id,
        now,
        result,
        operation_id,
        details,
    )
