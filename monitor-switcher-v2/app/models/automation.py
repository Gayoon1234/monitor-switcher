from dataclasses import dataclass
from enum import Enum

# Right now automations are only triggered by connecting or disconnecting
# usbs, however this can be expanded later
class TriggerType(Enum):
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"

# Do nothing doesn't do anything (crazy I know) but is used for testing.
# Or to create a placeholder.
# Automations only switch the monitor input - but can be expanded later.
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
    id: str # internal use only
    name: str # "nice" name for UI
    enabled: bool # skip this automation if false
    trigger: Trigger # Trigger type + device id (i.e. when device X connects or disconnects) 
    actions: list[Action] # ActionType + display + input (i.e. switch display Y to input Z)