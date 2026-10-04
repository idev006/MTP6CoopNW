"""Programmatic facades and event gateways for replaceable user interfaces."""

from mtp6coopnw.api.control import ControlApplicationFacade
from mtp6coopnw.api.events import SseEventGateway, UiEventGateway
from mtp6coopnw.api.facade import ReadOnlyControlFacade
from mtp6coopnw.api.ui import UiApplicationFacade

ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = [
    "ControlApplicationFacade",
    "ReadOnlyControlApi",
    "ReadOnlyControlFacade",
    "SseEventGateway",
    "UiApplicationFacade",
    "UiEventGateway",
]
