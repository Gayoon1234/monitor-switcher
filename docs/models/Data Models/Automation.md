---
id: automation
title: Automation
sidebar_position: 1
---

## Automations

The `Automation` model is used to store the sequence of events that should happen when a device is connected/disconnected.

Conceptually it is made up of one trigger (i.e. when USB device A connects) and a list of actions that will be executed (i.e. switch the input of display 1 to HDMI). It's a one-to-many relationship and there are no set bounds on the number of actions that a trigger will handle.

Automations can be created/modified/deleted on the Automations tab in the UI.

Automations are stored in the config.json file.

## Model definition

```python
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
```

- `id`: Internal identifier used by configuration and automation services.
- `name`: Display name shown in the UI.
- `enabled`: Determines whether the automation is evaluated.
- `trigger`: Defines the USB event and device that trigger the automation.
- `actions`: Defines the work performed after the trigger matches.
