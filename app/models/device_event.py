from dataclasses import dataclass
from enum import Enum

# TODO: Merge with TriggerType in automation.py
class DeviceEventType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

@dataclass
class DeviceEvent:
    device_id: str
    event_type: DeviceEventType