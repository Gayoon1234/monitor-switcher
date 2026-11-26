from PySide6.QtCore import QObject, Signal

from app.services.automation_service import AutomationService
from app.services.usb_service import UsbService


class QtServiceEventAdapter(QObject):

    activity_event = Signal(object)
    usb_devices_changed = Signal()

    def __init__(
        self,
        automation_service: AutomationService,
        usb_service: UsbService,
        parent: QObject | None = None,
    ):
        super().__init__(parent)

        self._unsubscribers = [
            automation_service.activity_events.subscribe(
                self.activity_event.emit
            ),
            usb_service.devices_changed.subscribe(
                self._emit_usb_devices_changed
            ),
        ]

    def close(self) -> None:
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    def _emit_usb_devices_changed(self, _: None) -> None:
        self.usb_devices_changed.emit()
