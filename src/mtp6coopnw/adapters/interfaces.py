from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol


class ClockPort(Protocol):
    def now(self) -> datetime: ...


class NetworkPort(Protocol):
    def get_state(self) -> dict[str, Any]: ...


class FirewallPort(Protocol):
    def get_state(self) -> dict[str, Any]: ...


class SqlPort(Protocol):
    def get_state(self) -> dict[str, Any]: ...


class PolicyStore(Protocol):
    def get(self, host_id: str) -> dict[str, Any] | None: ...

    def save(self, host_id: str, policy: dict[str, Any]) -> None: ...


class AuditStore(Protocol):
    def append(self, event: dict[str, Any]) -> None: ...


class TransportPort(Protocol):
    def send(self, target: str, message: dict[str, Any]) -> None: ...
