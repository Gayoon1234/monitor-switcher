import uuid

from PySide6.QtCore import QTimer, Qt

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.usb_device import ConfiguredUsbDevice
from app.ui.widgets.usb_device_card import UsbDeviceCard


class FindMyDevicePage(QWidget):

    def __init__(self, usb_service):
        super().__init__()

        self.usb_service = usb_service

        self.usb_service.devices_changed.connect(
            self._refresh
        )

        self.detecting = False
        self.initial_device_ids = set()

        self.detect_button = None
        self.status_label = None
        self.detected_device_layout = None

        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # To be not hardcoded at some point
        self.timer.timeout.connect(
            self._check_for_new_devices
        )

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Find My Device")
        layout.addWidget(title)

        mode_layout = QHBoxLayout()

        all_devices_button = QPushButton("All Devices")
        detect_button = QPushButton("Detect New Device")

        all_devices_button.clicked.connect(
            self._show_all_devices
        )

        detect_button.clicked.connect(
            self._show_detection
        )

        mode_layout.addWidget(all_devices_button)
        mode_layout.addWidget(detect_button)

        layout.addLayout(mode_layout)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self._show_all_devices()

    # ------------------------------------------------------------------
    # All Devices
    # ------------------------------------------------------------------

    def _show_all_devices(self):
        self._stop_detection()
        self._clear_content()

        self.content_layout.addWidget(
            QLabel("All Devices")
        )

        device_container = QWidget()

        device_layout = QGridLayout(device_container)
        device_layout.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )

        devices = self.usb_service.get_devices()
        configured_devices = (
            self.usb_service.get_configured_devices()
        )

        configured_devices_by_windows_id = {
            device.windows_device_id: device
            for device in configured_devices
        }

        columns = 3

        if not devices:
            device_layout.addWidget(
                QLabel("No USB devices found."),
                0,
                0,
            )

        else:
            for index, device in enumerate(devices):

                row = index // columns
                column = index % columns

                configured_device = (
                    configured_devices_by_windows_id.get(
                        device.windows_device_id
                    )
                )

                card = UsbDeviceCard(
                    device,
                    configured_device=configured_device,
                    connected=True,
                )

                card.setFixedWidth(250)

                if configured_device is None:
                    card.add_device_requested.connect(
                        self._add_device
                    )
                else:
                    card.edit_device_requested.connect(
                        self._edit_device
                    )

                    card.delete_device_requested.connect(
                        self._delete_device
                    )

                device_layout.addWidget(
                    card,
                    row,
                    column,
                )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(device_container)

        self.content_layout.addWidget(
            scroll_area
        )

        refresh_button = QPushButton("Refresh")

        refresh_button.clicked.connect(
            self._show_all_devices
        )

        self.content_layout.addWidget(
            refresh_button
        )

        self.content_layout.addStretch()

    def _refresh(self):
        self._show_all_devices()

    # ------------------------------------------------------------------
    # Detect New Device
    # ------------------------------------------------------------------

    def _show_detection(self):
        self._stop_detection()
        self._clear_content()

        self.content_layout.addWidget(
            QLabel("Detect New Device")
        )

        detection_container = QWidget()

        detection_layout = QVBoxLayout(
            detection_container
        )

        detection_layout.addWidget(
            QLabel(
                "Connect the USB device you want to add.\n"
                "If it's already connected, disconnect it "
                'before selecting "Start Detecting".'
            )
        )

        self.detect_button = QPushButton(
            "Start Detecting"
        )

        self.detect_button.clicked.connect(
            self._toggle_detection
        )

        detection_layout.addWidget(
            self.detect_button
        )

        self.status_label = QLabel(
            "Status: Ready"
        )

        detection_layout.addWidget(
            self.status_label
        )

        self.detected_device_layout = QVBoxLayout()

        detection_layout.addLayout(
            self.detected_device_layout
        )

        detection_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(
            detection_container
        )

        self.content_layout.addWidget(
            scroll_area
        )

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _start_detection(self):
        # Take a fresh snapshot when detection starts.
        devices = self.usb_service.get_devices()

        self.initial_device_ids = {
            device.windows_device_id
            for device in devices
        }

        self.detecting = True

        self.status_label.setText(
            "Status: Waiting for device..."
        )

        self.detect_button.setText(
            "Stop Detecting"
        )

        self.timer.start()

    def _check_for_new_devices(self):
        if not self.detecting:
            return

        devices = self.usb_service.get_devices()

        for device in devices:

            if (
                device.windows_device_id
                not in self.initial_device_ids
            ):
                self._device_detected(device)
                return

    def _device_detected(self, device):
        self.timer.stop()
        self.detecting = False

        self.detect_button.setText(
            "Start Detecting"
        )

        self.status_label.setText(
            "Status: Device detected"
        )

        # A detected device is, by definition, not configured yet.
        card = UsbDeviceCard(
            device,
            configured_device=None,
            connected=True,
        )

        card.setFixedWidth(250)

        card.add_device_requested.connect(
            self._add_device
        )

        self.detected_device_layout.addWidget(
            card
        )

    def _stop_detection(self):
        self.timer.stop()

        self.detecting = False

        if self.detect_button is not None:
            self.detect_button.setText(
                "Start Detecting"
            )

        if self.status_label is not None:
            self.status_label.setText(
                "Status: Ready"
            )

    def _toggle_detection(self):
        if self.detecting:
            self._stop_detection()
        else:
            self._start_detection()

    # ------------------------------------------------------------------
    # UI Cleanup
    # ------------------------------------------------------------------

    def _clear_content(self):
        while self.content_layout.count():

            item = self.content_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.detect_button = None
        self.status_label = None
        self.detected_device_layout = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _add_device(self, device, nickname):
        configured_device = ConfiguredUsbDevice(
            id=str(uuid.uuid4()),
            windows_device_id=device.windows_device_id,
            nickname=nickname,
        )

        self.usb_service.add_device(
            configured_device
        )

        self._show_all_devices()

    def _edit_device(self, device):
        self.usb_service.update_device(device)
        self._show_all_devices()


    def _delete_device(self, device):
        self.usb_service.remove_device(device.id)
        self._show_all_devices()