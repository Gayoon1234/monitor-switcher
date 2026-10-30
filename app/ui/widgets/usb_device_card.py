from PySide6.QtCore import Qt, Signal

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class UsbDeviceCard(QFrame):

    add_device_requested = Signal(object, str)
    edit_device_requested = Signal(object)
    delete_device_requested = Signal(object)

    def __init__(
        self,
        device,
        configured_device=None,
        connected=None,
    ):
        super().__init__()

        self.device = device
        self.configured_device = configured_device
        self.setProperty(
            "deviceState",
            "configured" if configured_device is not None else "unconfigured",
        )
        self.setObjectName("usbDeviceCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        if configured_device is not None:
            self._setup_configured_card(
                layout,
                device,
                configured_device,
                connected,
            )
        else:
            self._setup_unconfigured_card(
                layout,
                device,
            )

    def _setup_configured_card(
        self,
        layout,
        device,
        configured_device,
        connected,
    ):
        header = QHBoxLayout()
        self.nickname_label = QLabel(
            configured_device.nickname
        )
        self.nickname_label.setObjectName("cardTitle")
        self.nickname_label.setWordWrap(True)

        device_name = QLabel(
            self._get_device_name(device)
        )
        device_name.setObjectName("mutedText")
        device_name.setWordWrap(True)

        status = QLabel("Connected" if connected else "Disconnected")
        status.setObjectName("deviceStatus")
        status.setProperty(
            "connectionState",
            "connected" if connected else "disconnected",
        )
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(self.nickname_label, 1)
        header.addWidget(status)

        buttons = QHBoxLayout()

        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")
        delete_button.setObjectName("dangerButton")

        edit_button.clicked.connect(
            self._edit_device
        )

        delete_button.clicked.connect(
            self._delete_device
        )

        buttons.addWidget(edit_button)
        buttons.addWidget(delete_button)
        layout.addLayout(header)
        layout.addWidget(device_name)
        layout.addStretch()
        layout.addLayout(buttons)

    def _setup_unconfigured_card(
        self,
        layout,
        device,
    ):
        name = QLabel(device.name)
        name.setObjectName("cardTitle")
        name.setWordWrap(True)

        id_label = QLabel("DEVICE ID")
        id_label.setObjectName("eyebrow")
        device_id = QLabel(
            device.windows_device_id
        )
        device_id.setObjectName("mutedText")
        device_id.setWordWrap(True)
        device_id.setToolTip(device.windows_device_id)
        device_id.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        nickname_input = QLineEdit()

        nickname_input.setPlaceholderText(
            "Enter a nickname"
        )

        add_button = QPushButton(
            "Add to My Devices"
        )
        add_button.setObjectName("primaryButton")

        add_button.clicked.connect(
            lambda: self._add_device(
                nickname_input
            )
        )

        layout.addWidget(name)
        layout.addWidget(id_label)
        layout.addWidget(device_id)
        layout.addStretch()
        layout.addWidget(nickname_input)
        layout.addWidget(add_button)

    def _add_device(self, nickname_input):
        nickname = nickname_input.text().strip()

        if not nickname:
            return

        self.add_device_requested.emit(
            self.device,
            nickname,
        )

    def _edit_device(self):
        nickname, accepted = QInputDialog.getText(
            self,
            "Edit Device",
            "Nickname:",
            QLineEdit.Normal,
            self.configured_device.nickname,
        )

        if not accepted:
            return

        nickname = nickname.strip()

        if not nickname:
            return

        self.configured_device.nickname = nickname

        self.edit_device_requested.emit(
            self.configured_device
        )

    def _delete_device(self):
        result = QMessageBox.question(
            self,
            "Delete Device",
            (
                f"Are you sure you want to delete "
                f"'{self.configured_device.nickname}'?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if result != QMessageBox.Yes:
            return

        self.delete_device_requested.emit(
            self.configured_device
        )

    def _get_device_name(self, device):
        return getattr(
            device,
            "name",
            device.windows_device_id,
        )
