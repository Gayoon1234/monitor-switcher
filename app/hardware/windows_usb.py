import logging

import win32com.client

from app.hardware.usb import UsbDeviceMonitor
from app.models.usb_device import UsbDevice


logger = logging.getLogger(__name__)


class WindowsUsbDeviceMonitor(UsbDeviceMonitor):

    def get_devices(self) -> list[UsbDevice]:
        logger.debug("Enumerating connected USB devices")

        wmi = win32com.client.GetObject("winmgmts:")
        devices = wmi.InstancesOf("Win32_PnPEntity")

        result = []

        for device in devices:
            if not device.Present:
                continue

            device_id = device.DeviceID
            if not device_id:
                continue

            if not device_id.startswith("USB\\"):
                continue

            result.append(
                UsbDevice(
                    windows_device_id=device_id,
                    name=device.Name or device_id,
                )
            )

        logger.debug(
            "Found %d connected USB devices",
            len(result),
        )

        return result