from PySide6.QtCore import QObject, Signal

from app.models.automation import Automation, ActionType, TriggerType
from app.models.device_event import DeviceEvent, DeviceEventType
from app.models.activity_event import ActivityEvent
from app.services.display_service import DisplayService
from app.services.activity_repository import ActivityRepository
from datetime import datetime


class AutomationService(QObject):

    activity_event = Signal(object)

    def __init__(
        self,
        display_service: DisplayService,
        activity_repository: ActivityRepository,
        automations: list[Automation],
    ):
        super().__init__()

        self.display_service = display_service
        self.activity_repository = activity_repository
        self.automations = automations

    def handle_device_event(self, event: DeviceEvent) -> None:
        self._emit_activity(
            ActivityEvent(
                timestamp=datetime.now(),
                event_type="device_event",
                message=(
                    "Device connected"
                    if event.event_type == DeviceEventType.CONNECTED
                    else "Device disconnected"
                ),
                success=True,
            )
        )

        for automation in self.automations:

            if not automation.enabled:
                continue

            trigger = automation.trigger

            if trigger.device_id != event.device_id:
                continue

            if (
                event.event_type == DeviceEventType.CONNECTED
                and trigger.type != TriggerType.DEVICE_CONNECTED
            ):
                continue

            if (
                event.event_type == DeviceEventType.DISCONNECTED
                and trigger.type != TriggerType.DEVICE_DISCONNECTED
            ):
                continue

            self._emit_activity(
                ActivityEvent(
                    timestamp=datetime.now(),
                    event_type="automation_triggered",
                    message=f"Automation triggered: {automation.name}",
                    success=True,
                )
            )

            self._execute_actions(automation)

    def _execute_actions(self, automation: Automation) -> None:
        for action in automation.actions:

            if action.type == ActionType.DO_NOTHING:
                continue

            if action.type == ActionType.SWITCH_INPUT:
                try:
                    self.display_service.switch_input(
                        action.display_id,
                        action.input_id,
                    )

                    self._emit_activity(
                        ActivityEvent(
                            timestamp=datetime.now(),
                            event_type="action",
                            message=(
                                f"{action.display_id} → "
                                f"{action.input_id}"
                            ),
                            success=True,
                        )
                    )

                except Exception as error:
                    self._emit_activity(
                        ActivityEvent(
                            timestamp=datetime.now(),
                            event_type="action",
                            message=(
                                f"Failed to switch "
                                f"{action.display_id} → "
                                f"{action.input_id}: {error}"
                            ),
                            success=False,
                        )
                    )

    def _emit_activity(self, event: ActivityEvent) -> None:
        events = self.activity_repository.load()
        events.append(event)
        self.activity_repository.save(events)

        self.activity_event.emit(event)
        
    def get_activity_history(self) -> list[ActivityEvent]:
        return self.activity_repository.load()