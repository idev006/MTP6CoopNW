from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Iterable
from zoneinfo import ZoneInfo

_DAY = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass(frozen=True, slots=True)
class ScheduleRule:
    name: str
    days: tuple[str, ...]
    start: time
    end: time
    timezone: str
    host_enabled: bool | None = None
    internet_allowed: bool | None = None
    database_allowed: bool | None = None
    allowed_ports: tuple[int, ...] | None = None

    def active(self, now: datetime) -> bool:
        local = now.astimezone(ZoneInfo(self.timezone))
        day = _DAY[local.weekday()]
        previous_day = _DAY[(local.weekday() - 1) % 7]
        current = local.timetz().replace(tzinfo=None)
        if self.start == self.end:
            return day in self.days
        if self.start < self.end:
            return day in self.days and self.start <= current < self.end
        return (day in self.days and current >= self.start) or (
            previous_day in self.days and current < self.end
        )


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    source: str
    priority: int
    host_enabled: bool | None = None
    internet_allowed: bool | None = None
    database_allowed: bool | None = None
    allowed_ports: tuple[int, ...] | None = None


@dataclass(frozen=True, slots=True)
class EffectivePolicy:
    host_id: str
    evaluated_at: datetime
    policy_revision: int
    policy_hash: str
    host_enabled: bool
    internet_allowed: bool
    database_allowed: bool
    allowed_ports: tuple[int, ...]
    winning_sources: tuple[str, ...]
    warnings: tuple[str, ...] = ()


class PolicyConflictError(ValueError):
    """Raised when equal-priority policy inputs disagree."""


def canonical_policy_hash(policy: dict[str, Any]) -> str:
    raw = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class PolicyEngine:
    """Deterministic policy resolver. Higher numeric priority wins per field."""

    def evaluate(
        self,
        *,
        host_id: str,
        now: datetime,
        policy: dict[str, Any],
        schedules: Iterable[ScheduleRule] = (),
        maintenance: PolicyDecision | None = None,
        manual_override: PolicyDecision | None = None,
        emergency: PolicyDecision | None = None,
        safety: PolicyDecision | None = None,
    ) -> EffectivePolicy:
        revision = policy.get("policy_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise ValueError("policy_revision must be integer >= 1")

        decisions: list[PolicyDecision] = [
            PolicyDecision(
                source="default",
                priority=10,
                host_enabled=bool(policy.get("host", {}).get("enabled", True)),
                internet_allowed=bool(policy.get("internet", {}).get("allowed", True)),
                database_allowed=bool(policy.get("database", {}).get("allowed", True)),
                allowed_ports=tuple(
                    sorted(set(policy.get("ports", {}).get("managed", ())))
                ),
            )
        ]
        for rule in schedules:
            if rule.active(now):
                decisions.append(
                    PolicyDecision(
                        source=f"schedule:{rule.name}",
                        priority=20,
                        host_enabled=rule.host_enabled,
                        internet_allowed=rule.internet_allowed,
                        database_allowed=rule.database_allowed,
                        allowed_ports=rule.allowed_ports,
                    )
                )
        for item in (maintenance, manual_override, emergency, safety):
            if item is not None:
                decisions.append(item)

        warnings: list[str] = []
        values: dict[str, Any] = {}
        sources: list[str] = []
        for field_name in (
            "host_enabled",
            "internet_allowed",
            "database_allowed",
            "allowed_ports",
        ):
            candidates = [
                decision
                for decision in decisions
                if getattr(decision, field_name) is not None
            ]
            top = max(decision.priority for decision in candidates)
            winners = [decision for decision in candidates if decision.priority == top]
            distinct = {repr(getattr(decision, field_name)) for decision in winners}
            if len(distinct) > 1:
                sources_text = ",".join(sorted(decision.source for decision in winners))
                raise PolicyConflictError(
                    f"equal-priority conflict for {field_name}: {sources_text}"
                )
            winner = sorted(winners, key=lambda decision: decision.source)[0]
            values[field_name] = getattr(winner, field_name)
            sources.append(f"{field_name}={winner.source}")

        if not values["host_enabled"] and values["internet_allowed"]:
            values["internet_allowed"] = False
            warnings.append("host_disabled_forces_internet_denied")

        return EffectivePolicy(
            host_id=host_id,
            evaluated_at=now,
            policy_revision=revision,
            policy_hash=canonical_policy_hash(policy),
            host_enabled=values["host_enabled"],
            internet_allowed=values["internet_allowed"],
            database_allowed=values["database_allowed"],
            allowed_ports=tuple(values["allowed_ports"]),
            winning_sources=tuple(sources),
            warnings=tuple(warnings),
        )


@dataclass(slots=True)
class VersionedPolicyStore:
    """Reference store implementing revision/replay behavior from ADR-008."""

    _items: dict[str, tuple[int, str, dict[str, Any]]] = field(default_factory=dict)

    def accept(self, host_id: str, policy: dict[str, Any]) -> str:
        revision = policy.get("policy_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            return "INVALID"
        digest = canonical_policy_hash(policy)
        current = self._items.get(host_id)
        if current is not None:
            current_revision, current_hash, _ = current
            if revision < current_revision:
                return "STALE"
            if revision == current_revision:
                return "DUPLICATE" if digest == current_hash else "CONFLICT"
        self._items[host_id] = (revision, digest, copy.deepcopy(policy))
        return "ACCEPTED"

    def get(self, host_id: str) -> dict[str, Any] | None:
        current = self._items.get(host_id)
        if current is None:
            return None
        return copy.deepcopy(current[2])
