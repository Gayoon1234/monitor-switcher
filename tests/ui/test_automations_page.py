from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.ui.pages.automations import AutomationsPage
from app.ui.widgets.automation_editor import ActionWidget


class RepositoryStub:
    def __init__(self, automations=None):
        self.automations = automations or []

    def load_automations(self):
        return self.automations


class DisplayServiceStub:
    def get_displays(self):
        return []


class UsbServiceStub:
    def get_configured_devices(self):
        return []


def make_automation(name, enabled):
    return Automation(
        id=f"{name.lower()}-id",
        name=name,
        enabled=enabled,
        trigger=Trigger(
            TriggerType.DEVICE_CONNECTED,
            "USB\\DEVICE",
        ),
        actions=[
            Action(
                ActionType.SWITCH_INPUT,
                "display-1",
                "HDMI1",
            )
        ],
    )


def test_automations_page_shows_empty_state(qapp):
    page = AutomationsPage(
        RepositoryStub(),
        DisplayServiceStub(),
        UsbServiceStub(),
    )

    assert page.summary.text() == "Nothing is running yet"
    assert page.automations_layout.count() == 1
    assert page.automations_layout.itemAt(0).widget() is page.empty_state
    assert page.add_button.text() == "＋  Add automation"


def test_automations_page_summarizes_and_displays_cards(qapp):
    automations = [
        make_automation("Dock connects", True),
        make_automation("Console connects", False),
    ]
    page = AutomationsPage(
        RepositoryStub(automations),
        DisplayServiceStub(),
        UsbServiceStub(),
    )

    assert page.summary.text() == "2 automations  ·  1 enabled"
    assert page.automations_layout.count() == 2
    assert page.automations_layout.itemAt(0).widget().objectName() == (
        "automationCard"
    )
    assert page.automations_layout.itemAt(0).widget().findChild(
        type(page.empty_state),
        "automationStatus",
    ).text() == "Enabled"


def test_do_nothing_action_disables_display_controls(qapp):
    action = ActionWidget(
        displays=[],
        action=Action(ActionType.DO_NOTHING),
    )

    assert not action.display_combo.isEnabled()
    assert not action.input_combo.isEnabled()
