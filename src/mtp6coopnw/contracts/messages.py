from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class MessageEnvelope:
    message_type: str
    source: str
    target: str
    created_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: UUID = field(default_factory=uuid4)
    schema_version: int = 1


@dataclass(frozen=True, slots=True)
class PolicyEnvelope:
    host_id: str
    revision: int
    schema_version: int
    effective_from: datetime | None
    policy: dict[str, Any]
