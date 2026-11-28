from app.hardware.usb import UsbDeviceMonitor
from app.models.usb_device import UsbDevice, ConfiguredUsbDevice
from app.events import EventHook
from app.models.config import ConfigKey
from app.services.config_repository import ConfigRepository


class UsbService:

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        repository: ConfigRepository,
    ):
        self.device_monitor = device_monitor
        self.repository = repository
        self.devices_changed: EventHook[None] = EventHook()
        self._unsubscribe_config = self.repository.config_changed.subscribe(
            self._on_config_changed
        )

    def get_devices(self) -> list[UsbDevice]:
        return self.device_monitor.get_devices()

    def get_configured_devices(self) -> list[ConfiguredUsbDevice]:
        return self.repository.get_config(ConfigKey.USB_DEVICES)

    def add_device(self, device: ConfiguredUsbDevice) -> None:
        self.repository.add_config(ConfigKey.USB_DEVICES, device)

    def remove_device(self, device_id: str) -> None:
        self.repository.remove_config(ConfigKey.USB_DEVICES, device_id)

    def update_device(self, device: ConfiguredUsbDevice) -> None:
        devices = self.get_configured_devices()

        for index, existing_device in enumerate(devices):
            if existing_device.id == device.id:
                devices[index] = device
                break

        self.repository.update_config(ConfigKey.USB_DEVICES, devices)

    def _on_config_changed(self, key: ConfigKey) -> None:
        if key is ConfigKey.USB_DEVICES:
            self.devices_changed.emit(None)