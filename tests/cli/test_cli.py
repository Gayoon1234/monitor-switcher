from app.cli.main import build_parser
from app.cli.commands.automations import _next_automation_id


def test_cli_parser_accepts_activity_and_hardware_commands():
    parser = build_parser()

    activity = parser.parse_args(["activity", "list", "--days", "all"])
    devices = parser.parse_args(["my-devices", "displays", "switch", "display-001", "HDMI1"])

    assert activity.command == "activity"
    assert activity.days == "all"
    assert devices.command == "my-devices"
    assert devices.display_action == "switch"


def test_automation_ids_use_first_available_sequence():
    class ExistingAutomation:
        def __init__(self, automation_id):
            self.id = automation_id

    automations = [
        ExistingAutomation("automation-001"),
        ExistingAutomation("automation-003"),
    ]

    assert _next_automation_id(automations) == "automation-002"
