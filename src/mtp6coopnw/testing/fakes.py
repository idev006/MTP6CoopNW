from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass(slots=True)
class FakeClock:
    current: datetime

    def now(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> datetime:
        self.current += delta
        return self.current

    def set(self, value: datetime) -> None:
        self.current = value


@dataclass(slots=True)
class FakeNetworkAdapter:
    lan_reachable: bool = True
    internet_reachable: bool = True

    def get_state(self) -> dict[str, Any]:
        return {
            "lan_reachable": self.lan_reachable,
            "internet_reachable": self.internet_reachable,
        }


@dataclass(slots=True)
class FakeFirewallAdapter:
    internet_allowed: bool = True
    database_allowed: bool = True
    allowed_ports: set[int] = field(default_factory=set)

    def get_state(self) -> dict[str, Any]:
        return {
            "internet_allowed": self.internet_allowed,
            "database_allowed": self.database_allowed,
            "allowed_ports": sorted(self.allowed_ports),
        }

    def apply_access(
        self,
        *,
        internet_allowed: bool | None = None,
        database_allowed: bool | None = None,
        allowed_ports: set[int] | None = None,
    ) -> None:
        if internet_allowed is not None:
            self.internet_allowed = internet_allowed
        if database_allowed is not None:
            self.database_allowed = database_allowed
        if allowed_ports is not None:
            self.allowed_ports = set(allowed_ports)


@dataclass(slots=True)
class FakeSqlAdapter:
    reachable: bool = True
    port: int = 1433

    def get_state(self) -> dict[str, Any]:
        return {"reachable": self.reachable, "port": self.port}


@dataclass(slots=True)
class FakeServiceAdapter:
    services: dict[str, str] = field(default_factory=dict)

    def get_state(self) -> dict[str, Any]:
        return {"services": copy.deepcopy(self.services)}


@dataclass(slots=True)
class InMemoryPolicyStore:
    policies: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get(self, host_id: str) -> dict[str, Any] | None:
        value = self.policies.get(host_id)
        return copy.deepcopy(value) if value is not None else None

    def save(self, host_id: str, policy: dict[str, Any]) -> None:
        self.policies[host_id] = copy.deepcopy(policy)


@dataclass(slots=True)
class InMemoryAuditStore:
    events: list[dict[str, Any]] = field(default_factory=list)

    def append(self, event: dict[str, Any]) -> None:
        self.events.append(copy.deepcopy(event))


@dataclass(slots=True)
class FakeTransport:
    sent: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    online: bool = True

    def send(self, target: str, message: dict[str, Any]) -> None:
        if not self.online:
            raise ConnectionError("Fake transport is offline")
        self.sent.append((target, copy.deepcopy(message)))
