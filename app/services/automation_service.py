import logging
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from app.models.activity_event import ActivityEvent
from app.models.automation import ActionType, Automation, TriggerType
from app.models.device_event import DeviceEvent, DeviceEventType
from app.services.activity_repository import ActivityRepository
from app.services.display_service import DisplayService


logger = logging.getLogger(__name__)


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
            if not self._matches_trigger(automation, event):
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

    def _matches_trigger(
        self,
        automation: Automation,
        event: DeviceEvent,
    ) -> bool:
        if not automation.enabled:
            return False

        trigger = automation.trigger

        if trigger.device_id != event.device_id:
            return False

        if (
            event.event_type == DeviceEventType.CONNECTED
            and trigger.type != TriggerType.DEVICE_CONNECTED
        ):
            return False

        if (
            event.event_type == DeviceEventType.DISCONNECTED
            and trigger.type != TriggerType.DEVICE_DISCONNECTED
        ):
            return False

        return True

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
                    logger.exception(
                        "Automation action failed: %s → %s",
                        action.display_id,
                        action.input_id,
                    )

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
        self.activity_repository.append(event)
        self.activity_event.emit(event)

    def get_activity_history(self) -> list[ActivityEvent]:
        return self.activity_repository.load()
