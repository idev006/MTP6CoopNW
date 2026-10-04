from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.adapters import AuditStore, ClockPort
from mtp6coopnw.core.alarms import CentralAlarm, alarms_for_host
from mtp6coopnw.core.registry import HostRegistry, HostView, PolicyRegistry
from mtp6coopnw.observability import EventPublisher

_ALLOWED_ROLES = {"client", "database_server", "control"}


class TelemetryIngestError(ValueError):
    """Raised when telemetry does not match the Core read-only contract."""


@dataclass(slots=True)
class ControlCore:
    clock: ClockPort
    audit_store: AuditStore
    hosts: HostRegistry
    policies: PolicyRegistry
    event_publisher: EventPublisher | None = None
    _published_freshness: dict[str, str] = field(default_factory=dict, init=False)

    def register_host(self, host_id: str, role: str) -> None:
        _validate_role(role)
        self.hosts.register(host_id, role)
        now = self.clock.now()
        self.audit_store.append(
            {
                "event": "core.host_registered",
                "hostId": host_id,
                "role": role,
                "timestamp": now.isoformat(),
            }
        )
        self._publish(
            "host.registered",
            timestamp=now,
            host_id=host_id,
            data={"role": role},
        )
        self.refresh_freshness_events()

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
            self._reject_heartbeat(host_id, source_timestamp, received_at, "STALE")
            raise TelemetryIngestError("Stale heartbeat rejected")

        if result == "CONFLICT":
            self._reject_heartbeat(host_id, source_timestamp, received_at, "CONFLICT")
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
            self._publish(
                "host.telemetry_duplicate",
                timestamp=received_at,
                host_id=host_id,
                data={"sourceTimestamp": source_timestamp.isoformat()},
            )
            return

        self.audit_store.append(dict(event))
        self._publish(
            "host.telemetry_updated",
            timestamp=received_at,
            host_id=host_id,
            policy_revision=_valid_revision(snapshot.get("policyRevision")),
            data={
                "healthy": snapshot.get("healthy"),
                "sourceTimestamp": source_timestamp.isoformat(),
                "snapshot": snapshot,
            },
        )
        self.refresh_freshness_events()

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

    def refresh_freshness_events(self) -> None:
        """Publish host freshness transitions from the Core monitoring cycle."""
        now = self.clock.now()
        for view in self.list_hosts():
            current = view.freshness.value
            previous = self._published_freshness.get(view.host_id)
            if previous == current:
                continue
            self._published_freshness[view.host_id] = current
            self._publish(
                "host.freshness_changed",
                timestamp=now,
                host_id=view.host_id,
                policy_revision=view.policy_revision,
                data={"from": previous, "to": current},
            )

    def run_monitoring_cycle(self) -> None:
        """Core-side timer hook; UI never needs to poll status for freshness."""
        self.refresh_freshness_events()

    def set_policy_read_only(self, host_id: str, policy: dict[str, Any]) -> None:
        self.policies.set(host_id, policy)
        now = self.clock.now()
        revision = _valid_revision(policy.get("policy_revision"))
        self.audit_store.append(
            {
                "event": "core.policy_staged",
                "hostId": host_id,
                "timestamp": now.isoformat(),
                "policyRevision": revision,
                "mode": "READ_ONLY",
            }
        )
        self._publish(
            "policy.staged",
            timestamp=now,
            host_id=host_id,
            policy_revision=revision,
            data={"mode": "READ_ONLY"},
        )

    def get_policy(self, host_id: str) -> dict[str, Any] | None:
        return self.policies.get(host_id)

    def _reject_heartbeat(
        self,
        host_id: str,
        source_timestamp: datetime,
        received_at: datetime,
        reason: str,
    ) -> None:
        self.audit_store.append(
            {
                "event": "core.heartbeat_rejected",
                "hostId": host_id,
                "reason": reason,
                "timestamp": received_at.isoformat(),
                "sourceTimestamp": source_timestamp.isoformat(),
            }
        )
        self._publish(
            "host.telemetry_rejected",
            timestamp=received_at,
            host_id=host_id,
            data={
                "reason": reason,
                "sourceTimestamp": source_timestamp.isoformat(),
            },
        )

    def _publish(
        self,
        event_type: str,
        *,
        timestamp: datetime,
        host_id: str | None = None,
        policy_revision: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        if self.event_publisher is None:
            return
        self.event_publisher.publish(
            event_type,
            timestamp=timestamp,
            source="core",
            host_id=host_id,
            policy_revision=policy_revision,
            data=data,
        )


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


def _valid_revision(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
