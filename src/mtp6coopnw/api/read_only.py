from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mtp6coopnw.core import ControlCore


@dataclass(slots=True)
class ReadOnlyControlApi:
    core: ControlCore

    def list_hosts(self) -> list[dict[str, Any]]:
        return [view.to_dict() for view in self.core.list_hosts()]

    def get_host(self, host_id: str) -> dict[str, Any]:
        return self.core.host(host_id).to_dict()

    def get_alarms(self) -> list[dict[str, str]]:
        return [alarm.to_dict() for alarm in self.core.list_alarms()]

    def get_policy(self, host_id: str) -> dict[str, Any] | None:
        return self.core.get_policy(host_id)

    def register_host(self, host_id: str, role: str) -> None:
        self.core.register_host(host_id, role)

    def ingest_heartbeat(self, event: dict[str, Any]) -> None:
        self.core.ingest(event)
