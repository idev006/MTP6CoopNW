"""Composition roots for assembling headless Core and Agent engines."""

from mtp6coopnw.composition.agent import AgentPorts, compose_read_only_agent
from mtp6coopnw.composition.core import CoreCompositionSettings, compose_read_only_core

__all__ = [
    "AgentPorts",
    "CoreCompositionSettings",
    "compose_read_only_agent",
    "compose_read_only_core",
]
