from app.hardware.display import DisplayController, DisplayDiscovery
from app.models.config import ConfigKey
from app.models.display import Display
from app.services.config_repository import ConfigRepository


class DisplayService:

    def __init__(
        self,
        display_controller: DisplayController,
        display_discovery: DisplayDiscovery,
        repository: ConfigRepository,
    ):
        self.display_controller = display_controller
        self.display_discovery = display_discovery
        self.repository = repository
        self.displays: list[Display] = []
        self._display_by_id: dict[str, Display] = {}

        self.displays = self.repository.get_config(ConfigKey.DISPLAYS)

        if not self.displays:
            self.displays = self.display_discovery.get_displays()
            self.repository.update_config(ConfigKey.DISPLAYS, self.displays)
        else:
            self._refresh_current_inputs()

        self._rebuild_display_lookup()
        self.display_controller.set_displays(self.displays)
        self._unsubscribe_config = self.repository.config_changed.subscribe(
            self._on_config_changed
        )

    def get_displays(self) -> list[Display]:
        return self.displays

    def refresh_displays(self) -> list[Display]:
        displays = self.display_discovery.get_displays()

        if displays != self.displays:
            self.repository.update_config(ConfigKey.DISPLAYS, displays)

        return self.displays

    def switch_input(
        self,
        display_id: str,
        input_id: str,
    ) -> None:
        display = self._find_display(display_id)

        self.display_controller.switch_input(
            display_id,
            input_id,
        )

        display.current_input = input_id

    def _find_display(self, display_id: str) -> Display:
        try:
            return self._display_by_id[display_id]
        except KeyError as error:
            raise ValueError(f"Display not found: {display_id}") from error

    def _rebuild_display_lookup(self) -> None:
        self._display_by_id = {
            display.id: display
            for display in self.displays
        }

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

    def _on_config_changed(self, key: ConfigKey) -> None:
        if key is not ConfigKey.DISPLAYS:
            return

        self.displays = self.repository.get_config(ConfigKey.DISPLAYS)
        self._rebuild_display_lookup()
        self.display_controller.set_displays(self.displays)