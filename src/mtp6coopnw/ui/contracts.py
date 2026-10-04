from __future__ import annotations

from typing import Any, Protocol


class DashboardBackend(Protocol):
    """Minimal UI/backend contract; intentionally independent from engines."""

    def bootstrap_dashboard(self) -> dict[str, Any]: ...

    def next_ui_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> dict[str, Any]: ...
