from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mtp6coopnw.config import load_toml, validate_agent_config


@dataclass(frozen=True, slots=True)
class AgentSettings:
    host_id: str
    role: str
    reconcile_seconds: int
    core_url: str
    local_policy_path: Path
    fail_safe: str
    network_adapter: str
    firewall_adapter: str
    service_adapter: str
    sql_adapter: str


def load_agent_settings(path: Path) -> AgentSettings:
    loaded = load_toml(path)
    validate_agent_config(loaded.data)

    agent = loaded.data["agent"]
    core = loaded.data["core"]
    local_policy = loaded.data["local_policy"]
    adapters = loaded.data["adapters"]

    policy_path = Path(str(local_policy["path"]))
    if not policy_path.is_absolute():
        policy_path = (path.parent / policy_path).resolve()

    return AgentSettings(
        host_id=str(agent["host_id"]),
        role=str(agent["role"]),
        reconcile_seconds=int(agent["reconcile_seconds"]),
        core_url=str(core["url"]),
        local_policy_path=policy_path,
        fail_safe=str(local_policy["fail_safe"]),
        network_adapter=str(adapters["network"]),
        firewall_adapter=str(adapters["firewall"]),
        service_adapter=str(adapters["services"]),
        sql_adapter=str(adapters["sql"]),
    )
