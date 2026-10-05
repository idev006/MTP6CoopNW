from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mtp6coopnw.api import ReadOnlyControlApi, ReadOnlyControlFacade
from mtp6coopnw.cli.status import render_status
from mtp6coopnw.core import ControlCore, HostRegistry, PolicyRegistry
from mtp6coopnw.testing import FakeClock, InMemoryAuditStore

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def _facade() -> ReadOnlyControlFacade:
    core = ControlCore(
        clock=FakeClock(NOW),
        audit_store=InMemoryAuditStore(),
        hosts=HostRegistry(stale_after_seconds=10, offline_after_seconds=30),
        policies=PolicyRegistry(),
    )
    return ReadOnlyControlFacade(core)


def test_legacy_api_name_is_facade_compatible() -> None:
    facade = _facade()
    assert isinstance(facade, ReadOnlyControlApi)


def test_system_status_aggregates_hosts_alarms_and_summary() -> None:
    facade = _facade()
    facade.register_host("CLIENT-01", "client")

    status = facade.system_status()

    assert status["summary"] == {"hostCount": 1, "activeAlarmCount": 1}
    assert status["hosts"][0]["hostId"] == "CLIENT-01"
    assert status["alarms"][0]["code"] == "AGENT_NEVER_SEEN"


class FakeStatusFacade:
    def system_status(self) -> dict[str, Any]:
        return {
            "hosts": [
                {
                    "hostId": "CLIENT-X",
                    "role": "client",
                    "freshness": "ONLINE",
                    "healthy": True,
                    "policyRevision": 99,
                }
            ],
            "alarms": [],
            "summary": {"hostCount": 1, "activeAlarmCount": 0},
        }


def test_cli_depends_only_on_status_facade_contract() -> None:
    output = render_status(FakeStatusFacade())

    assert "CLIENT-X | client | ONLINE | HEALTHY | 99" in output
    assert "Hosts: 1" in output
    assert "Active alarms: 0" in output
