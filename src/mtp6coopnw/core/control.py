from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mtp6coopnw.adapters import AuditStore, ClockPort
from mtp6coopnw.core.alarms import CentralAlarm, alarms_for_host
from mtp6coopnw.core.registry import HostRegistry, HostView, PolicyRegistry

_ALLOWED_ROLES = {"client", "database_server", "control"}


class TelemetryIngestError(ValueError):
    """Raised when telemetry does not match the Core read-only contract."""


@dataclass(slots=True)
class ControlCore:
    clock: ClockPort
    audit_store: AuditStore
    hosts: HostRegistry
    policies: PolicyRegistry

    def register_host(self, host_id: str, role: str) -> None:
        _validate_role(role)
        self.hosts.register(host_id, role)
        self.audit_store.append(
            {
                "event": "core.host_registered",
                "hostId": host_id,
                "role": role,
                "timestamp": self.clock.now().isoformat(),
            }
        )

    def ingest(self, event: dict[str, Any]) -> None:
        event_name = event.get("event")
        if event_name != "agent.heartbeat":
            raise TelemetryIngestError(f"Unsupported event: {event_name}")

        source_timestamp = _parse_timestamp(event.get("timestamp"))
        data = event.get("data")
        if not isinstance(data, dict):
            raise TelemetryIngestError("Heartbeat event requires data object")

        snapshot = data.get("snapshot")
        if not isinstance(snapshot, dict):
            raise TelemetryIngestError("Heartbeat event requires data.snapshot object")

        host_id = snapshot.get("hostId")
        role = snapshot.get("role")
        if not isinstance(host_id, str) or not host_id:
            raise TelemetryIngestError("Heartbeat snapshot requires hostId")
        if not isinstance(role, str) or not role:
            raise TelemetryIngestError("Heartbeat snapshot requires role")
        _validate_role(role)

        received_at = self.clock.now()
        result = self.hosts.ingest_heartbeat(
            host_id=host_id,
            role=role,
            received_at=received_at,
            source_timestamp=source_timestamp,
            snapshot=snapshot,
        )

        if result == "STALE":
            self.audit_store.append(
                {
                    "event": "core.heartbeat_rejected",
                    "hostId": host_id,
                    "reason": "STALE",
                    "timestamp": received_at.isoformat(),
                    "sourceTimestamp": source_timestamp.isoformat(),
                }
            )
            raise TelemetryIngestError("Stale heartbeat rejected")

        if result == "CONFLICT":
            self.audit_store.append(
                {
                    "event": "core.heartbeat_rejected",
                    "hostId": host_id,
                    "reason": "CONFLICT",
                    "timestamp": received_at.isoformat(),
                    "sourceTimestamp": source_timestamp.isoformat(),
                }
            )
            raise TelemetryIngestError("Conflicting heartbeat timestamp rejected")

        if result == "DUPLICATE":
            self.audit_store.append(
                {
                    "event": "core.heartbeat_duplicate",
                    "hostId": host_id,
                    "timestamp": received_at.isoformat(),
                    "sourceTimestamp": source_timestamp.isoformat(),
                }
            )
            return

        self.audit_store.append(dict(event))

    def host(self, host_id: str) -> HostView:
        return self.hosts.get_view(host_id, now=self.clock.now())

    def list_hosts(self) -> tuple[HostView, ...]:
        return self.hosts.list_views(now=self.clock.now())

    def list_alarms(self) -> tuple[CentralAlarm, ...]:
        return tuple(
            alarm
            for view in self.list_hosts()
            for alarm in alarms_for_host(view)
        )

    def set_policy_read_only(self, host_id: str, policy: dict[str, Any]) -> None:
        self.policies.set(host_id, policy)
        self.audit_store.append(
            {
                "event": "core.policy_staged",
                "hostId": host_id,
                "timestamp": self.clock.now().isoformat(),
                "policyRevision": policy.get("policy_revision"),
                "mode": "READ_ONLY",
            }
        )

    def get_policy(self, host_id: str) -> dict[str, Any] | None:
        return self.policies.get(host_id)


def _validate_role(role: str) -> None:
    if role not in _ALLOWED_ROLES:
        raise TelemetryIngestError(f"Unsupported host role: {role}")


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise TelemetryIngestError("Heartbeat event requires timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise TelemetryIngestError("Invalid heartbeat timestamp") from exc
    if parsed.tzinfo is None:
        raise TelemetryIngestError("Heartbeat timestamp must be timezone-aware")
    return parsed
