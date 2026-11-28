import logging
import sys

from PySide6.QtWidgets import QApplication

from app.adapters.qt.usb_monitor_adapter import QtUsbMonitorAdapter
from app.hardware.windows_display import WindowsDisplayController
from app.hardware.windows_usb import WindowsUsbDeviceMonitor
from app.services.activity_repository import ActivityRepository
from app.services.automation_service import AutomationService
from app.services.config_repository import ConfigRepository
from app.models.config import ConfigKey
from app.services.display_service import DisplayService
from app.services.theme_service import ThemeService
from app.services.usb_monitor_service import UsbMonitorService
from app.services.usb_service import UsbService
from app.ui.main_window import MainWindow


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------
# Qt application
# -------------------------
app = QApplication(sys.argv)
theme_service = ThemeService()
app.setStyleSheet(theme_service.get_stylesheet())


# -------------------------
# Hardware
# -------------------------
display_controller = WindowsDisplayController()
usb_monitor = WindowsUsbDeviceMonitor()


# -------------------------
# Services
# -------------------------
repository = ConfigRepository()

display_service = DisplayService(
    display_controller=display_controller,
    display_discovery=display_controller,
    repository=repository,
)

activity_repository = ActivityRepository()

usb_service = UsbService(
    device_monitor=usb_monitor,
    repository=repository,
)


# -------------------------
# Automations
# -------------------------
automation_service = AutomationService(
    display_service=display_service,
    activity_repository=activity_repository,
    config_repository=repository,
)


# -------------------------
# USB event monitoring
# -------------------------
usb_monitor_service = UsbMonitorService()

usb_monitor_service.device_events.subscribe(
    automation_service.handle_device_event
)
usb_monitor_adapter = QtUsbMonitorAdapter(
    device_monitor=usb_monitor,
    monitor_service=usb_monitor_service,
    parent=app,
)

settings = repository.get_config(ConfigKey.SETTINGS)
if settings.usb_monitor_enabled:
    usb_monitor_adapter.start(settings.usb_monitor_interval_ms)


# -------------------------
# Main window
# -------------------------
window = MainWindow(
    display_service=display_service,
    usb_service=usb_service,
    repository=repository,
    automation_service=automation_service,
    theme_service=theme_service,
    usb_monitor_adapter=usb_monitor_adapter,
)

window.show()


# -------------------------
# Start application
# -------------------------
logger.info("Monitor Switcher started")

sys.exit(app.exec())