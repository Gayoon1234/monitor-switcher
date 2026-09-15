from PySide6.QtCore import QObject, QTimer, Signal

from app.hardware.usb import UsbDeviceMonitor
from app.models.device_event import (
    DeviceEvent,
    DeviceEventType,
)


class UsbMonitorService(QObject):

    device_event = Signal(object)

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        device_id: str,
    ):
        super().__init__()

        self.device_monitor = device_monitor
        self.device_id = device_id

        self.previous_connected = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._check_device)

    def start(self, interval_ms: int = 500) -> None:
        self.previous_connected = self._is_connected()
        self.timer.start(interval_ms)

    def stop(self) -> None:
        self.timer.stop()

    def _check_device(self) -> None:
        connected = self._is_connected()

        if connected == self.previous_connected:
            return

        self.previous_connected = connected

        event_type = (
            DeviceEventType.CONNECTED
            if connected
            else DeviceEventType.DISCONNECTED
        )

        self.device_event.emit(
            DeviceEvent(
                device_id=self.device_id,
                event_type=event_type,
            )
        )

    def _is_connected(self) -> bool:
        devices = self.device_monitor.get_devices()

        return any(
            device.windows_device_id == self.device_id
            for device in devices
        )