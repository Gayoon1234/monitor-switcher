from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.ui.pages.my_devices import MyDevicesPage
from app.ui.pages.automations import AutomationsPage


class MainWindow(QMainWindow):

    def __init__(self, display_service, usb_service, repository):
        super().__init__()

        self.setWindowTitle("Monitor Switcher")
        self.resize(1000, 700)

        self.display_service = display_service
        self.usb_service = usb_service
        self.repository = repository

        self._setup_ui()

    def _setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)

        self.sidebar = QListWidget()
        self.sidebar.addItems([
            "My Devices",
            "Find My Device",
            "Automations",
            "Activity",
            "Settings",
        ])

        self.pages = QStackedWidget()

        self.pages.addWidget(
            MyDevicesPage(
                self.display_service,
                self.usb_service,
            )
        )

        self.pages.addWidget(QWidget())
        self.pages.addWidget(
            AutomationsPage(self.repository)
        )
        self.pages.addWidget(QWidget())
        self.pages.addWidget(QWidget())

        self.sidebar.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.sidebar.setCurrentRow(0)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)

        self.setCentralWidget(container)