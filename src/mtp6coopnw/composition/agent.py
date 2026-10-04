from __future__ import annotations

from dataclasses import dataclass

from mtp6coopnw.adapters import (
    AuditStore,
    ClockPort,
    FirewallPort,
    NetworkPort,
    PolicyStore,
    ServicePort,
    SqlPort,
    TransportPort,
)
from mtp6coopnw.agent import AgentIdentity, ReadOnlyAgent
from mtp6coopnw.observability import MetricRegistry


@dataclass(frozen=True, slots=True)
class AgentPorts:
    network: NetworkPort
    firewall: FirewallPort
    sql: SqlPort
    services: ServicePort
    policy_store: PolicyStore
    audit_store: AuditStore
    transport: TransportPort


def compose_read_only_agent(
    *,
    identity: AgentIdentity,
    clock: ClockPort,
    ports: AgentPorts,
    metrics: MetricRegistry | None = None,
) -> ReadOnlyAgent:
    """Assemble an Agent from replaceable ports without selecting infrastructure."""
    return ReadOnlyAgent(
        identity=identity,
        clock=clock,
        network=ports.network,
        firewall=ports.firewall,
        sql=ports.sql,
        services=ports.services,
        policy_store=ports.policy_store,
        audit_store=ports.audit_store,
        transport=ports.transport,
        metrics=metrics or MetricRegistry(),
    )
