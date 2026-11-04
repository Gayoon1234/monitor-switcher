---
id: display
title: Display
sidebar_position: 3
---

## Model definition

This `Display` class represents the physical displays the user has as well as the available input options.

On first load of the app, the code will attempt to automatically identify the connected displays and input types however this can have varying results, as some monitors seem to have intermittent failures and it does result in an increased startup time. To mitigate this after the first run finds the input types the displays and input types are written to `config.json`.

For the InputTypes, only HDMI, ANALOG (VGA) and DVI were tested. The remaining items are from the monitor-control python library docs.

```python
class InputType(Enum):
    HDMI = "HDMI"
    ANALOG = "ANALOG"
    DVI = "DVI"
    DP = "DP"
    COMPOSITE = "COMPOSITE"

@dataclass
class DisplayInput:
    input_id: str
    input_type: InputType

@dataclass
class Display:
    id: str
    name: str
    windows_device_id: str
    inputs: list[DisplayInput]
    current_input: str | None = None
```

- `input_id` (`DisplayInput`): The internal identifier used to select a specific display input.
- `input_type` (`DisplayInput`): The supported input type reported by the display hardware.
- `id` (`Display`): The internal identifier used to store and reference the display.
- `name` (`Display`): The user-friendly display name shown in the application.
- `windows_device_id` (`Display`): The Windows device identifier associated with the display.
- `inputs` (`Display`): The available display inputs detected for the monitor.
- `current_input` (`Display`): The currently active input identifier, when one is known.
