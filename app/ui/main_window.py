from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.ui.pages.my_devices import MyDevicesPage
from app.ui.pages.automations import AutomationsPage
from app.ui.pages.activity import ActivityPage
from app.ui.pages.find_my_device import FindMyDevicePage
from app.ui.pages.settings import SettingsPage

class MainWindow(QMainWindow):

    def __init__(
        self,
        display_service,
        usb_service,
        repository,
        automation_service,
        theme_service=None,
    ):
        super().__init__()

        self.setWindowTitle("Monitor Switcher")
        self.resize(1000, 700)

        self.display_service = display_service
        self.usb_service = usb_service
        self.repository = repository
        self.automation_service = automation_service
        self.theme_service = theme_service
        
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(190)
        self.sidebar.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.sidebar.setWordWrap(False)
        self.sidebar.setSpacing(4)

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

        self.pages.addWidget(
            FindMyDevicePage(self.usb_service)
        )
        
        self.pages.addWidget(
            AutomationsPage(
                self.repository,
                self.display_service,
                self.usb_service
            )
        )
        
        self.activity_page = ActivityPage(
            activity_history=self.automation_service.get_activity_history()
        )

        self.pages.addWidget(
            self.activity_page
        )

        if self.theme_service is not None:
            self.settings_page = SettingsPage(self.theme_service)
            self.settings_page.theme_changed.connect(
                self._set_active_theme
            )
            self.settings_page.activity_days_changed.connect(
                self._set_activity_period
            )
            self.settings_page.clear_activity_requested.connect(
                self._clear_activity_history
            )
            self.pages.addWidget(self.settings_page)
        else:
            self.pages.addWidget(QWidget())

        self.sidebar.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.sidebar.setCurrentRow(0)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)

        self.setCentralWidget(container)

        self.automation_service.activity_event.connect(
            self.activity_page.add_event
        )

    def _set_active_theme(self, theme_name):
        self.theme_service.set_active_theme(theme_name)
        application = QApplication.instance()
        if application is not None:
            application.setStyleSheet(
                self.theme_service.get_stylesheet()
            )

    def _set_activity_period(self, days):
        self.activity_page.days = days
        self.activity_page.set_events(
            self.automation_service.get_activity_history(days)
        )

    def _clear_activity_history(self):
        self.automation_service.clear_activity_history()
        self.activity_page.set_events([])