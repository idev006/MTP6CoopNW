from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MetricRegistry:
    counters: dict[str, float] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)

    def increment(self, name: str, amount: float = 1.0) -> float:
        value = self.counters.get(name, 0.0) + amount
        self.counters[name] = value
        return value

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def snapshot(self) -> dict[str, dict[str, float]]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
        }
