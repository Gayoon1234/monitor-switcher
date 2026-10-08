import json
from dataclasses import asdict

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.display import (
    Display,
    DisplayInput,
    InputType,
)
from app.models.usb_device import ConfiguredUsbDevice
from app.services.config_repository import ConfigRepository


def test_load_usb_devices(tmp_path):
    config_path = tmp_path / "config.json"

    usb_devices = [
        ConfiguredUsbDevice(
            id="device1",
            windows_device_id="USB\\TEST_DEVICE",
            nickname="Test Device",
        )
    ]

    data = {
        "usb_devices": [asdict(device) for device in usb_devices]
    }

    config_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )

    repository = ConfigRepository(path=config_path)

    loaded_devices = repository.load_usb_devices()

    assert loaded_devices == usb_devices


def test_save_usb_devices(tmp_path):
    config_path = tmp_path / "config.json"

    usb_devices = [
        ConfiguredUsbDevice(
            id="device1",
            windows_device_id="USB\\TEST_DEVICE",
            nickname="Test Device",
        )
    ]

    repository = ConfigRepository(path=config_path)

    repository.save_usb_devices(usb_devices)

    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert data["usb_devices"] == [
        asdict(device)
        for device in usb_devices
    ]


def test_load_automations(tmp_path):
    config_path = tmp_path / "config.json"

    automations = [
        Automation(
            id="automation1",
            name="Test Automation",
            enabled=True,
            trigger=Trigger(
                type=TriggerType.DEVICE_CONNECTED,
                device_id="device1",
            ),
            actions=[
                Action(
                    type=ActionType.SWITCH_INPUT,
                    display_id="display1",
                    input_id="HDMI1",
                )
            ],
        )
    ]

    data = {
        "automations": [
            {
                "id": automation.id,
                "name": automation.name,
                "enabled": automation.enabled,
                "trigger": {
                    "type": automation.trigger.type.value,
                    "device_id": automation.trigger.device_id,
                },
                "actions": [
                    {
                        "type": action.type.value,
                        "display_id": action.display_id,
                        "input_id": action.input_id,
                    }
                    for action in automation.actions
                ],
            }
            for automation in automations
        ]
    }

    config_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )

    repository = ConfigRepository(path=config_path)

    loaded_automations = repository.load_automations()

    assert loaded_automations == automations


def test_save_automations(tmp_path):
    config_path = tmp_path / "config.json"

    automations = [
        Automation(
            id="automation1",
            name="Test Automation",
            enabled=True,
            trigger=Trigger(
                type=TriggerType.DEVICE_CONNECTED,
                device_id="device1",
            ),
            actions=[
                Action(
                    type=ActionType.SWITCH_INPUT,
                    display_id="display1",
                    input_id="HDMI1",
                )
            ],
        )
    ]

    repository = ConfigRepository(path=config_path)

    repository.save_automations(automations)

    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert data["automations"] == [
        {
            "id": automation.id,
            "name": automation.name,
            "enabled": automation.enabled,
            "trigger": {
                "type": automation.trigger.type.value,
                "device_id": automation.trigger.device_id,
            },
            "actions": [
                {
                    "type": action.type.value,
                    "display_id": action.display_id,
                    "input_id": action.input_id,
                }
                for action in automation.actions
            ],
        }
        for automation in automations
    ]


def test_load_displays(tmp_path):
    config_path = tmp_path / "config.json"

    displays = [
        Display(
            id="display1",
            name="Test Display",
            windows_device_id="DISPLAY\\TEST",
            inputs=[
                DisplayInput(
                    input_id="HDMI1",
                    input_type=InputType.HDMI,
                )
            ],
        )
    ]

    data = {
        "displays": [
            {
                "id": display.id,
                "name": display.name,
                "windows_device_id": display.windows_device_id,
                "inputs": [
                    {
                        "input_id": input_.input_id,
                        "input_type": input_.input_type.value,
                    }
                    for input_ in display.inputs
                ],
            }
            for display in displays
        ]
    }

    config_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )

    repository = ConfigRepository(path=config_path)

    loaded_displays = repository.load_displays()

    assert loaded_displays == displays


def test_save_displays(tmp_path):
    config_path = tmp_path / "config.json"

    displays = [
        Display(
            id="display1",
            name="Test Display",
            windows_device_id="DISPLAY\\TEST",
            inputs=[
                DisplayInput(
                    input_id="HDMI1",
                    input_type=InputType.HDMI,
                )
            ],
        )
    ]

    repository = ConfigRepository(path=config_path)

    repository.save_displays(displays)

    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert data["displays"] == [
        {
            "id": display.id,
            "name": display.name,
            "windows_device_id": display.windows_device_id,
            "inputs": [
                {
                    "input_id": input_.input_id,
                    "input_type": input_.input_type.value,
                }
                for input_ in display.inputs
            ],
        }
        for display in displays
    ]
