"""Programmatic facades for replaceable user interfaces."""

from mtp6coopnw.api.control import ControlApplicationFacade
from mtp6coopnw.api.facade import ReadOnlyControlFacade

ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = [
    "ControlApplicationFacade",
    "ReadOnlyControlApi",
    "ReadOnlyControlFacade",
]
