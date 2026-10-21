from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
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

        self.usb_service.devices_changed.connect(
            self._refresh
        )

        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(24, 20, 24, 20)
        self.content_layout.setSpacing(12)

        title = QLabel("My Devices")
        title.setObjectName("pageTitle")
        self.content_layout.addWidget(title)

        self.displays_title = QLabel("Displays")
        self.displays_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.displays_title)

        self.display_list = QWidget()
        self.display_layout = QVBoxLayout(self.display_list)
        self.display_layout.setSpacing(12)
        self.content_layout.addWidget(self.display_list)

        self.usb_title = QLabel("USB Devices")
        self.usb_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.usb_title)

        self.device_scroll_area = QScrollArea()
        self.device_scroll_area.setWidgetResizable(False)
        self.device_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.device_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.device_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.device_container = QWidget()
        self.device_layout = QHBoxLayout(self.device_container)
        self.device_layout.setContentsMargins(0, 0, 0, 0)
        self.device_layout.setSpacing(12)
        self.device_scroll_area.setWidget(self.device_container)

        self.content_layout.addWidget(self.device_scroll_area)
        self.content_layout.addStretch()

        page_scroll_area = QScrollArea()
        page_scroll_area.setObjectName("myDevicesScrollArea")
        page_scroll_area.setWidgetResizable(True)
        page_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        page_scroll_area.setWidget(self.content)
        layout.addWidget(page_scroll_area)

    def _refresh(self):
        self._populate_displays()
        self._populate_devices()

    def _populate_displays(self):
        while self.display_layout.count():
            item = self.display_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for display in self.display_service.get_displays():
            self.display_layout.addWidget(
                DisplayCard(display, self.display_service)
            )

    def _populate_devices(self):
        while self.device_layout.count():
            item = self.device_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        configured_devices = self.usb_service.get_configured_devices()
        connected_devices = self.usb_service.get_devices()
        connected_devices_by_id = {
            device.windows_device_id: device
            for device in connected_devices
        }

        for configured_device in configured_devices:
            connected_device = connected_devices_by_id.get(
                configured_device.windows_device_id
            )
            connected = connected_device is not None
            device = connected_device or configured_device

            card = UsbDeviceCard(
                device,
                configured_device=configured_device,
                connected=connected,
            )
            card.setFixedWidth(250)
            card.edit_device_requested.connect(self._edit_device)
            card.delete_device_requested.connect(self._delete_device)
            self.device_layout.addWidget(card)

        if not configured_devices:
            empty_label = QLabel(
                "No devices saved yet. Find a connected device to add it."
            )
            empty_label.setObjectName("emptyState")
            self.device_layout.addWidget(empty_label)

        self.device_layout.addStretch()
        self.device_container.setMinimumSize(
            self.device_layout.sizeHint()
        )
        self.device_container.adjustSize()
        self.device_scroll_area.setMinimumHeight(
            self.device_container.sizeHint().height()
            + self.device_scroll_area.horizontalScrollBar().sizeHint().height()
            + 16
        )

    def _edit_device(self, device):
        self.usb_service.update_device(device)
        self._refresh()

    def _delete_device(self, device):
        self.usb_service.remove_device(device.id)
        self._refresh()