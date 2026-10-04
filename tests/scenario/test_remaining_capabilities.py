from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from mtp6coopnw.api.commands import NetworkControlFacade
from mtp6coopnw.core.alarm_lifecycle import AlarmLifecycleStore
from mtp6coopnw.network import Direction, NetworkPolicy, PortRule, Protocol
from mtp6coopnw.operations.idempotency import IdempotencyStore
from mtp6coopnw.persistence import AtomicJsonPolicyStore
from mtp6coopnw.policy.advanced import (
    SpecialDateRule,
    TemporaryGrant,
    resolve_temporal_override,
)
from mtp6coopnw.resilience import recover_agent_policy
from mtp6coopnw.security import (
    ActorContext,
    AgentInitiatedSessionGuard,
    HostIdentityRegistry,
    Role,
    SqlCredentialPolicy,
    authorize,
    certificate_fingerprint,
    mutation_audit,
)

pytestmark = pytest.mark.scenario
NOW = datetime(2026, 10, 4, 8, 0, tzinfo=UTC)


def test_holiday_exception_and_temporary_access_auto_expiry() -> None:
    special = (SpecialDateRule(date(2026, 10, 4), False),)
    assert resolve_temporal_override(now=NOW, default=True, special_dates=special) is False

    grant = TemporaryGrant(True, NOW, NOW + timedelta(minutes=30))
    assert (
        resolve_temporal_override(
            now=NOW + timedelta(minutes=5),
            default=False,
            temporary=grant,
        )
        is True
    )
    assert (
        resolve_temporal_override(
            now=NOW + timedelta(minutes=30),
            default=False,
            temporary=grant,
        )
        is False
    )


def test_network_rules_support_protocol_direction_destination_and_sql_wan_guard() -> None:
    policy = NetworkPolicy(
        False,
        True,
        (
            PortRule(
                Protocol.TCP,
                1433,
                Direction.OUTBOUND,
                "192.168.1.10",
                True,
            ),
            PortRule(
                Protocol.UDP,
                53,
                Direction.OUTBOUND,
                "192.168.1.1",
                True,
            ),
        ),
    )
    policy.validate_db_safety(db_server_ip="192.168.1.10")
    assert policy.allows(
        protocol=Protocol.TCP,
        port=1433,
        direction=Direction.OUTBOUND,
        destination="192.168.1.10",
    )

    unsafe = NetworkPolicy(
        False,
        True,
        (
            PortRule(
                Protocol.TCP,
                1433,
                Direction.INBOUND,
                "WAN",
                True,
            ),
        ),
    )
    with pytest.raises(ValueError, match="WAN"):
        unsafe.validate_db_safety(db_server_ip="192.168.1.10")


def test_operation_retry_is_idempotent_and_payload_conflict_is_rejected() -> None:
    store = IdempotencyStore[int]()
    calls = 0

    def action() -> int:
        nonlocal calls
        calls += 1
        return 42

    result, replayed = store.execute_once("op-1", {"host": "CLIENT-01"}, action)
    assert (result, replayed, calls) == (42, False, 1)

    result, replayed = store.execute_once("op-1", {"host": "CLIENT-01"}, action)
    assert (result, replayed, calls) == (42, True, 1)

    with pytest.raises(ValueError):
        store.execute_once("op-1", {"host": "CLIENT-02"}, action)


def test_atomic_policy_persistence_survives_process_recreation(tmp_path) -> None:
    path = tmp_path / "policy.json"
    first = AtomicJsonPolicyStore(path)
    first.save(
        "CLIENT-01",
        {"policy_revision": 7, "internet": {"allowed": False}},
    )

    second = AtomicJsonPolicyStore(path)
    restored = second.get("CLIENT-01")

    assert restored is not None
    assert restored["policy_revision"] == 7


def test_role_authorization_and_host_certificate_binding() -> None:
    authorize(ActorContext("alice", Role.OPERATOR), "operate")
    with pytest.raises(PermissionError):
        authorize(ActorContext("viewer", Role.VIEWER), "operate")

    certificate = b"fake-client-cert"
    registry = HostIdentityRegistry(
        {"CLIENT-01": certificate_fingerprint(certificate)}
    )
    registry.verify("CLIENT-01", certificate)
    with pytest.raises(PermissionError):
        registry.verify("CLIENT-01", b"other")


def test_agent_initiated_transport_rejects_replay_and_core_initiation() -> None:
    certificate = b"client-cert"
    guard = AgentInitiatedSessionGuard(
        HostIdentityRegistry(
            {"CLIENT-01": certificate_fingerprint(certificate)}
        )
    )

    assert (
        guard.accept(
            host_id="CLIENT-01",
            certificate=certificate,
            sequence=1,
            initiated_by_agent=True,
        )
        == "ACCEPTED"
    )
    assert (
        guard.accept(
            host_id="CLIENT-01",
            certificate=certificate,
            sequence=1,
            initiated_by_agent=True,
        )
        == "REPLAY"
    )
    with pytest.raises(PermissionError):
        guard.accept(
            host_id="CLIENT-01",
            certificate=certificate,
            sequence=2,
            initiated_by_agent=False,
        )


def test_agent_restart_recovers_last_known_valid_or_enters_safe_hold(tmp_path) -> None:
    store = AtomicJsonPolicyStore(tmp_path / "policy.json")
    assert recover_agent_policy("CLIENT-01", store).mode == "SAFE_HOLD"

    store.save(
        "CLIENT-01",
        {"policy_revision": 9, "internet": {"allowed": False}},
    )
    recovered = recover_agent_policy(
        "CLIENT-01",
        AtomicJsonPolicyStore(tmp_path / "policy.json"),
    )
    assert recovered.mode == "LAST_KNOWN_VALID"
    assert recovered.policy is not None
    assert recovered.policy["policy_revision"] == 9


def test_alarm_acknowledge_and_clear_lifecycle() -> None:
    store = AlarmLifecycleStore()
    alarm, created = store.raise_alarm(
        "CLIENT-01",
        "AGENT_OFFLINE",
        NOW,
    )
    assert created and alarm.active

    store.acknowledge(
        "CLIENT-01",
        "AGENT_OFFLINE",
        "operator-1",
        NOW + timedelta(seconds=1),
    )
    assert alarm.acknowledged_by == "operator-1"

    alarm, cleared = store.clear(
        "CLIENT-01",
        "AGENT_OFFLINE",
        NOW + timedelta(seconds=2),
    )
    assert cleared and not alarm.active


def test_mutation_audit_identifies_actor_target_action_and_result() -> None:
    actor = ActorContext("operator-17", Role.OPERATOR)
    event = mutation_audit(
        actor=actor,
        action="internet.disable",
        host_id="CLIENT-02",
        now=NOW,
        result="COMPLETED",
        operation_id="op-9",
    )
    payload = event.to_dict()

    assert payload["actorId"] == "operator-17"
    assert payload["hostId"] == "CLIENT-02"
    assert payload["action"] == "internet.disable"
    assert payload["result"] == "COMPLETED"


def test_sql_application_credentials_are_least_privilege() -> None:
    with pytest.raises(ValueError):
        SqlCredentialPolicy("sa", ("select",)).validate()
    with pytest.raises(ValueError):
        SqlCredentialPolicy("coop_app", ("sysadmin",)).validate()
    SqlCredentialPolicy("coop_app", ("select", "execute")).validate()


class _Audit:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def append(self, event: dict[str, object]) -> None:
        self.events.append(event)


class _Executor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object], datetime]] = []

    def apply(
        self,
        *,
        host_id: str,
        desired: dict[str, object],
        now: datetime,
    ) -> dict[str, object]:
        self.calls.append((host_id, desired, now))
        return {"operationId": "op-1", "stage": "COMPLETED"}


def test_command_facade_controls_host_internet_database_and_ports_with_audit() -> None:
    audit = _Audit()
    executor = _Executor()
    facade = NetworkControlFacade(executor, audit)
    admin = ActorContext("admin-1", Role.ADMIN)

    assert (
        facade.set_host_enabled(
            actor=admin,
            host_id="CLIENT-01",
            enabled=False,
            now=NOW,
        )["stage"]
        == "COMPLETED"
    )
    facade.set_internet_allowed(
        actor=admin,
        host_id="CLIENT-01",
        allowed=False,
        now=NOW,
    )
    facade.set_database_allowed(
        actor=admin,
        host_id="CLIENT-01",
        allowed=True,
        now=NOW,
    )
    facade.set_port_rules(
        actor=admin,
        host_id="CLIENT-01",
        rules=[
            {
                "protocol": "TCP",
                "port": 1433,
                "direction": "OUTBOUND",
                "destination": "192.168.1.10",
            }
        ],
        now=NOW,
    )

    assert len(executor.calls) == 4
    assert all(event["actorId"] == "admin-1" for event in audit.events)

    with pytest.raises(PermissionError):
        facade.set_internet_allowed(
            actor=ActorContext("viewer-1", Role.VIEWER),
            host_id="CLIENT-01",
            allowed=True,
            now=NOW,
        )
