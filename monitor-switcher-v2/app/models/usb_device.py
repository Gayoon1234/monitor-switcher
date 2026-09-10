from dataclasses import dataclass

# This represents a usb device. In my case its a usb-hub/switch.
@dataclass
class UsbDevice:
    id: str
    windows_device_id: str
    name: str