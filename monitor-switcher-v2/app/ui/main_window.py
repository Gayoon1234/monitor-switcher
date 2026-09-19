from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.ui.pages.my_devices import MyDevicesPage
from app.ui.pages.automations import AutomationsPage
from app.ui.pages.activity import ActivityPage

class MainWindow(QMainWindow):

    def __init__(self, display_service, usb_service, repository, automation_service):
        super().__init__()

        self.setWindowTitle("Monitor Switcher")
        self.resize(1000, 700)

        self.display_service = display_service
        self.usb_service = usb_service
        self.repository = repository
        self.automation_service = automation_service
        
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        
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
        
        self.activity_page = ActivityPage(
            activity_history=self.automation_service.get_activity_history()
        )

        self.pages.addWidget(
            self.activity_page
        )

        self.pages.addWidget(QWidget())

        self.sidebar.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.sidebar.setCurrentRow(0)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)

        self.setCentralWidget(container)