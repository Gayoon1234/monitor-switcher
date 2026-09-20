from app.hardware.monitor import DisplayDiscovery, MonitorController
from app.models.display import Display


class DisplayService:

    def __init__(
        self,
        monitor_controller: MonitorController,
        display_discovery: DisplayDiscovery,
    ):
        self.monitor_controller = monitor_controller
        self.display_discovery = display_discovery

    def get_displays(self) -> list[Display]:
        return self.display_discovery.get_displays()

    def switch_input(self, display_id: str, input_id: str) -> None:
        self.monitor_controller.switch_input(display_id, input_id)