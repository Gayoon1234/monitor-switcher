from app.hardware.usb import UsbDeviceMonitor
from app.models.usb_device import UsbDevice, ConfiguredUsbDevice
from app.services.config_repository import ConfigRepository


class UsbService:

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        repository: ConfigRepository,
    ):
        self.device_monitor = device_monitor
        self.repository = repository

    def get_devices(self) -> list[UsbDevice]:
        return self.device_monitor.get_devices()

    def get_configured_devices(self) -> list[ConfiguredUsbDevice]:
        return self.repository.load_usb_devices()

    def add_device(self, device: ConfiguredUsbDevice) -> None:
        devices = self.get_configured_devices()

        devices.append(device)

        self.repository.save_usb_devices(devices)

    def remove_device(self, device_id: str) -> None:
        devices = self.get_configured_devices()

        devices = [
            device
            for device in devices
            if device.id != device_id
        ]

        self.repository.save_usb_devices(devices)