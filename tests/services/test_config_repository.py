import json
from dataclasses import asdict

import pytest

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


def test_activity_days_default_to_30_and_persist_selection(tmp_path):
    config_path = tmp_path / "config.json"
    repository = ConfigRepository(path=config_path)

    assert repository.load_activity_days() == 30

    repository.save_activity_days(7)
    reloaded_repository = ConfigRepository(path=config_path)

    assert reloaded_repository.load_activity_days() == 7
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["settings"] == {
        "activity_days": 7,
        "store_activity_logs": True,
        "usb_monitor_enabled": True,
        "usb_monitor_interval_ms": 500,
    }
    assert "activity_days" not in data


def test_activity_days_can_persist_all_activity(tmp_path):
    config_path = tmp_path / "config.json"
    repository = ConfigRepository(path=config_path)

    repository.save_activity_days(None)

    assert ConfigRepository(path=config_path).load_activity_days() is None


def test_legacy_activity_days_are_migrated_into_settings(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"activity_days": 7, "other_setting": "keep"}),
        encoding="utf-8",
    )
    repository = ConfigRepository(path=config_path)

    assert repository.load_activity_days() == 7
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data == {
        "other_setting": "keep",
        "settings": {
            "activity_days": 7,
            "store_activity_logs": True,
            "usb_monitor_enabled": True,
            "usb_monitor_interval_ms": 500,
        },
    }


def test_store_activity_logs_default_and_persist(tmp_path):
    config_path = tmp_path / "config.json"
    repository = ConfigRepository(path=config_path)

    assert repository.load_store_activity_logs() is True
    repository.save_store_activity_logs(False)

    assert ConfigRepository(path=config_path).load_store_activity_logs() is False


def test_usb_monitor_settings_default_and_persist(tmp_path):
    config_path = tmp_path / "config.json"
    repository = ConfigRepository(path=config_path)

    assert repository.load_usb_monitor_enabled() is True
    assert repository.load_usb_monitor_interval_ms() == 500

    repository.save_usb_monitor_enabled(False)
    repository.save_usb_monitor_interval_ms(1250)
    reloaded_repository = ConfigRepository(path=config_path)

    assert reloaded_repository.load_usb_monitor_enabled() is False
    assert reloaded_repository.load_usb_monitor_interval_ms() == 1250
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["settings"]["usb_monitor_enabled"] is False
    assert data["settings"]["usb_monitor_interval_ms"] == 1250


def test_usb_monitor_interval_rejects_non_positive_values(tmp_path):
    repository = ConfigRepository(path=tmp_path / "config.json")

    with pytest.raises(ValueError, match="polling interval"):
        repository.save_usb_monitor_interval_ms(0)
