"""Compatibility module for the original read-only API name."""

from mtp6coopnw.api.facade import ReadOnlyControlFacade

ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = ["ReadOnlyControlApi", "ReadOnlyControlFacade"]
