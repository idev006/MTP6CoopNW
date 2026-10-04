"""Composition roots for assembling headless Core, Agent and control runtimes."""

from mtp6coopnw.composition.agent import AgentPorts, compose_read_only_agent
from mtp6coopnw.composition.control import (
    ControlRuntime,
    ManagedHostSpec,
    compose_control_runtime,
)
from mtp6coopnw.composition.core import CoreCompositionSettings, compose_read_only_core

__all__ = [
    "AgentPorts",
    "ControlRuntime",
    "CoreCompositionSettings",
    "ManagedHostSpec",
    "compose_control_runtime",
    "compose_read_only_agent",
    "compose_read_only_core",
]
