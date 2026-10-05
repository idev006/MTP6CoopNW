from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class IdempotencyStore(Generic[T]):
    _items: dict[str, tuple[str, T]] = field(default_factory=dict)

    @staticmethod
    def digest(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def execute_once(
        self,
        operation_id: str,
        payload: dict[str, Any],
        action: Callable[[], T],
    ) -> tuple[T, bool]:
        digest = self.digest(payload)
        existing = self._items.get(operation_id)
        if existing is not None:
            old_digest, result = existing
            if old_digest != digest:
                raise ValueError("operation id reused with different payload")
            return result, True
        result = action()
        self._items[operation_id] = (digest, result)
        return result, False
