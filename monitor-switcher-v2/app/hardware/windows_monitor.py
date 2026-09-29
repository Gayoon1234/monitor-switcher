import win32com.client

from monitorcontrol import InputSource, get_monitors

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
        # Win32_DesktopMonitor does not detect my beloved hp w1907, so PnPEntity it is.
        devices = wmi.InstancesOf("Win32_PnPEntity")

        display_devices = [
            device
            for device in devices
            if (device.DeviceID or "").startswith("DISPLAY\\")
        ]

        result = []

        for index, device in enumerate(display_devices):
            monitor = self.monitors[index] if index < len(self.monitors) else None

            inputs = self._get_inputs(monitor)
            current_input = self._get_current_input(monitor, inputs)

            result.append(
                Display(
                    id=f"display-{index + 1:03d}",
                    name=device.Name or device.DeviceID,
                    windows_device_id=device.DeviceID,
                    inputs=inputs,
                    current_input=current_input,
                )
            )

        return result


    def _get_inputs(self, monitor) -> list[DisplayInput]:
        if monitor is None:
            return []

        try:
            with monitor:
                capabilities = monitor.get_vcp_capabilities()
        except Exception:
            # get_vcp_capabilities does not work on the HP w1907...don't know why...
            if monitor.vcp.description == "HP w1907 Wide LCD Monitor":
                return [
                    DisplayInput("ANALOG1", InputType.ANALOG),
                    DisplayInput("DVI1", InputType.DVI),
                ]

            return []

        return [
            display_input
            for input_source in capabilities.get("inputs", [])
            if (display_input := self._to_display_input(input_source)) is not None
        ]  

    def _to_display_input(self, input_source) -> DisplayInput | None:
        input_name = getattr(input_source, "name", None)

        if input_name is None:
            return None

        input_type = self._get_input_type(input_name)

        if input_type is None:
            return None

        return DisplayInput(
            input_id=input_name,
            input_type=input_type,
        )

    def _get_input_type(self, input_name: str) -> InputType | None:
        if input_name.startswith("HDMI"):
            return InputType.HDMI

        if input_name.startswith("DVI"):
            return InputType.DVI

        if input_name.startswith("ANALOG"):
            return InputType.ANALOG

        return None

    def _get_current_input(
        self,
        monitor,
        inputs: list[DisplayInput],
    ) -> str | None:
        if monitor is None:
            return None

        try:
            with monitor:
                value = monitor.get_input_source()
        except Exception:
            return None

        for input_source in InputSource:
            if input_source.value == value:
                return input_source.name

        return None