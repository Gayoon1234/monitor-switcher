from app.hardware.windows_monitor import WindowsMonitorController
from app.hardware.windows_usb import WindowsUsbDeviceMonitor
from app.services.config_repository import ConfigRepository
from app.services.display_service import DisplayService
from app.services.usb_service import UsbService
from app.models.usb_device import ConfiguredUsbDevice


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


print("=== Displays ===")

for display in display_service.get_displays():
    print(display)


print()
print("=== USB Devices ===")

for device in usb_service.get_devices():
    print(device)


print()
print("=== Configured USB Devices ===")

for device in usb_service.get_configured_devices():
    print(device)

print()
print("=== Testing Add ===")

new_device = ConfiguredUsbDevice(
    id="usb-002",
    windows_device_id=r"USB\TEST\123",
    nickname="Test Device",
)

usb_service.add_device(new_device)

for device in usb_service.get_configured_devices():
    print(device)


print()
print("=== Testing Remove ===")

usb_service.remove_device("usb-002")

for device in usb_service.get_configured_devices():
    print(device)