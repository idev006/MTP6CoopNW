"""Programmatic facades for replaceable user interfaces."""

from mtp6coopnw.api.facade import ReadOnlyControlFacade

# Backward-compatible name retained while presentation code migrates to "Facade".
ReadOnlyControlApi = ReadOnlyControlFacade

__all__ = ["ReadOnlyControlApi", "ReadOnlyControlFacade"]
