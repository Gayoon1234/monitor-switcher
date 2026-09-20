from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QFrame,
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

        layout = QVBoxLayout(self)

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
        self.nickname_label = QLabel(
            configured_device.nickname
        )

        self.nickname_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        device_name = QLabel(
            self._get_device_name(device)
        )

        status = QLabel(
            "● Connected"
            if connected
            else "○ Disconnected"
        )

        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")

        edit_button.clicked.connect(
            self._edit_device
        )

        delete_button.clicked.connect(
            self._delete_device
        )

        layout.addWidget(
            self.nickname_label
        )

        layout.addWidget(
            device_name
        )

        layout.addWidget(
            status
        )

        layout.addWidget(
            edit_button
        )

        layout.addWidget(
            delete_button
        )

        self.setStyleSheet(
            """
            UsbDeviceCard {
                background-color: #29432f;
                border: 1px solid #4f7d59;
                border-radius: 8px;
            }
            """
        )

    def _setup_unconfigured_card(
        self,
        layout,
        device,
    ):
        name = QLabel(device.name)

        name.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        device_id = QLabel(
            device.windows_device_id
        )

        nickname_input = QLineEdit()

        nickname_input.setPlaceholderText(
            "Enter a nickname"
        )

        add_button = QPushButton(
            "Add Device"
        )

        add_button.clicked.connect(
            lambda: self._add_device(
                nickname_input
            )
        )

        layout.addWidget(name)
        layout.addWidget(device_id)
        layout.addWidget(nickname_input)
        layout.addWidget(add_button)

        self.setStyleSheet(
            """
            UsbDeviceCard {
                background-color: #4a4328;
                border: 1px solid #8a7a3a;
                border-radius: 8px;
            }
            """
        )

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
