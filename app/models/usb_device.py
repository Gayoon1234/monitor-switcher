from dataclasses import dataclass

# This represents any USB device that is connected but not configured.
@dataclass
class UsbDevice:
    windows_device_id: str
    name: str

# This represents a USB device that has been configured in the app
@dataclass
class ConfiguredUsbDevice:
    id: str
    windows_device_id: str
    nickname: str