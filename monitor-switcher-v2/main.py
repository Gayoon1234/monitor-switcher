import sys

from PySide6.QtWidgets import QApplication

from app.hardware.windows_monitor import WindowsMonitorController
from app.hardware.windows_usb import WindowsUsbDeviceMonitor

from app.services.config_repository import ConfigRepository
from app.services.display_service import DisplayService
from app.services.usb_service import UsbService
from app.services.automation_service import AutomationService
from app.services.usb_monitor_service import UsbMonitorService
from app.services.activity_repository import ActivityRepository

from app.ui.main_window import MainWindow

# -------------------------
# Hardware
# -------------------------

monitor_controller = WindowsMonitorController()
usb_monitor = WindowsUsbDeviceMonitor()


# -------------------------
# Services
# -------------------------

display_service = DisplayService(
    monitor_controller=monitor_controller,
    display_discovery=monitor_controller,
)

repository = ConfigRepository()
activity_repository = ActivityRepository()

usb_service = UsbService(
    device_monitor=usb_monitor,
    repository=repository,
)


# -------------------------
# Automations
# -------------------------

automations = repository.load_automations()

automation_service = AutomationService(
    display_service=display_service,
    automations=automations,
    activity_repository=activity_repository
)


# -------------------------
# Qt application
# -------------------------

app = QApplication(sys.argv)


# -------------------------
# USB event monitoring
# -------------------------

usb_monitor_service = UsbMonitorService(
    device_monitor=usb_monitor,
    device_id="USB\\VID_05E3&PID_0626\\5&21296CF&0&17",
)

usb_monitor_service.device_event.connect(
    automation_service.handle_device_event
)

usb_monitor_service.start()


# -------------------------
# Main window
# -------------------------

window = MainWindow(
    display_service=display_service,
    usb_service=usb_service,
    repository=repository,
    automation_service=automation_service
)

automation_service.activity_event.connect(
    window.activity_page.add_event
)

window.show()


# -------------------------
# Start application
# -------------------------

sys.exit(app.exec())