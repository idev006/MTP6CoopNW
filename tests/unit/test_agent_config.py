from __future__ import annotations

import pathlib

from mtp6coopnw.agent import load_agent_settings


ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_agent_settings_load_from_example_toml() -> None:
    source = ROOT / "config" / "agent.example.toml"

    settings = load_agent_settings(source)

    assert settings.host_id == "CLIENT-01"
    assert settings.role == "client"
    assert settings.reconcile_seconds == 5
    assert settings.core_url.startswith("https://")
    assert settings.fail_safe == "last_known_valid"
    assert settings.local_policy_path.is_absolute()
    assert settings.network_adapter == "windows-powershell"
