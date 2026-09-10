from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.display_card import DisplayCard
from app.ui.widgets.usb_device_card import UsbDeviceCard


class MyDevicesPage(QWidget):

    def __init__(self, display_service, usb_service):
        super().__init__()

        self.display_service = display_service
        self.usb_service = usb_service

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("My Devices")
        layout.addWidget(title)

        layout.addWidget(QLabel("Displays"))

        displays = self.display_service.get_displays()

        for display in displays:
           layout.addWidget(
                DisplayCard(
                    display,
                    self.display_service,
                )
            )

        layout.addWidget(QLabel("USB Devices"))
        configured_devices = self.usb_service.get_configured_devices()
        connected_devices = self.usb_service.get_devices()

        connected_ids = {
            device.windows_device_id
            for device in connected_devices
        }

        for device in configured_devices:
            connected = device.windows_device_id in connected_ids

            layout.addWidget(
                UsbDeviceCard(
                    device,
                    connected,
                )
            )