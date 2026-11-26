import logging

from PySide6.QtCore import QObject, Signal

from app.hardware.usb import UsbDeviceMonitor
from app.models.device_event import DeviceEvent, DeviceEventType
from app.services.usb_device_poller import UsbDevicePoller


logger = logging.getLogger(__name__)


class UsbMonitorService(QObject):

    device_event = Signal(object)

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        device_id: str | None = None,
    ):
        super().__init__()

        self.device_id = device_id
        self.previous_connected: bool | set[str] = (
            set() if device_id is None else False
        )
        self._baseline_pending = False

        self._poller = UsbDevicePoller(
            device_monitor=device_monitor,
            device_id=device_id,
            parent=self,
        )
        self._poller.state_ready.connect(self._on_state_ready)
        self._poller.poll_failed.connect(self._on_poll_failed)

    def start(self, interval_ms: int = 500) -> None:
        UsbDevicePoller.validate_interval(interval_ms)
        self._baseline_pending = True
        self.previous_connected = (
            set() if self.device_id is None else False
        )
        self._poller.start(interval_ms)

    def set_interval(self, interval_ms: int) -> None:
        self._poller.set_interval(interval_ms)

    def stop(self) -> None:
        self._baseline_pending = False
        self._poller.stop()

    def _on_state_ready(self, current_state: bool | set[str]) -> None:
        if self._baseline_pending:
            self.previous_connected = current_state
            self._baseline_pending = False
            return

        if self.device_id is None:
            if isinstance(current_state, set):
                self._check_all_devices(current_state)
            else:
                logger.error("USB monitor returned an invalid device state")
            return

        if isinstance(current_state, bool):
            if current_state == self.previous_connected:
                return

            self.previous_connected = current_state
            self._emit_device_event(self.device_id, current_state)
        else:
            logger.error("USB monitor returned an invalid device state")

    def _on_poll_failed(self, error: Exception) -> None:
        message = (
            "Failed to initialize USB monitoring state for %s"
            if self._baseline_pending
            else "Failed to check USB device state for %s"
        )
        logger.error(
            message,
            self.device_id,
            exc_info=(type(error), error, error.__traceback__),
        )
        self._baseline_pending = False

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
