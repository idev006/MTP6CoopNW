from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mtp6coopnw.ui.contracts import DashboardBackend
from mtp6coopnw.ui.viewmodels import DashboardViewModel, HostCardViewModel


@dataclass(slots=True)
class DashboardPresenter:
    """Headless UI state coordinator, testable with a fake facade."""

    backend: DashboardBackend
    model: DashboardViewModel

    @classmethod
    def create(cls, backend: DashboardBackend) -> "DashboardPresenter":
        return cls(backend=backend, model=DashboardViewModel())

    def load(self) -> DashboardViewModel:
        payload = self.backend.bootstrap_dashboard()
        self._load_payload(payload)
        return self.model

    def refresh_from_events(
        self,
        *,
        timeout_seconds: float = 0.0,
        limit: int = 100,
    ) -> DashboardViewModel:
        batch = self.backend.next_ui_events(
            after_sequence=self.model.latest_sequence,
            timeout_seconds=timeout_seconds,
            limit=limit,
        )
        if bool(batch.get("resyncRequired")):
            self.model.resync_count += 1
            return self.load()

        events = batch.get("events", [])
        if not isinstance(events, list):
            raise ValueError("events must be a list")
        for event in events:
            if isinstance(event, dict):
                self._apply_event(event)
        latest = batch.get("latestSequence")
        if isinstance(latest, int):
            self.model.latest_sequence = latest
        return self.model

    def _load_payload(self, payload: dict[str, Any]) -> None:
        hosts = payload.get("hosts", [])
        if not isinstance(hosts, list):
            raise ValueError("hosts must be a list")
        self.model.hosts = {
            card.host_id: card
            for item in hosts
            if isinstance(item, dict)
            for card in (HostCardViewModel.from_payload(item),)
        }
        summary = payload.get("summary", {})
        self.model.active_alarm_count = int(
            summary.get("activeAlarmCount", 0)
            if isinstance(summary, dict)
            else 0
        )
        sequence = payload.get("latestSequence", 0)
        self.model.latest_sequence = sequence if isinstance(sequence, int) else 0

    def _apply_event(self, event: dict[str, Any]) -> None:
        data = event.get("data")
        if not isinstance(data, dict):
            data = {}

        projected = data.get("hostCard")
        if isinstance(projected, dict):
            card = HostCardViewModel.from_payload(projected)
            self.model.hosts[card.host_id] = card

        if event.get("eventType") == "operation.stage_changed":
            operation_id = event.get("operationId")
            stage = data.get("stage")
            if isinstance(operation_id, str) and isinstance(stage, str):
                self.model.operation_stages[operation_id] = stage
