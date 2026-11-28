from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.display import Display, DisplayInput, InputType
from app.models.usb_device import ConfiguredUsbDevice


class ConfigKey(Enum):
    AUTOMATIONS = "automations"
    DISPLAYS = "displays"
    USB_DEVICES = "usb_devices"
    SETTINGS = "settings"


@dataclass
class AppSettings:
    activity_days: int | None = 30
    store_activity_logs: bool = True
    usb_monitor_enabled: bool = True
    usb_monitor_interval_ms: int = 500


@dataclass
class AppConfig:
    automations: list[Automation] = field(default_factory=list)
    displays: list[Display] = field(default_factory=list)
    usb_devices: list[ConfiguredUsbDevice] = field(default_factory=list)
    settings: AppSettings = field(default_factory=AppSettings)
    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: object) -> "AppConfig":
        root = _require_dict(data, "Configuration")
        raw_settings = _require_dict(
            root.get("settings", {}),
            "Application settings",
        )

        legacy_activity_days = root.get("activity_days", 30)
        settings = AppSettings(
            activity_days=_optional_int(
                raw_settings.get("activity_days", legacy_activity_days),
                "activity_days",
            ),
            store_activity_logs=_bool(
                raw_settings.get("store_activity_logs", True),
                "store_activity_logs",
            ),
            usb_monitor_enabled=_bool(
                raw_settings.get("usb_monitor_enabled", True),
                "usb_monitor_enabled",
            ),
            usb_monitor_interval_ms=_positive_int(
                raw_settings.get("usb_monitor_interval_ms", 500),
                "usb_monitor_interval_ms",
            ),
        )

        known_keys = {
            "automations",
            "displays",
            "usb_devices",
            "settings",
            "activity_days",
        }
        return cls(
            automations=[
                _automation(value)
                for value in _require_list(
                    root.get("automations", []),
                    "automations",
                )
            ],
            displays=[
                _display(value)
                for value in _require_list(root.get("displays", []), "displays")
            ],
            usb_devices=[
                _usb_device(value)
                for value in _require_list(
                    root.get("usb_devices", []),
                    "usb_devices",
                )
            ],
            settings=settings,
            extra={
                key: value
                for key, value in root.items()
                if key not in known_keys
            },
        )

    def to_dict(self) -> dict[str, Any]:
        data = dict(self.extra)
        data.update(
            {
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
                    for automation in self.automations
                ],
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
                    for display in self.displays
                ],
                "usb_devices": [
                    {
                        "id": device.id,
                        "windows_device_id": device.windows_device_id,
                        "nickname": device.nickname,
                    }
                    for device in self.usb_devices
                ],
                "settings": {
                    "activity_days": self.settings.activity_days,
                    "store_activity_logs": self.settings.store_activity_logs,
                    "usb_monitor_enabled": self.settings.usb_monitor_enabled,
                    "usb_monitor_interval_ms": (
                        self.settings.usb_monitor_interval_ms
                    ),
                },
            }
        )
        return data


def _require_dict(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


def _require_list(value: object, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array.")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string.")
    return value


def _bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean.")
    return value


def _optional_string(value: object, name: str) -> str | None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{name} must be a string or null.")
    return value


def _optional_int(value: object, name: str) -> int | None:
    if value is not None and (
        not isinstance(value, int) or isinstance(value, bool)
    ):
        raise ValueError(f"{name} must be an integer or null.")
    return value


def _positive_int(value: object, name: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= 2_147_483_647
    ):
        raise ValueError(
            f"{name} must be between 1 and 2147483647."
        )
    return value


def _automation(value: object) -> Automation:
    data = _require_dict(value, "Automation")
    trigger_data = _require_dict(data.get("trigger"), "Automation trigger")
    try:
        trigger = Trigger(
            type=TriggerType(_string(trigger_data.get("type"), "trigger.type")),
            device_id=_string(
                trigger_data.get("device_id"),
                "trigger.device_id",
            ),
        )
        actions = [
            Action(
                type=ActionType(_string(action.get("type"), "action.type")),
                display_id=_optional_string(
                    action.get("display_id"),
                    "action.display_id",
                ),
                input_id=_optional_string(
                    action.get("input_id"),
                    "action.input_id",
                ),
            )
            for action in (
                _require_dict(item, "Automation action")
                for item in _require_list(
                    data.get("actions", []),
                    "automation.actions",
                )
            )
        ]
    except ValueError as error:
        raise ValueError(f"Invalid automation: {error}") from error

    return Automation(
        id=_string(data.get("id"), "automation.id"),
        name=_string(data.get("name"), "automation.name"),
        enabled=_bool(data.get("enabled"), "automation.enabled"),
        trigger=trigger,
        actions=actions,
    )


def _display(value: object) -> Display:
    data = _require_dict(value, "Display")
    try:
        inputs = [
            DisplayInput(
                input_id=_string(item.get("input_id"), "input.input_id"),
                input_type=InputType(
                    _string(item.get("input_type"), "input.input_type")
                ),
            )
            for item in (
                _require_dict(item, "Display input")
                for item in _require_list(
                    data.get("inputs", []),
                    "display.inputs",
                )
            )
        ]
    except ValueError as error:
        raise ValueError(f"Invalid display: {error}") from error

    return Display(
        id=_string(data.get("id"), "display.id"),
        name=_string(data.get("name"), "display.name"),
        windows_device_id=_string(
            data.get("windows_device_id"),
            "display.windows_device_id",
        ),
        inputs=inputs,
    )


def _usb_device(value: object) -> ConfiguredUsbDevice:
    data = _require_dict(value, "USB device")
    return ConfiguredUsbDevice(
        id=_string(data.get("id"), "usb_device.id"),
        windows_device_id=_string(
            data.get("windows_device_id"),
            "usb_device.windows_device_id",
        ),
        nickname=_string(data.get("nickname"), "usb_device.nickname"),
    )
