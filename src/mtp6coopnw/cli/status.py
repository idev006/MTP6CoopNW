from __future__ import annotations

from typing import Any, Protocol


class StatusFacade(Protocol):
    def system_status(self) -> dict[str, Any]: ...


def render_status(api: StatusFacade) -> str:
    status = api.system_status()
    hosts = status["hosts"]
    alarms = status["alarms"]

    lines = [
        "MTP6CoopNW Central Status",
        f"Hosts: {status['summary']['hostCount']}",
        f"Active alarms: {status['summary']['activeAlarmCount']}",
        "",
        "HOST | ROLE | FRESHNESS | HEALTH | POLICY",
    ]

    for host in hosts:
        health = (
            "HEALTHY"
            if host["healthy"] is True
            else ("DEGRADED" if host["healthy"] is False else "UNKNOWN")
        )
        revision = host["policyRevision"]
        lines.append(
            f"{host['hostId']} | {host['role']} | {host['freshness']} | "
            f"{health} | {revision if revision is not None else '-'}"
        )

    if alarms:
        lines.extend(["", "ALARMS"])
        for alarm in alarms:
            lines.append(
                f"{alarm['severity']} {alarm['hostId']} {alarm['code']}: "
                f"{alarm['message']}"
            )

    return "\n".join(lines)
