from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mtp6coopnw.api.events import UiEventGateway
from mtp6coopnw.api.facade import ReadOnlyControlFacade


@dataclass(slots=True)
class UiApplicationFacade:
    """Presentation-ready facade.

    Concrete UI code receives stable DTO-like dictionaries and does not import
    Core/Engine types. Action flags are presentation hints only; command handlers
    must still revalidate authorization and safety interlocks.
    """

    status: ReadOnlyControlFacade
    events: UiEventGateway

    def bootstrap_dashboard(self) -> dict[str, Any]:
        raw = self.events.bootstrap()
        snapshot = raw["snapshot"]
        alarm_counts = self._alarm_counts(snapshot["alarms"])
        hosts = [
            self._host_card(host, alarm_counts.get(str(host["hostId"]), 0))
            for host in snapshot["hosts"]
        ]
        return {
            "hosts": hosts,
            "alarms": snapshot["alarms"],
            "summary": snapshot["summary"],
            "latestSequence": raw["latestSequence"],
        }

    def next_ui_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> dict[str, Any]:
        batch = self.events.next_events(
            after_sequence=after_sequence,
            timeout_seconds=timeout_seconds,
            limit=limit,
        )
        if batch["resyncRequired"]:
            return batch

        enriched: list[dict[str, Any]] = []
        for raw_event in batch["events"]:
            event = dict(raw_event)
            host_id = event.get("hostId")
            if isinstance(host_id, str) and self._needs_host_projection(event):
                try:
                    host = self.status.get_host(host_id)
                except KeyError:
                    host = None
                if host is not None:
                    alarms = self.status.get_alarms()
                    alarm_count = sum(
                        1 for alarm in alarms if alarm["hostId"] == host_id
                    )
                    data = dict(event.get("data", {}))
                    data["hostCard"] = self._host_card(host, alarm_count)
                    event["data"] = data
            enriched.append(event)

        return {
            "events": enriched,
            "latestSequence": batch["latestSequence"],
            "resyncRequired": False,
        }

    @staticmethod
    def _needs_host_projection(event: dict[str, Any]) -> bool:
        return event.get("eventType") in {
            "host.registered",
            "host.telemetry_updated",
            "host.freshness_changed",
            "policy.staged",
        }

    @staticmethod
    def _alarm_counts(alarms: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for alarm in alarms:
            host_id = str(alarm["hostId"])
            counts[host_id] = counts.get(host_id, 0) + 1
        return counts

    @staticmethod
    def _host_card(host: dict[str, Any], alarm_count: int) -> dict[str, Any]:
        freshness = str(host["freshness"])
        healthy = host["healthy"]
        health = (
            "HEALTHY"
            if healthy is True
            else ("DEGRADED" if healthy is False else "UNKNOWN")
        )
        actionable = freshness == "ONLINE" and healthy is True
        snapshot = host.get("snapshot")
        control = {}
        if isinstance(snapshot, dict):
            value = snapshot.get("control")
            if isinstance(value, dict):
                control = {
                    "hostEnabled": bool(value.get("hostEnabled", True)),
                    "internetAllowed": bool(value.get("internetAllowed", False)),
                    "databaseAllowed": bool(value.get("databaseAllowed", False)),
                    "allowedPorts": [
                        int(port)
                        for port in value.get("allowedPorts", [])
                        if isinstance(port, int) and not isinstance(port, bool)
                    ],
                }
        return {
            "hostId": host["hostId"],
            "role": host["role"],
            "freshness": freshness,
            "health": health,
            "policyRevision": host["policyRevision"],
            "lastHeartbeat": host["lastHeartbeat"],
            "alarmCount": alarm_count,
            "control": control,
            "actions": {
                "canViewDetails": True,
                "canPlan": actionable,
                "canApply": actionable,
                "canRetry": freshness in {"STALE", "OFFLINE"} or healthy is False,
                "canEnterMaintenance": freshness == "ONLINE" and healthy is True,
            },
        }
