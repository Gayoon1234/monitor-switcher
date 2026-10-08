from dataclasses import dataclass
from enum import Enum

# DP and Composite are not tested, neither are displays with multiple inputs of the same type. 
class InputType(Enum):
    HDMI = "HDMI"
    ANALOG = "ANALOG"
    DVI = "DVI"
    DP = "DP"
    COMPOSITE = "COMPOSITE"


@dataclass
class DisplayInput:
    input_id: str # used internally to identify a specific input on a display
    input_type: InputType # what monitor control sends back


@dataclass
class Display:
    id: str # internal uuid
    name: str # "nice" name for UI
    windows_device_id: str 
    inputs: list[DisplayInput]
    current_input: str | None = None