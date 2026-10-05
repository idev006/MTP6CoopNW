from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from mtp6coopnw.application import StatusQueryService, UiEventService
from mtp6coopnw.ui.contracts import (
    ActionAvailabilityPayload,
    ControlStatePayload,
    DashboardPayload,
    DashboardSummaryPayload,
    HostCardPayload,
    UiEventBatchPayload,
    UiEventPayload,
)


@dataclass(slots=True)
class UiApplicationFacade:
    """Presentation-oriented facade with no dependency on concrete engines."""

    status: StatusQueryService
    events: UiEventService

    def bootstrap_dashboard(self) -> DashboardPayload:
        raw = self.events.bootstrap()
        snapshot = cast(dict[str, Any], raw["snapshot"])
        alarms = cast(list[dict[str, Any]], snapshot["alarms"])
        alarm_counts = self._alarm_counts(alarms)
        hosts = [
            self._host_card(host, alarm_counts.get(str(host["hostId"]), 0))
            for host in cast(list[dict[str, Any]], snapshot["hosts"])
        ]
        raw_summary = cast(dict[str, Any], snapshot["summary"])
        summary: DashboardSummaryPayload = {
            "hostCount": int(raw_summary.get("hostCount", len(hosts))),
            "activeAlarmCount": int(raw_summary.get("activeAlarmCount", len(alarms))),
        }
        return {
            "hosts": hosts,
            "alarms": alarms,
            "summary": summary,
            "latestSequence": int(raw["latestSequence"]),
        }

    def next_ui_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> UiEventBatchPayload:
        batch = self.events.next_events(
            after_sequence=after_sequence,
            timeout_seconds=timeout_seconds,
            limit=limit,
        )
        if bool(batch["resyncRequired"]):
            return {
                "events": [],
                "latestSequence": int(batch["latestSequence"]),
                "resyncRequired": True,
            }

        enriched: list[UiEventPayload] = []
        for raw_event in cast(list[dict[str, Any]], batch["events"]):
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
            enriched.append(cast(UiEventPayload, event))

        return {
            "events": enriched,
            "latestSequence": int(batch["latestSequence"]),
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
    def _host_card(host: dict[str, Any], alarm_count: int) -> HostCardPayload:
        freshness = str(host["freshness"])
        healthy = host["healthy"]
        health = (
            "HEALTHY"
            if healthy is True
            else ("DEGRADED" if healthy is False else "UNKNOWN")
        )
        actionable = freshness == "ONLINE" and healthy is True
        control: ControlStatePayload = {
            "hostEnabled": True,
            "internetAllowed": False,
            "databaseAllowed": False,
            "allowedPorts": [],
        }
        snapshot = host.get("snapshot")
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

        actions: ActionAvailabilityPayload = {
            "canViewDetails": True,
            "canPlan": actionable,
            "canApply": actionable,
            "canRetry": freshness in {"STALE", "OFFLINE"} or healthy is False,
            "canEnterMaintenance": freshness == "ONLINE" and healthy is True,
        }
        revision = host.get("policyRevision")
        last_heartbeat = host.get("lastHeartbeat")
        return {
            "hostId": str(host["hostId"]),
            "role": str(host["role"]),
            "freshness": freshness,
            "health": health,
            "policyRevision": revision if isinstance(revision, int) else None,
            "lastHeartbeat": (
                str(last_heartbeat) if last_heartbeat is not None else None
            ),
            "alarmCount": alarm_count,
            "control": control,
            "actions": actions,
        }
