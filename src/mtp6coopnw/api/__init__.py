"""Programmatic facades and gateways for replaceable presentation shells."""

from mtp6coopnw.application import CommandExecutionResult, StateReporter
from mtp6coopnw.api.commands import NetworkControlFacade
from mtp6coopnw.api.desktop import DesktopActionFacade
from mtp6coopnw.api.control import ControlApplicationFacade
from mtp6coopnw.api.engine_executor import EngineCommandExecutor
from mtp6coopnw.api.events import SseEventGateway, UiEventGateway
from mtp6coopnw.api.facade import ReadOnlyControlFacade
from mtp6coopnw.api.ui import UiApplicationFacade

ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = [
    "CommandExecutionResult",
    "ControlApplicationFacade",
    "DesktopActionFacade",
    "EngineCommandExecutor",
    "NetworkControlFacade",
    "ReadOnlyControlApi",
    "ReadOnlyControlFacade",
    "SseEventGateway",
    "StateReporter",
    "UiApplicationFacade",
    "UiEventGateway",
]
