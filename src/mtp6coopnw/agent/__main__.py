from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mtp6coopnw.adapters.windows import (
    PowerShellFirewallPort,
    PowerShellNetworkPort,
    PowerShellReadOnlyBridge,
    PowerShellServicePort,
    PowerShellSqlPort,
)
from mtp6coopnw.agent.config import AgentSettings, load_agent_settings
from mtp6coopnw.agent.runtime import AgentIdentity
from mtp6coopnw.composition.agent import AgentPorts, compose_read_only_agent
from mtp6coopnw.testing import InMemoryAuditStore, InMemoryPolicyStore


@dataclass(slots=True)
class _SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass(slots=True)
class _ConsoleTransport:
    """Temporary read-only transport until the Core transport adapter is wired."""

    core_url: str

    def send(self, target: str, message: dict[str, Any]) -> None:
        print(
            json.dumps(
                {
                    "transport": "console",
                    "target": target,
                    "coreUrl": self.core_url,
                    "message": message,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            flush=True,
        )


def _build_agent(settings: AgentSettings):
    project_root = Path(__file__).resolve().parents[3]
    powershell_root = project_root / "powershell"
    bridge = PowerShellReadOnlyBridge(module_root=powershell_root)

    ports = AgentPorts(
        network=PowerShellNetworkPort(bridge=bridge),
        firewall=PowerShellFirewallPort(bridge=bridge),
        sql=PowerShellSqlPort(bridge=bridge, computer_name="localhost"),
        services=PowerShellServicePort(bridge=bridge, names=()),
        policy_store=InMemoryPolicyStore(),
        audit_store=InMemoryAuditStore(),
        transport=_ConsoleTransport(core_url=settings.core_url),
    )

    identity = AgentIdentity(
        host_id=settings.host_id,
        role=settings.role,
        version="0.1.0.dev0",
    )
    return compose_read_only_agent(
        identity=identity,
        clock=_SystemClock(),
        ports=ports,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mtp6coopnw.agent",
        description="Start the MTP6CoopNW read-only Client Agent.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/agent.toml"),
        help="Path to the Agent TOML configuration file.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Collect one read-only snapshot/heartbeat and exit.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run local read-only adapter checks and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config_path = args.config.resolve()

    if not config_path.is_file():
        print(f"[MTP6CoopNW] Agent config not found: {config_path}", file=sys.stderr)
        return 2

    try:
        settings = load_agent_settings(config_path)
        agent = _build_agent(settings)
    except Exception as exc:
        print(
            f"[MTP6CoopNW] Agent startup failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"[MTP6CoopNW] Client Agent starting: "
        f"host={settings.host_id} role={settings.role} "
        f"interval={settings.reconcile_seconds}s"
    )
    print(
        "[MTP6CoopNW] MODE: READ-ONLY LOCAL/CONSOLE TRANSPORT. "
        "Core network transport is not wired yet."
    )

    try:
        if args.self_test:
            snapshot = agent.self_test()
            print(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2))
            return 0 if snapshot.healthy else 3

        if args.once:
            snapshot = agent.run_once()
            print(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2))
            return 0 if snapshot.healthy else 3

        while True:
            snapshot = agent.run_once()
            state = "HEALTHY" if snapshot.healthy else "DEGRADED"
            print(
                f"[MTP6CoopNW] {settings.host_id} {state} "
                f"captured={snapshot.captured_at.isoformat()}",
                flush=True,
            )
            time.sleep(settings.reconcile_seconds)
    except KeyboardInterrupt:
        print("\n[MTP6CoopNW] Client Agent stopped by user.")
        return 0
    except Exception as exc:
        print(
            f"[MTP6CoopNW] Agent runtime failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
