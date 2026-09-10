from app.hardware.windows_usb import WindowsUsbDeviceMonitor


usb_monitor = WindowsUsbDeviceMonitor()

for device in usb_monitor.get_devices():
    print(device)