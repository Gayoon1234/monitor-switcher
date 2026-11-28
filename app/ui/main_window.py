from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from app.adapters.qt.service_event_adapter import QtServiceEventAdapter
from app.models.config import ConfigKey
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
        usb_monitor_adapter=None,
    ):
        super().__init__()

        self.setWindowTitle("Monitor Switcher")
        self.resize(1000, 700)

        self.display_service = display_service
        self.usb_service = usb_service
        self.repository = repository
        self.automation_service = automation_service
        self.theme_service = theme_service
        self.usb_monitor_adapter = usb_monitor_adapter
        self.service_event_adapter = QtServiceEventAdapter(
            automation_service,
            usb_service,
            parent=self,
        )
        
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
                self.service_event_adapter.usb_devices_changed,
            )
        )

        self.pages.addWidget(
            FindMyDevicePage(
                self.usb_service,
                self.service_event_adapter.usb_devices_changed,
            )
        )
        
        self.automations_page = AutomationsPage(
            self.repository,
            self.display_service,
            self.usb_service,
        )
        self.pages.addWidget(self.automations_page)
        
        activity_days = self.repository.get_config(ConfigKey.ACTIVITY_DAYS)
        self.activity_page = ActivityPage(
            activity_history=self.automation_service.get_activity_history(
                activity_days
            ),
            days=activity_days,
        )

        self.pages.addWidget(
            self.activity_page
        )

        if self.theme_service is not None:
            self.settings_page = SettingsPage(
                self.theme_service,
                activity_days=activity_days,
                activity_logging_paused=(
                    self.automation_service.activity_logging_paused
                ),
                usb_monitor_enabled=(
                    self.repository.get_config(
                        ConfigKey.USB_MONITOR_ENABLED
                    )
                ),
                usb_monitor_interval_ms=(
                    self.repository.get_config(
                        ConfigKey.USB_MONITOR_INTERVAL_MS
                    )
                ),
            )
            self.settings_page.theme_changed.connect(
                self._set_active_theme
            )
            self.settings_page.activity_days_changed.connect(
                self._set_activity_period
            )
            self.settings_page.clear_activity_requested.connect(
                self._clear_activity_history
            )
            self.settings_page.activity_logging_paused_changed.connect(
                self._set_activity_logging_paused
            )
            self.settings_page.usb_monitor_enabled_changed.connect(
                self._set_usb_monitor_enabled
            )
            self.settings_page.usb_monitor_interval_changed.connect(
                self._set_usb_monitor_interval
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

        self.service_event_adapter.activity_event.connect(
            self.activity_page.add_event
        )

    def closeEvent(self, event):
        self.service_event_adapter.close()
        self.automations_page.close()
        self.automation_service.close()
        if self.usb_monitor_adapter is not None:
            self.usb_monitor_adapter.stop()
        super().closeEvent(event)

    def _set_active_theme(self, theme_name):
        self.theme_service.set_active_theme(theme_name)
        application = QApplication.instance()
        if application is not None:
            application.setStyleSheet(
                self.theme_service.get_stylesheet()
            )

    def _set_activity_period(self, days):
        self.repository.update_config(ConfigKey.ACTIVITY_DAYS, days)
        self.activity_page.days = days
        self.activity_page.set_events(
            self.automation_service.get_activity_history(days)
        )

    def _set_activity_logging_paused(self, paused):
        self.repository.update_config(
            ConfigKey.STORE_ACTIVITY_LOGS,
            not paused,
        )

    def _set_usb_monitor_enabled(self, enabled):
        self.repository.update_config(
            ConfigKey.USB_MONITOR_ENABLED,
            enabled,
        )
        if self.usb_monitor_adapter is None:
            return

        if enabled:
            self.usb_monitor_adapter.start(
                self.repository.get_config(
                    ConfigKey.USB_MONITOR_INTERVAL_MS
                )
            )
        else:
            self.usb_monitor_adapter.stop()

    def _set_usb_monitor_interval(self, interval_ms):
        self.repository.update_config(
            ConfigKey.USB_MONITOR_INTERVAL_MS,
            interval_ms,
        )
        if self.usb_monitor_adapter is not None:
            self.usb_monitor_adapter.set_interval(interval_ms)

    def _clear_activity_history(self):
        self.automation_service.clear_activity_history()
        self.activity_page.set_events([])