from __future__ import annotations

import pathlib

import pytest

from mtp6coopnw.config import (
    ConfigError,
    load_toml,
    validate_agent_config,
    validate_core_config,
    validate_logging_config,
    validate_policy_config,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("filename", "validator"),
    [
        ("core.example.toml", validate_core_config),
        ("agent.example.toml", validate_agent_config),
        ("policy.example.toml", validate_policy_config),
        ("logging.example.toml", validate_logging_config),
    ],
)
def test_example_configs_are_valid(filename: str, validator: object) -> None:
    loaded = load_toml(ROOT / "config" / filename)
    assert len(loaded.sha256) == 64

    assert callable(validator)
    validator(loaded.data)  # type: ignore[operator]


def test_loader_hash_is_stable() -> None:
    path = ROOT / "config" / "core.example.toml"
    first = load_toml(path)
    second = load_toml(path)
    assert first.sha256 == second.sha256


def test_core_rejects_invalid_telemetry_order() -> None:
    loaded = load_toml(ROOT / "config" / "core.example.toml")
    loaded.data["telemetry"]["offline_after_seconds"] = 2

    with pytest.raises(ConfigError, match="heartbeat < stale < offline"):
        validate_core_config(loaded.data)


def test_agent_requires_https_core_url() -> None:
    loaded = load_toml(ROOT / "config" / "agent.example.toml")
    loaded.data["core"]["url"] = "http://192.168.1.101:8443"

    with pytest.raises(ConfigError, match="https"):
        validate_agent_config(loaded.data)


def test_policy_rejects_invalid_database_port() -> None:
    loaded = load_toml(ROOT / "config" / "policy.example.toml")
    loaded.data["database"]["port"] = 70000

    with pytest.raises(ConfigError, match="between 1 and 65535"):
        validate_policy_config(loaded.data)
