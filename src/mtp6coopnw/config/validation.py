from __future__ import annotations

import ipaddress
from datetime import time
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from mtp6coopnw.config.loader import ConfigError


_ALLOWED_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
_ALLOWED_ROLES = {"client", "database_server", "control"}
_ALLOWED_PROTOCOLS = {"tcp", "udp"}
_ALLOWED_FAIL_SAFE = {"last_known_valid"}


def _require_table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Expected TOML table [{key}]")
    return value


def _require_int(table: dict[str, Any], key: str, *, minimum: int | None = None) -> int:
    value = table.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(f"Expected integer: {key}")
    if minimum is not None and value < minimum:
        raise ConfigError(f"{key} must be >= {minimum}")
    return value


def _require_bool(table: dict[str, Any], key: str) -> bool:
    value = table.get(key)
    if not isinstance(value, bool):
        raise ConfigError(f"Expected boolean: {key}")
    return value


def _require_str(table: dict[str, Any], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Expected non-empty string: {key}")
    return value.strip()


def _validate_schema_version(data: dict[str, Any]) -> None:
    version = data.get("schema_version")
    if version != 1:
        raise ConfigError("schema_version must be 1")


def _validate_timezone(value: str) -> None:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Unknown timezone: {value}") from exc


def _validate_port(value: int, field: str) -> None:
    if value < 1 or value > 65535:
        raise ConfigError(f"{field} must be between 1 and 65535")


def _validate_time(value: str, field: str) -> None:
    try:
        time.fromisoformat(value)
    except ValueError as exc:
        raise ConfigError(f"{field} must be an ISO time such as 08:00") from exc


def validate_core_config(data: dict[str, Any]) -> None:
    _validate_schema_version(data)

    core = _require_table(data, "core")
    _require_str(core, "node_id")
    _validate_timezone(_require_str(core, "timezone"))

    telemetry = _require_table(data, "telemetry")
    heartbeat = _require_int(telemetry, "heartbeat_seconds", minimum=1)
    stale = _require_int(telemetry, "stale_after_seconds", minimum=1)
    offline = _require_int(telemetry, "offline_after_seconds", minimum=1)
    if not heartbeat < stale < offline:
        raise ConfigError("telemetry timing must satisfy heartbeat < stale < offline")

    cycles = _require_table(data, "cycles")
    _require_int(cycles, "fast_seconds", minimum=1)
    _require_int(cycles, "slow_seconds", minimum=1)
    _require_int(cycles, "reconcile_seconds", minimum=1)

    timeouts = _require_table(data, "timeouts")
    for key in (
        "validate_seconds",
        "plan_seconds",
        "apply_seconds",
        "verify_seconds",
        "rollback_seconds",
        "approval_seconds",
    ):
        _require_int(timeouts, key, minimum=1)

    transport = _require_table(data, "transport")
    _require_str(transport, "mode")
    _require_str(transport, "bind")
    port = _require_int(transport, "port", minimum=1)
    _validate_port(port, "transport.port")

    logging = _require_table(data, "logging")
    _require_str(logging, "level")
    _require_str(logging, "format")


def validate_agent_config(data: dict[str, Any]) -> None:
    _validate_schema_version(data)

    agent = _require_table(data, "agent")
    _require_str(agent, "host_id")
    role = _require_str(agent, "role")
    if role not in _ALLOWED_ROLES:
        raise ConfigError(f"Unsupported agent.role: {role}")
    _require_int(agent, "reconcile_seconds", minimum=1)

    core = _require_table(data, "core")
    core_url = _require_str(core, "url")
    if not core_url.startswith("https://"):
        raise ConfigError("core.url must use https://")

    local_policy = _require_table(data, "local_policy")
    _require_str(local_policy, "path")
    fail_safe = _require_str(local_policy, "fail_safe")
    if fail_safe not in _ALLOWED_FAIL_SAFE:
        raise ConfigError(f"Unsupported local_policy.fail_safe: {fail_safe}")

    adapters = _require_table(data, "adapters")
    for key in ("network", "firewall", "services", "sql"):
        _require_str(adapters, key)


def validate_policy_config(data: dict[str, Any]) -> None:
    _validate_schema_version(data)
    revision = data.get("policy_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ConfigError("policy_revision must be an integer >= 1")

    host = _require_table(data, "host")
    _require_bool(host, "enabled")

    internet = _require_table(data, "internet")
    _require_bool(internet, "allowed")

    database = _require_table(data, "database")
    _require_bool(database, "allowed")
    server = _require_str(database, "server")
    try:
        ipaddress.ip_address(server)
    except ValueError as exc:
        raise ConfigError(f"database.server must be an IP address: {server}") from exc
    db_port = _require_int(database, "port", minimum=1)
    _validate_port(db_port, "database.port")

    schedules = data.get("schedule", [])
    if not isinstance(schedules, list):
        raise ConfigError("[[schedule]] must be an array of tables")
    for index, schedule in enumerate(schedules):
        if not isinstance(schedule, dict):
            raise ConfigError(f"schedule[{index}] must be a table")

        days = schedule.get("days")
        if not isinstance(days, list) or not days:
            raise ConfigError(f"schedule[{index}].days must be a non-empty array")
        if any(not isinstance(day, str) or day not in _ALLOWED_DAYS for day in days):
            raise ConfigError(f"schedule[{index}].days contains an unsupported day")

        _validate_time(_require_str(schedule, "start"), f"schedule[{index}].start")
        _validate_time(_require_str(schedule, "end"), f"schedule[{index}].end")
        _validate_timezone(_require_str(schedule, "timezone"))

    ports = data.get("ports", {})
    if not isinstance(ports, dict):
        raise ConfigError("[ports] must be a table")
    allow_rules = ports.get("allow", [])
    if not isinstance(allow_rules, list):
        raise ConfigError("[[ports.allow]] must be an array of tables")

    for index, rule in enumerate(allow_rules):
        if not isinstance(rule, dict):
            raise ConfigError(f"ports.allow[{index}] must be a table")

        protocol = _require_str(rule, "protocol").lower()
        if protocol not in _ALLOWED_PROTOCOLS:
            raise ConfigError(f"ports.allow[{index}].protocol must be tcp or udp")

        remote_port = _require_int(rule, "remote_port", minimum=1)
        _validate_port(remote_port, f"ports.allow[{index}].remote_port")

        remote_address = _require_str(rule, "remote_address")
        try:
            ipaddress.ip_network(remote_address, strict=False)
        except ValueError as exc:
            raise ConfigError(
                f"ports.allow[{index}].remote_address must be an IP/network"
            ) from exc


def validate_logging_config(data: dict[str, Any]) -> None:
    _validate_schema_version(data)
    logging = _require_table(data, "logging")
    _require_str(logging, "level")
    _require_str(logging, "format")
    _require_bool(logging, "include_correlation_id")
    _require_bool(logging, "redact_secrets")
