from dataclasses import dataclass
from enum import Enum


class TriggerType(Enum):
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"


class ActionType(Enum):
    SWITCH_INPUT = "switch_input"
    DO_NOTHING = "do_nothing"


@dataclass
class Trigger:
    type: TriggerType
    device_id: str


@dataclass
class Action:
    type: ActionType
    display_id: str | None = None
    input_id: str | None = None


@dataclass
class Automation:
    id: str
    name: str
    enabled: bool
    trigger: Trigger
    actions: list[Action]