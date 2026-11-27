from app.models.activity_event import ActivityEvent
from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.device_event import DeviceEvent, DeviceEventType
from app.services.automation_service import AutomationService


class FakeDisplayService:

    def __init__(self):
        self.calls = []
        self.error: Exception | None = None

    def switch_input(
        self,
        display_id: str | None,
        input_id: str | None,
    ) -> None:
        self.calls.append((display_id, input_id))

        if self.error is not None:
            raise self.error


class FakeActivityRepository:

    def __init__(self):
        self.events: list[ActivityEvent] = []

    def append(self, event: ActivityEvent) -> None:
        self.events.append(event)

    def load(self) -> list[ActivityEvent]:
        return list(self.events)


def create_automation_service(
    automations: list[Automation],
) -> tuple[AutomationService, FakeDisplayService, FakeActivityRepository]:
    display_service = FakeDisplayService()
    activity_repository = FakeActivityRepository()

    service = AutomationService(
        display_service=display_service,
        activity_repository=activity_repository,
        automations=automations,
    )

    return service, display_service, activity_repository


def create_automation(
    *,
    enabled: bool = True,
    trigger_type: TriggerType = TriggerType.DEVICE_CONNECTED,
    device_id: str = "USB\\TEST_DEVICE",
    actions: list[Action] | None = None,
    name: str = "Test Automation",
) -> Automation:
    return Automation(
        id="automation-001",
        name=name,
        enabled=enabled,
        trigger=Trigger(
            type=trigger_type,
            device_id=device_id,
        ),
        actions=actions or [],
    )


def test_matching_enabled_automation_executes_action():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == [
        ("display-001", "HDMI1")
    ]

    assert [
        event.event_type
        for event in repository.events
    ] == [
        "automation_triggered",
        "action",
    ]

    assert repository.events[1].success is True


def test_wrong_device_does_not_execute_automation():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\OTHER_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == []
    assert repository.events == []


def test_disabled_automation_does_not_execute():
    automation = create_automation(
        enabled=False,
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == []
    assert repository.events == []


def test_connected_event_does_not_match_disconnected_trigger():
    automation = create_automation(
        trigger_type=TriggerType.DEVICE_DISCONNECTED,
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == []
    assert repository.events == []


def test_disconnected_event_matches_disconnected_trigger():
    automation = create_automation(
        trigger_type=TriggerType.DEVICE_DISCONNECTED,
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="DVI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.DISCONNECTED,
        )
    )

    assert display_service.calls == [
        ("display-001", "DVI1")
    ]

    assert [
        event.event_type
        for event in repository.events
    ] == [
        "automation_triggered",
        "action",
    ]


def test_do_nothing_action_does_not_call_display_service():
    automation = create_automation(
        actions=[
            Action(type=ActionType.DO_NOTHING)
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == []

    assert [
        event.event_type
        for event in repository.events
    ] == [
        "automation_triggered",
    ]


def test_multiple_actions_are_all_executed():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            ),
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-002",
                input_id="DVI1",
            ),
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == [
        ("display-001", "HDMI1"),
        ("display-002", "DVI1"),
    ]

    assert [
        event.event_type
        for event in repository.events
    ] == [
        "automation_triggered",
        "action",
        "action",
    ]


def test_failed_action_creates_failed_activity_event():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )

    service, display_service, repository = create_automation_service(
        [automation]
    )

    display_service.error = RuntimeError("Monitor unavailable")

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == [
        ("display-001", "HDMI1")
    ]

    failed_event = repository.events[-1]

    assert failed_event.event_type == "action"
    assert failed_event.success is False
    assert "Failed to switch" in failed_event.message
    assert "Monitor unavailable" in failed_event.message


def test_failed_action_does_not_prevent_later_actions():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            ),
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-002",
                input_id="DVI1",
            ),
        ]
    )

    class SelectiveFailureDisplayService(FakeDisplayService):

        def switch_input(
            self,
            display_id: str | None,
            input_id: str | None,
        ) -> None:
            self.calls.append((display_id, input_id))

            if display_id == "display-001":
                raise RuntimeError("First monitor unavailable")

    display_service = SelectiveFailureDisplayService()
    repository = FakeActivityRepository()

    service = AutomationService(
        display_service=display_service,
        activity_repository=repository,
        automations=[automation],
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == [
        ("display-001", "HDMI1"),
        ("display-002", "DVI1"),
    ]

    assert repository.events[-2].success is False
    assert repository.events[-1].success is True


def test_pausing_activity_logging_keeps_automations_running():
    automation = create_automation(
        actions=[
            Action(
                type=ActionType.SWITCH_INPUT,
                display_id="display-001",
                input_id="HDMI1",
            )
        ]
    )
    service, display_service, repository = create_automation_service(
        [automation]
    )
    emitted_events = []
    service.activity_events.subscribe(emitted_events.append)
    service.set_activity_logging_paused(True)

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert display_service.calls == [("display-001", "HDMI1")]
    assert repository.events == []
    assert emitted_events == []

    service.set_activity_logging_paused(False)
    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert [event.event_type for event in repository.events] == [
        "automation_triggered",
        "action",
    ]


def test_activity_logging_can_start_disabled():
    repository = FakeActivityRepository()
    service = AutomationService(
        display_service=FakeDisplayService(),
        activity_repository=repository,
        automations=[],
        store_activity_logs=False,
    )

    service.handle_device_event(
        DeviceEvent(
            device_id="USB\\TEST_DEVICE",
            event_type=DeviceEventType.CONNECTED,
        )
    )

    assert repository.events == []