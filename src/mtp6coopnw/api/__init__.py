"""Programmatic facades and event gateways for replaceable user interfaces."""

from mtp6coopnw.api.control import ControlApplicationFacade
from mtp6coopnw.api.events import UiEventGateway
from mtp6coopnw.api.facade import ReadOnlyControlFacade

ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = [
    "ControlApplicationFacade",
    "ReadOnlyControlApi",
    "ReadOnlyControlFacade",
    "UiEventGateway",
]
