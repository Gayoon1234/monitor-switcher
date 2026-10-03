from app.hardware.monitor import DisplayDiscovery, MonitorController
from app.models.display import Display
from app.services.config_repository import ConfigRepository


class DisplayService:

    def __init__(
        self,
        monitor_controller: MonitorController,
        display_discovery: DisplayDiscovery,
        repository: ConfigRepository,
    ):
        self.monitor_controller = monitor_controller
        self.display_discovery = display_discovery
        self.repository = repository

        self.displays = self.repository.load_displays()

        if not self.displays:
            self.displays = self.display_discovery.get_displays()
            self.repository.save_displays(self.displays)
        else:
            self._refresh_current_inputs()

        self.monitor_controller.set_displays(self.displays)

    def get_displays(self) -> list[Display]:
        return self.displays

    def refresh_displays(self) -> list[Display]:
        displays = self.display_discovery.get_displays()

        self.repository.save_displays(displays)

        self.displays = displays
        self.monitor_controller.set_displays(self.displays)

        return self.displays

    def switch_input(
        self,
        display_id: str,
        input_id: str,
    ) -> None:
        self.monitor_controller.switch_input(
            display_id,
            input_id,
        )

        for display in self.displays:
            if display.id == display_id:
                display.current_input = input_id
                break

    def _refresh_current_inputs(self) -> None:
        live_displays = self.display_discovery.get_displays()

        current_inputs = {
            display.windows_device_id: display.current_input
            for display in live_displays
        }

        for display in self.displays:
            if display.windows_device_id in current_inputs:
                display.current_input = current_inputs[
                    display.windows_device_id
                ]