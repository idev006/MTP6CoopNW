from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from mtp6coopnw.api.desktop import DesktopActionFacade
from mtp6coopnw.security import ActorContext, Role

NOW = datetime(2026, 10, 4, 10, 0, tzinfo=UTC)


@dataclass
class FakeClock:
    def now(self) -> datetime:
        return NOW


class FakeCommands:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def _record(self, action: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"action": action, **kwargs})
        return {"operationId": "op-1", "stage": "COMPLETED"}

    def set_host_enabled(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("host", **kwargs)

    def set_internet_allowed(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("internet", **kwargs)

    def set_database_allowed(self, **kwargs: Any) -> dict[str, Any]:
        return self._record("database", **kwargs)


def test_desktop_action_facade_binds_actor_and_clock() -> None:
    commands = FakeCommands()
    actor = ActorContext("operator-1", Role.OPERATOR)
    facade = DesktopActionFacade(commands=commands, actor=actor, clock=FakeClock())

    result = facade.set_internet_allowed("CLIENT-01", False)

    assert result["stage"] == "COMPLETED"
    assert commands.calls == [
        {
            "action": "internet",
            "actor": actor,
            "host_id": "CLIENT-01",
            "allowed": False,
            "now": NOW,
        }
    ]
