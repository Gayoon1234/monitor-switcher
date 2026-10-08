from app.models.display import Display, DisplayInput, InputType
from app.services.display_service import DisplayService


class FakeDisplayRepository:
    def __init__(self, displays=None):
        self.displays = displays or []
        self.saved_displays = []

    def load_displays(self):
        return list(self.displays)

    def save_displays(self, displays):
        self.saved_displays.append(list(displays))


class FakeDisplayDiscovery:
    def __init__(self, displays=None):
        self.displays = displays or []
        self.calls = 0

    def get_displays(self):
        self.calls += 1
        return list(self.displays)


class FakeMonitorController:
    def __init__(self):
        self.set_displays_calls = []
        self.switch_input_calls = []
        self.error = None

    def set_displays(self, displays):
        self.set_displays_calls.append(list(displays))

    def switch_input(self, display_id, input_id):
        self.switch_input_calls.append((display_id, input_id))

        if self.error is not None:
            raise self.error


def create_display(
    *,
    display_id="display-001",
    name="Test Monitor",
    windows_device_id="DISPLAY\\TEST",
    inputs=None,
    current_input=None,
):
    return Display(
        id=display_id,
        name=name,
        windows_device_id=windows_device_id,
        inputs=inputs or [],
        current_input=current_input,
    )


def create_service(
    *,
    repository_displays=None,
    discovered_displays=None,
):
    repository = FakeDisplayRepository(repository_displays)
    discovery = FakeDisplayDiscovery(discovered_displays)
    controller = FakeMonitorController()

    service = DisplayService(
        monitor_controller=controller,
        display_discovery=discovery,
        repository=repository,
    )

    return service, repository, discovery, controller


def test_loads_displays_from_repository():
    display = create_display(
        current_input=None,
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
        ],
    )

    service, repository, discovery, controller = create_service(
        repository_displays=[display],
        discovered_displays=[],
    )

    assert service.get_displays() == [display]
    assert discovery.calls == 1
    assert controller.set_displays_calls == [[display]]


def test_discovers_and_saves_displays_when_repository_is_empty():
    display = create_display(
        current_input="HDMI1",
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
        ],
    )

    service, repository, discovery, controller = create_service(
        repository_displays=[],
        discovered_displays=[display],
    )

    assert service.get_displays() == [display]
    assert repository.saved_displays == [[display]]
    assert discovery.calls == 1
    assert controller.set_displays_calls == [[display]]


def test_refresh_displays_discovers_saves_and_updates_controller():
    initial_display = create_display(
        name="Old Monitor",
        windows_device_id="DISPLAY\\OLD",
    )
    refreshed_display = create_display(
        name="New Monitor",
        windows_device_id="DISPLAY\\NEW",
    )

    service, repository, discovery, controller = create_service(
        repository_displays=[initial_display],
        discovered_displays=[refreshed_display],
    )

    repository.saved_displays.clear()
    controller.set_displays_calls.clear()

    result = service.refresh_displays()

    assert result == [refreshed_display]
    assert service.get_displays() == [refreshed_display]
    assert repository.saved_displays == [[refreshed_display]]
    assert controller.set_displays_calls == [[refreshed_display]]
    assert discovery.calls == 2


def test_refresh_displays_updates_current_inputs():
    saved_display = create_display(
        name="Test Monitor",
        windows_device_id="DISPLAY\\TEST",
        current_input=None,
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
        ],
    )

    live_display = create_display(
        name="Test Monitor",
        windows_device_id="DISPLAY\\TEST",
        current_input="HDMI1",
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
        ],
    )

    service, _, _, _ = create_service(
        repository_displays=[saved_display],
        discovered_displays=[live_display],
    )

    assert service.get_displays()[0].current_input == "HDMI1"


def test_switch_input_updates_controller_and_display():
    display = create_display(
        current_input="HDMI1",
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
            DisplayInput("ANALOG1", InputType.ANALOG),
        ],
    )

    service, _, _, controller = create_service(
        repository_displays=[display],
        discovered_displays=[display],
    )

    service.switch_input("display-001", "ANALOG1")

    assert controller.switch_input_calls == [
        ("display-001", "ANALOG1"),
    ]
    assert display.current_input == "ANALOG1"


def test_switch_input_does_not_update_display_when_controller_fails():
    display = create_display(
        current_input="HDMI1",
        inputs=[
            DisplayInput("HDMI1", InputType.HDMI),
            DisplayInput("ANALOG1", InputType.ANALOG),
        ],
    )

    service, _, _, controller = create_service(
        repository_displays=[display],
        discovered_displays=[display],
    )

    controller.error = RuntimeError("Monitor unavailable")

    try:
        service.switch_input("display-001", "ANALOG1")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError")

    assert controller.switch_input_calls == [
        ("display-001", "ANALOG1"),
    ]
    assert display.current_input == "HDMI1"


def test_switch_input_unknown_display_raises_error():
    display = create_display()

    service, _, _, controller = create_service(
        repository_displays=[display],
        discovered_displays=[display],
    )

    try:
        service.switch_input("display-999", "HDMI1")
    except ValueError as error:
        assert str(error) == "Display not found: display-999"
    else:
        raise AssertionError("Expected ValueError")

    assert controller.switch_input_calls == []