import win32com.client
from monitorcontrol import get_monitors

from app.hardware.monitor import DisplayDiscovery, MonitorController
from app.models.display import Display, DisplayInput, InputType


class WindowsMonitorController(MonitorController, DisplayDiscovery):

    def __init__(self):
        self.monitors = get_monitors()
        self.displays = self.get_displays()

        self._monitor_map = {
            display.id: monitor
            for display, monitor in zip(self.displays, self.monitors)
        }

    def switch_input(self, display_id: str, input_id: str) -> None:
        monitor = self._monitor_map[display_id]

        with monitor:
            monitor.set_input_source(input_id)

        display = next(
            display
            for display in self.displays
            if display.id == display_id
        )

        display.current_input = input_id

    def get_displays(self) -> list[Display]:
        wmi = win32com.client.GetObject("winmgmts:")
        devices = wmi.InstancesOf("Win32_PnPEntity")

        result = []

        for device in devices:
            device_id = device.DeviceID or ""

            if not device_id.startswith("DISPLAY\\"):
                continue

            display_id = f"display-{len(result) + 1:03d}"

            if "PHLC213" in device_id:
                inputs = [
                    DisplayInput("HDMI1", InputType.HDMI),
                    DisplayInput("ANALOG1", InputType.ANALOG),
                ]
            elif "HWP26A2" in device_id:
                inputs = [
                    DisplayInput("ANALOG1", InputType.ANALOG),
                    DisplayInput("DVI1", InputType.DVI),
                ]
            else:
                inputs = []

            monitor = self.monitors[len(result)]
            current_input = self._get_current_input(monitor, inputs)

            result.append(
                Display(
                    id=display_id,
                    name=device.Name or device_id,
                    windows_device_id=device_id,
                    inputs=inputs,
                    current_input=current_input,
                )
            )

        return result

    def _get_current_input(
        self,
        monitor,
        inputs: list[DisplayInput],
    ) -> str | None:

        try:
            with monitor:
                value = monitor.get_input_source()

        except Exception:
            return None

        input_map = {
            1: "DVI1",
            2: "ANALOG1",
            15: "ANALOG1",
            17: "HDMI1",
        }

        return input_map.get(value)