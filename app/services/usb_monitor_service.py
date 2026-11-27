import logging

from app.events import EventHook
from app.models.device_event import DeviceEvent, DeviceEventType


logger = logging.getLogger(__name__)


class UsbMonitorService:

    def __init__(
        self,
        device_id: str | None = None,
    ):
        self.device_id = device_id
        self.previous_connected: bool | set[str] = (
            set() if device_id is None else False
        )
        self._baseline_pending = False
        self.device_events: EventHook[DeviceEvent] = EventHook()

    def begin_monitoring(self) -> None:
        self._baseline_pending = True
        self.previous_connected = (
            set() if self.device_id is None else False
        )

    def stop_monitoring(self) -> None:
        self._baseline_pending = False

    def handle_state(self, current_state: bool | set[str]) -> None:
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

    def handle_poll_error(self, error: Exception) -> None:
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
        self.device_events.emit(
            DeviceEvent(
                device_id=device_id,
                event_type=(
                    DeviceEventType.CONNECTED
                    if connected
                    else DeviceEventType.DISCONNECTED
                ),
            )
        )
