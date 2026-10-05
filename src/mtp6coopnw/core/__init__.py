"""Central control-domain package.

No Windows-specific implementation belongs in this package.
"""

from mtp6coopnw.core.alarm_lifecycle import AlarmLifecycleStore, AlarmState
from mtp6coopnw.core.alarms import CentralAlarm
from mtp6coopnw.core.control import ControlCore, TelemetryIngestError
from mtp6coopnw.core.registry import HostRegistry, HostView, PolicyRegistry

__all__ = [
    "AlarmLifecycleStore",
    "AlarmState",
    "CentralAlarm",
    "ControlCore",
    "HostRegistry",
    "HostView",
    "PolicyRegistry",
    "TelemetryIngestError",
]
