from PySide6.QtCore import QTimer

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class FindMyDevicePage(QWidget):

    def __init__(self, usb_service):
        super().__init__()

        self.usb_service = usb_service
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

    def _show_all_devices(self):
        self._stop_detection()
        self._clear_content()

        self.content_layout.addWidget(
            QLabel("All Devices")
        )

        device_container = QWidget()
        device_layout = QVBoxLayout(device_container)

        devices = self.usb_service.get_devices()

        if not devices:
            device_layout.addWidget(
                QLabel("No USB devices found.")
            )
        else:
            for device in devices:
                device_layout.addWidget(
                    QLabel(
                        f"{device.name}\n"
                        f"{device.windows_device_id}"
                    )
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
                'If it\'s already connected, disconnect it before selecting "Start Detecting".'
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

    def _start_detection(self):
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

        self.detected_device_layout.addWidget(
            QLabel(
                f"Name\n"
                f"{device.name}\n\n"
                f"Windows Device ID\n"
                f"{device.windows_device_id}"
            )
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

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.detect_button = None
        self.status_label = None
        self.detected_device_layout = None

    def _toggle_detection(self):
        if self.detecting:
            self._stop_detection()
        else:
            self._start_detection()