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
        try:
            self.previous_connected = self._current_state()
        except Exception:
            logger.exception(
                "Failed to initialize USB monitoring state for %s",
                self.device_id,
            )
            self.previous_connected = (
                set() if self.device_id is None else False
            )

        self.timer.start(interval_ms)

    def stop(self) -> None:
        self.timer.stop()

    def _current_state(self) -> bool | set[str]:
        if self.device_id is None:
            return self._current_device_ids()

        return self._is_connected()

    def _check_device(self) -> None:
        try:
            current_state = self._current_state()
        except Exception:
            logger.exception(
                "Failed to check USB device state for %s",
                self.device_id,
            )
            return

        if self.device_id is None:
            self._check_all_devices(current_state)
            return

        connected = current_state

        if connected == self.previous_connected:
            return

        self.previous_connected = connected
        self._emit_device_event(self.device_id, connected)

    def _check_all_devices(self, current_ids: set[str]) -> None:
        previous_ids = (
            set(self.previous_connected)
            if isinstance(self.previous_connected, set)
            else set()
        )

        for device_id in sorted(current_ids - previous_ids):
            self._emit_device_event(device_id, True)

        for device_id in sorted(previous_ids - current_ids):
            self._emit_device_event(device_id, False)

        self.previous_connected = current_ids

    def _emit_device_event(self, device_id: str, connected: bool) -> None:
        self.device_event.emit(
            DeviceEvent(
                device_id=device_id,
                event_type=(
                    DeviceEventType.CONNECTED
                    if connected
                    else DeviceEventType.DISCONNECTED
                ),
            )
        )

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