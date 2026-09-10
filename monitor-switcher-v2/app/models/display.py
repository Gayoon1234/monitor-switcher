from dataclasses import dataclass
from enum import Enum


class InputType(Enum):
    HDMI = "HDMI"
    ANALOG = "ANALOG"
    DVI = "DVI"


# This represents the inputs that the monitor can take
@dataclass
class DisplayInput:
    input_id: str
    input_type: InputType

# This represents a display/monitor/screen
@dataclass
class Display:
    id: str
    name: str
    inputs: list[DisplayInput]