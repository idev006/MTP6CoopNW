from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class SpecialDateRule(Generic[T]):
    day: date
    value: T
    enabled: bool = True

    def applies(self, now: datetime) -> bool:
        return self.enabled and now.date() == self.day


@dataclass(frozen=True, slots=True)
class TemporaryGrant(Generic[T]):
    value: T
    starts_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        if self.expires_at <= self.starts_at:
            raise ValueError("expires_at must be after starts_at")

    def active(self, now: datetime) -> bool:
        return self.starts_at <= now < self.expires_at


def resolve_temporal_override(
    *,
    now: datetime,
    default: T,
    special_dates: tuple[SpecialDateRule[T], ...] = (),
    temporary: TemporaryGrant[T] | None = None,
) -> T:
    if temporary is not None and temporary.active(now):
        return temporary.value
    matching = [rule for rule in special_dates if rule.applies(now)]
    if len(matching) > 1:
        values = {repr(rule.value) for rule in matching}
        if len(values) > 1:
            raise ValueError("conflicting special-date rules")
    if matching:
        return matching[0].value
    return default
