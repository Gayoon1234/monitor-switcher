import win32com.client
from monitorcontrol import get_monitors

from app.hardware.monitor import DisplayDiscovery, MonitorController
from app.models.display import Display


class WindowsMonitorController(MonitorController, DisplayDiscovery):

    def __init__(self):
        self.monitors = get_monitors()

        self._monitor_map = {
            "display-001": self.monitors[0],
            "display-002": self.monitors[1],
        }

    def switch_input(self, display_id: str, input_id: str) -> None:
        monitor = self._monitor_map[display_id]

        with monitor:
            monitor.set_input_source(input_id)

    def get_displays(self) -> list[Display]:
        wmi = win32com.client.GetObject("winmgmts:")
        devices = wmi.InstancesOf("Win32_PnPEntity")

        result = []

        for device in devices:
            device_id = device.DeviceID or ""

            if not device_id.startswith("DISPLAY\\"):
                continue

            display_id = f"display-{len(result) + 1:03d}"

            result.append(
                Display(
                    id=display_id,
                    name=device.Name or device_id,
                    windows_device_id=device_id,
                    inputs=[],
                )
            )

        return result