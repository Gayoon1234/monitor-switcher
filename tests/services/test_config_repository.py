import json

import pytest

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.config import AppConfig, AppSettings, ConfigKey
from app.models.display import Display, DisplayInput, InputType
from app.models.usb_device import ConfiguredUsbDevice
from app.services.config_repository import ConfigRepository


def make_automation(automation_id="automation-1"):
    return Automation(
        id=automation_id,
        name="Test Automation",
        enabled=True,
        trigger=Trigger(TriggerType.DEVICE_CONNECTED, "device-1"),
        actions=[
            Action(
                ActionType.SWITCH_INPUT,
                display_id="display-1",
                input_id="HDMI1",
            )
        ],
    )


def make_display(display_id="display-1"):
    return Display(
        id=display_id,
        name="Test Display",
        windows_device_id="DISPLAY\\TEST",
        inputs=[DisplayInput("HDMI1", InputType.HDMI)],
    )


def make_usb_device(device_id="device-1"):
    return ConfiguredUsbDevice(
        id=device_id,
        windows_device_id="USB\\TEST",
        nickname="Test Device",
    )


def test_get_config_loads_typed_models(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "automations": AppConfig(
                    automations=[make_automation()]
                ).to_dict()["automations"],
                "displays": AppConfig(
                    displays=[make_display()]
                ).to_dict()["displays"],
                "usb_devices": [
                    {
                        "id": "device-1",
                        "windows_device_id": "USB\\TEST",
                        "nickname": "Test Device",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    repository = ConfigRepository(config_path)

    assert repository.get_config(ConfigKey.AUTOMATIONS) == [
        make_automation()
    ]
    assert repository.get_config(ConfigKey.DISPLAYS) == [make_display()]
    assert repository.get_config(ConfigKey.USB_DEVICES) == [
        make_usb_device()
    ]


def test_add_and_remove_config_items_persist_and_notify(tmp_path):
    repository = ConfigRepository(tmp_path / "config.json")
    changes = []
    repository.config_changed.subscribe(changes.append)

    repository.add_config(ConfigKey.DISPLAYS, make_display())
    repository.add_config(ConfigKey.USB_DEVICES, make_usb_device())

    assert repository.remove_config(ConfigKey.DISPLAYS, "display-1")
    assert repository.remove_config(ConfigKey.USB_DEVICES, "device-1")
    assert not repository.remove_config(ConfigKey.USB_DEVICES, "missing")
    assert changes == [
        ConfigKey.DISPLAYS,
        ConfigKey.USB_DEVICES,
        ConfigKey.DISPLAYS,
        ConfigKey.USB_DEVICES,
    ]

    saved_data = json.loads(
        (tmp_path / "config.json").read_text(encoding="utf-8")
    )
    assert saved_data["displays"] == []
    assert saved_data["usb_devices"] == []


def test_add_config_rejects_wrong_types_and_duplicate_ids(tmp_path):
    repository = ConfigRepository(tmp_path / "config.json")
    repository.add_config(ConfigKey.DISPLAYS, make_display())

    with pytest.raises(TypeError, match="Display objects"):
        repository.add_config(ConfigKey.DISPLAYS, make_usb_device())
    with pytest.raises(ValueError, match="already contains"):
        repository.add_config(ConfigKey.DISPLAYS, make_display())


def test_update_config_persists_values_and_returns_isolated_copies(tmp_path):
    config_path = tmp_path / "config.json"
    repository = ConfigRepository(config_path)
    automations = [make_automation()]
    repository.update_config(ConfigKey.AUTOMATIONS, automations)
    repository.update_config(
        ConfigKey.SETTINGS,
        AppSettings(
            activity_days=7,
            store_activity_logs=False,
            usb_monitor_enabled=False,
            usb_monitor_interval_ms=1250,
        ),
    )

    returned_automations = repository.get_config(ConfigKey.AUTOMATIONS)
    returned_automations.clear()
    returned_settings = repository.get_config(ConfigKey.SETTINGS)
    returned_settings.activity_days = 90

    reloaded = ConfigRepository(config_path)
    assert reloaded.get_config(ConfigKey.AUTOMATIONS) == [make_automation()]
    assert reloaded.get_config(ConfigKey.SETTINGS) == AppSettings(
        activity_days=7,
        store_activity_logs=False,
        usb_monitor_enabled=False,
        usb_monitor_interval_ms=1250,
    )


def test_settings_default_values_and_legacy_migration(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"activity_days": 7, "other_setting": "keep"}),
        encoding="utf-8",
    )
    repository = ConfigRepository(config_path)

    assert repository.get_config(ConfigKey.SETTINGS) == AppSettings(
        activity_days=7,
        store_activity_logs=True,
        usb_monitor_enabled=True,
        usb_monitor_interval_ms=500,
    )

    settings = repository.get_config(ConfigKey.SETTINGS)
    settings.activity_days = 30
    repository.update_config(ConfigKey.SETTINGS, settings)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["settings"] == {
        "activity_days": 30,
        "store_activity_logs": True,
        "usb_monitor_enabled": True,
        "usb_monitor_interval_ms": 500,
    }
    assert data["other_setting"] == "keep"
    assert "activity_days" not in data


def test_activity_days_can_be_none(tmp_path):
    repository = ConfigRepository(tmp_path / "config.json")
    settings = repository.get_config(ConfigKey.SETTINGS)
    settings.activity_days = None
    repository.update_config(ConfigKey.SETTINGS, settings)

    assert repository.get_config(ConfigKey.SETTINGS).activity_days is None


def test_invalid_config_types_are_rejected(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"settings": {"usb_monitor_enabled": "yes"}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be a boolean"):
        ConfigRepository(config_path).get_config(ConfigKey.SETTINGS)


def test_usb_monitor_interval_requires_positive_integer(tmp_path):
    repository = ConfigRepository(tmp_path / "config.json")

    with pytest.raises(ValueError, match="polling interval"):
        repository.update_config(
            ConfigKey.SETTINGS,
            AppSettings(usb_monitor_interval_ms=0),
        )


def test_invalid_json_is_reported(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        ConfigRepository(config_path).get_config(ConfigKey.DISPLAYS)
