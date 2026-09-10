from dataclasses import dataclass
from enum import Enum


class InputType(Enum):
    HDMI = "HDMI"
    ANALOG = "ANALOG"
    DVI = "DVI"


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