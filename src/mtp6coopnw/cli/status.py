from __future__ import annotations

from mtp6coopnw.api import ReadOnlyControlApi


def render_status(api: ReadOnlyControlApi) -> str:
    hosts = api.list_hosts()
    alarms = api.get_alarms()

    lines = [
        "MTP6CoopNW Central Status",
        f"Hosts: {len(hosts)}",
        f"Active alarms: {len(alarms)}",
        "",
        "HOST | ROLE | FRESHNESS | HEALTH | POLICY",
    ]

    for host in hosts:
        health = "HEALTHY" if host["healthy"] is True else (
            "DEGRADED" if host["healthy"] is False else "UNKNOWN"
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
