from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class UsbDeviceCard(QFrame):

    def __init__(self, device, connected):
        super().__init__()

        layout = QVBoxLayout(self)

        name = QLabel(device.nickname)
        name.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        status = QLabel(
            "Connected" if connected else "Disconnected"
        )

        layout.addWidget(name)
        layout.addWidget(status)