from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from mtp6coopnw.security import ActorContext


class ClockLike(Protocol):
    def now(self) -> datetime: ...


class CommandLike(Protocol):
    def set_host_enabled(
        self, *, actor: ActorContext, host_id: str, enabled: bool, now: datetime
    ) -> dict[str, Any]: ...

    def set_internet_allowed(
        self, *, actor: ActorContext, host_id: str, allowed: bool, now: datetime
    ) -> dict[str, Any]: ...

    def set_database_allowed(
        self, *, actor: ActorContext, host_id: str, allowed: bool, now: datetime
    ) -> dict[str, Any]: ...


@dataclass(slots=True)
class DesktopActionFacade:
    """Bind actor/session and clock for the concrete desktop shell."""

    commands: CommandLike
    actor: ActorContext
    clock: ClockLike

    def set_host_enabled(self, host_id: str, enabled: bool) -> dict[str, Any]:
        return self.commands.set_host_enabled(
            actor=self.actor,
            host_id=host_id,
            enabled=enabled,
            now=self.clock.now(),
        )

    def set_internet_allowed(self, host_id: str, allowed: bool) -> dict[str, Any]:
        return self.commands.set_internet_allowed(
            actor=self.actor,
            host_id=host_id,
            allowed=allowed,
            now=self.clock.now(),
        )

    def set_database_allowed(self, host_id: str, allowed: bool) -> dict[str, Any]:
        return self.commands.set_database_allowed(
            actor=self.actor,
            host_id=host_id,
            allowed=allowed,
            now=self.clock.now(),
        )
