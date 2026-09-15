from abc import ABC, abstractmethod
from app.models.usb_device import UsbDevice

class UsbDeviceMonitor(ABC):

    @abstractmethod
    def get_devices(self) -> list[UsbDevice]:
        pass