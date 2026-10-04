from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from mtp6coopnw.ui import DashboardPresenter


@dataclass(slots=True)
class FakeDashboardFacade:
    bootstrap: dict[str, Any]
    batches: list[dict[str, Any]] = field(default_factory=list)
    calls: int = 0

    def bootstrap_dashboard(self) -> dict[str, Any]:
        self.calls += 1
        return copy.deepcopy(self.bootstrap)

    def next_ui_events(
        self,
        *,
        after_sequence: int,
        timeout_seconds: float = 30.0,
        limit: int = 100,
    ) -> dict[str, Any]:
        del after_sequence, timeout_seconds, limit
        if self.batches:
            return copy.deepcopy(self.batches.pop(0))
        return {
            "events": [],
            "latestSequence": int(self.bootstrap["latestSequence"]),
            "resyncRequired": False,
        }


def _card(*, freshness: str = "ONLINE", can_apply: bool = True) -> dict[str, Any]:
    return {
        "hostId": "CLIENT-01",
        "role": "client",
        "freshness": freshness,
        "health": "HEALTHY",
        "policyRevision": 1,
        "lastHeartbeat": "2026-10-04T15:00:00+00:00",
        "alarmCount": 0,
        "actions": {
            "canViewDetails": True,
            "canPlan": can_apply,
            "canApply": can_apply,
            "canRetry": not can_apply,
            "canEnterMaintenance": freshness == "ONLINE",
        },
    }


def _bootstrap() -> dict[str, Any]:
    return {
        "hosts": [_card()],
        "alarms": [],
        "summary": {"hostCount": 1, "activeAlarmCount": 0},
        "latestSequence": 10,
    }


def test_ui_presenter_loads_entirely_from_fake_facade() -> None:
    backend = FakeDashboardFacade(_bootstrap())
    presenter = DashboardPresenter.create(backend)

    model = presenter.load()

    assert backend.calls == 1
    assert model.hosts["CLIENT-01"].freshness == "ONLINE"
    assert model.hosts["CLIENT-01"].actions["canApply"] is True
    assert model.latest_sequence == 10


def test_ui_presenter_applies_facade_projection_without_engine() -> None:
    backend = FakeDashboardFacade(
        _bootstrap(),
        batches=[
            {
                "events": [
                    {
                        "eventType": "host.freshness_changed",
                        "sequence": 11,
                        "hostId": "CLIENT-01",
                        "data": {
                            "from": "ONLINE",
                            "to": "OFFLINE",
                            "hostCard": _card(
                                freshness="OFFLINE",
                                can_apply=False,
                            ),
                        },
                    }
                ],
                "latestSequence": 11,
                "resyncRequired": False,
            }
        ],
    )
    presenter = DashboardPresenter.create(backend)
    presenter.load()

    model = presenter.refresh_from_events()

    host = model.hosts["CLIENT-01"]
    assert host.freshness == "OFFLINE"
    assert host.actions["canApply"] is False
    assert host.actions["canRetry"] is True
    assert model.latest_sequence == 11


def test_ui_presenter_tracks_operation_progress_from_events() -> None:
    backend = FakeDashboardFacade(
        _bootstrap(),
        batches=[
            {
                "events": [
                    {
                        "eventType": "operation.stage_changed",
                        "sequence": 11,
                        "operationId": "op-1",
                        "data": {"stage": "APPLYING"},
                    },
                    {
                        "eventType": "operation.stage_changed",
                        "sequence": 12,
                        "operationId": "op-1",
                        "data": {"stage": "VERIFYING"},
                    },
                ],
                "latestSequence": 12,
                "resyncRequired": False,
            }
        ],
    )
    presenter = DashboardPresenter.create(backend)
    presenter.load()

    model = presenter.refresh_from_events()

    assert model.operation_stages["op-1"] == "VERIFYING"


def test_ui_presenter_resyncs_snapshot_after_replay_gap() -> None:
    bootstrap = _bootstrap()
    backend = FakeDashboardFacade(
        bootstrap,
        batches=[
            {
                "events": [],
                "latestSequence": 99,
                "resyncRequired": True,
            }
        ],
    )
    presenter = DashboardPresenter.create(backend)
    presenter.load()
    bootstrap["latestSequence"] = 100

    model = presenter.refresh_from_events()

    assert backend.calls == 2
    assert model.resync_count == 1
    assert model.latest_sequence == 100


def test_unknown_ui_event_is_forward_compatible() -> None:
    backend = FakeDashboardFacade(
        _bootstrap(),
        batches=[
            {
                "events": [
                    {
                        "eventType": "future.feature",
                        "sequence": 11,
                        "data": {"anything": True},
                    }
                ],
                "latestSequence": 11,
                "resyncRequired": False,
            }
        ],
    )
    presenter = DashboardPresenter.create(backend)
    presenter.load()

    model = presenter.refresh_from_events()

    assert model.hosts["CLIENT-01"].freshness == "ONLINE"
    assert model.latest_sequence == 11
