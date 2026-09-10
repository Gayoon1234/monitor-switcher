from app.models.automation import Automation
from app.models.device_event import DeviceEvent, DeviceEventType
from app.services.display_service import DisplayService


class AutomationService:

    def __init__(
        self,
        display_service: DisplayService,
        automations: list[Automation],
    ):
        self.display_service = display_service
        self.automations = automations

    def handle_device_event(self, event: DeviceEvent) -> None:
        for automation in self.automations:

            if not automation.enabled:
                continue

            trigger = automation.trigger

            if trigger.device_id != event.device_id:
                continue

            if (
                event.event_type == DeviceEventType.CONNECTED
                and trigger.type.value != "device_connected"
            ):
                continue

            if (
                event.event_type == DeviceEventType.DISCONNECTED
                and trigger.type.value != "device_disconnected"
            ):
                continue

            self._execute_actions(automation)

    def _execute_actions(self, automation: Automation) -> None:
        for action in automation.actions:

            if action.type.value == "do_nothing":
                continue

            if action.type.value == "switch_input":
                self.display_service.switch_input(
                    action.display_id,
                    action.input_id,
                )