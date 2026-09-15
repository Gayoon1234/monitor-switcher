import win32com.client

from app.hardware.usb import UsbDeviceMonitor
from app.models.usb_device import UsbDevice


class WindowsUsbDeviceMonitor(UsbDeviceMonitor):

    def get_devices(self) -> list[UsbDevice]:
        wmi = win32com.client.GetObject("winmgmts:")
        devices = wmi.InstancesOf("Win32_PnPEntity")

        result = []

        for device in devices:
            device_id = device.DeviceID

            if not device_id:
                continue

            result.append(
                UsbDevice(
                    windows_device_id=device_id,
                    name=device.Name or device_id,
                )
            )

        return result