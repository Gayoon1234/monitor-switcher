import sys

from PySide6.QtWidgets import QApplication

from app.hardware.windows_monitor import WindowsMonitorController
from app.hardware.windows_usb import WindowsUsbDeviceMonitor
from app.services.config_repository import ConfigRepository
from app.services.display_service import DisplayService
from app.services.usb_service import UsbService
from app.ui.main_window import MainWindow


monitor_controller = WindowsMonitorController()

display_service = DisplayService(
    monitor_controller=monitor_controller,
    display_discovery=monitor_controller,
)

usb_monitor = WindowsUsbDeviceMonitor()

repository = ConfigRepository()

usb_service = UsbService(
    device_monitor=usb_monitor,
    repository=repository,
)


app = QApplication(sys.argv)

window = MainWindow(
    display_service=display_service,
    usb_service=usb_service,
)

window.show()

sys.exit(app.exec())