from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mtp6coopnw.observability import FreshnessState, classify_freshness


@dataclass(slots=True)
class HostRecord:
    host_id: str
    role: str
    last_heartbeat: datetime | None = None
    last_source_timestamp: datetime | None = None
    policy_revision: int | None = None
    healthy: bool | None = None
    snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class HostView:
    host_id: str
    role: str
    freshness: FreshnessState
    healthy: bool | None
    last_heartbeat: datetime | None
    policy_revision: int | None
    snapshot: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostId": self.host_id,
            "role": self.role,
            "freshness": self.freshness.value,
            "healthy": self.healthy,
            "lastHeartbeat": (
                self.last_heartbeat.isoformat() if self.last_heartbeat else None
            ),
            "policyRevision": self.policy_revision,
            "snapshot": copy.deepcopy(self.snapshot),
        }


@dataclass(slots=True)
class HostRegistry:
    stale_after_seconds: int
    offline_after_seconds: int
    _hosts: dict[str, HostRecord] = field(default_factory=dict)

    def register(self, host_id: str, role: str) -> HostRecord:
        existing = self._hosts.get(host_id)
        if existing is not None:
            if existing.role != role:
                raise ValueError(f"Host role mismatch for {host_id}")
            return existing

        record = HostRecord(host_id=host_id, role=role)
        self._hosts[host_id] = record
        return record

    def ingest_heartbeat(
        self,
        *,
        host_id: str,
        role: str,
        received_at: datetime,
        source_timestamp: datetime,
        snapshot: dict[str, Any],
    ) -> str:
        record = self.register(host_id, role)

        if record.last_source_timestamp is not None:
            if source_timestamp < record.last_source_timestamp:
                return "STALE"
            if source_timestamp == record.last_source_timestamp:
                if snapshot == record.snapshot:
                    return "DUPLICATE"
                return "CONFLICT"

        record.last_heartbeat = received_at
        record.last_source_timestamp = source_timestamp
        revision = snapshot.get("policyRevision")
        record.policy_revision = (
            revision if isinstance(revision, int) and not isinstance(revision, bool) else None
        )
        healthy = snapshot.get("healthy")
        record.healthy = healthy if isinstance(healthy, bool) else None
        record.snapshot = copy.deepcopy(snapshot)
        return "ACCEPTED"

    def get_view(self, host_id: str, *, now: datetime) -> HostView:
        record = self._hosts[host_id]
        freshness = classify_freshness(
            now=now,
            last_heartbeat=record.last_heartbeat,
            stale_after_seconds=self.stale_after_seconds,
            offline_after_seconds=self.offline_after_seconds,
        )
        return HostView(
            host_id=record.host_id,
            role=record.role,
            freshness=freshness,
            healthy=record.healthy,
            last_heartbeat=record.last_heartbeat,
            policy_revision=record.policy_revision,
            snapshot=copy.deepcopy(record.snapshot),
        )

    def list_views(self, *, now: datetime) -> tuple[HostView, ...]:
        return tuple(
            self.get_view(host_id, now=now)
            for host_id in sorted(self._hosts)
        )


@dataclass(slots=True)
class PolicyRegistry:
    _policies: dict[str, dict[str, Any]] = field(default_factory=dict)

    def set(self, host_id: str, policy: dict[str, Any]) -> None:
        self._policies[host_id] = copy.deepcopy(policy)

    def get(self, host_id: str) -> dict[str, Any] | None:
        value = self._policies.get(host_id)
        return copy.deepcopy(value) if value is not None else None
