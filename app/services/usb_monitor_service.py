import logging

from PySide6.QtCore import QObject, QTimer, Signal

from app.hardware.usb import UsbDeviceMonitor
from app.models.device_event import DeviceEvent, DeviceEventType


logger = logging.getLogger(__name__)


class UsbMonitorService(QObject):

    device_event = Signal(object)

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        device_id: str | None = None,
    ):
        super().__init__()

        self.device_monitor = device_monitor
        self.device_id = device_id

        self.previous_connected: bool | set[str] = (
            set() if device_id is None else False
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self._check_device)

    def start(self, interval_ms: int = 500) -> None:
        if self.device_id is None:
            self.previous_connected = self._current_device_ids()
        else:
            self.previous_connected = self._is_connected()
        self.timer.start(interval_ms)

    def stop(self) -> None:
        self.timer.stop()

    def _check_device(self) -> None:
        try:
            if self.device_id is None:
                self._check_all_devices()
                return

            connected = self._is_connected()
        except Exception:
            logger.exception(
                "Failed to check USB device state for %s",
                self.device_id,
            )
            return

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

    def _check_all_devices(self) -> None:
        current_ids = self._current_device_ids()
        previous_ids = set(self.previous_connected)

        for device_id in sorted(current_ids - previous_ids):
            self.device_event.emit(
                DeviceEvent(
                    device_id=device_id,
                    event_type=DeviceEventType.CONNECTED,
                )
            )

        for device_id in sorted(previous_ids - current_ids):
            self.device_event.emit(
                DeviceEvent(
                    device_id=device_id,
                    event_type=DeviceEventType.DISCONNECTED,
                )
            )

        self.previous_connected = current_ids

    def _current_device_ids(self) -> set[str]:
        devices = self.device_monitor.get_devices()
        return {
            device.windows_device_id
            for device in devices
        }

    def _is_connected(self) -> bool:
        devices = self.device_monitor.get_devices()

        return any(
            device.windows_device_id == self.device_id
            for device in devices
        )