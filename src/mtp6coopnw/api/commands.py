from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from mtp6coopnw.security.access import ActorContext, authorize
from mtp6coopnw.security.audit import mutation_audit


class AuditSink(Protocol):
    def append(self, event: dict[str, Any]) -> None: ...


class CommandExecutor(Protocol):
    def apply(
        self,
        *,
        host_id: str,
        desired: dict[str, Any],
        now: datetime,
    ) -> dict[str, Any]: ...


@dataclass(slots=True)
class NetworkControlFacade:
    executor: CommandExecutor
    audit: AuditSink

    def set_host_enabled(
        self,
        *,
        actor: ActorContext,
        host_id: str,
        enabled: bool,
        now: datetime,
    ) -> dict[str, Any]:
        return self._execute(
            actor=actor,
            host_id=host_id,
            action="host.enabled",
            desired={"hostEnabled": enabled},
            now=now,
        )

    def set_internet_allowed(
        self,
        *,
        actor: ActorContext,
        host_id: str,
        allowed: bool,
        now: datetime,
    ) -> dict[str, Any]:
        return self._execute(
            actor=actor,
            host_id=host_id,
            action="internet.allowed",
            desired={"internetAllowed": allowed},
            now=now,
        )

    def set_database_allowed(
        self,
        *,
        actor: ActorContext,
        host_id: str,
        allowed: bool,
        now: datetime,
    ) -> dict[str, Any]:
        return self._execute(
            actor=actor,
            host_id=host_id,
            action="database.allowed",
            desired={"databaseAllowed": allowed},
            now=now,
        )

    def set_port_rules(
        self,
        *,
        actor: ActorContext,
        host_id: str,
        rules: list[dict[str, Any]],
        now: datetime,
    ) -> dict[str, Any]:
        authorize(actor, "configure")
        return self._execute(
            actor=actor,
            host_id=host_id,
            action="ports.configure",
            desired={"portRules": rules},
            now=now,
            preauthorized=True,
        )

    def _execute(
        self,
        *,
        actor: ActorContext,
        host_id: str,
        action: str,
        desired: dict[str, Any],
        now: datetime,
        preauthorized: bool = False,
    ) -> dict[str, Any]:
        if not preauthorized:
            authorize(actor, "operate")
        result = self.executor.apply(host_id=host_id, desired=desired, now=now)
        event = mutation_audit(
            actor=actor,
            action=action,
            host_id=host_id,
            now=now,
            result=str(result.get("stage", "UNKNOWN")),
            operation_id=result.get("operationId"),
            details={"desired": desired},
        )
        self.audit.append(event.to_dict())
        return result
