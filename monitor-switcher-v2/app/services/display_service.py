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

        displays = self.repository.load_displays()

        if not displays:
            displays = self.display_discovery.get_displays()
            self.repository.save_displays(displays)

        self.monitor_controller.set_displays(displays)

    def get_displays(self) -> list[Display]:
        return self.repository.load_displays()

    def refresh_displays(self) -> list[Display]:
        displays = self.display_discovery.get_displays()

        self.repository.save_displays(displays)
        self.monitor_controller.set_displays(displays)

        return displays

    def switch_input(
        self,
        display_id: str,
        input_id: str,
    ) -> None:
        self.monitor_controller.switch_input(
            display_id,
            input_id,
        )