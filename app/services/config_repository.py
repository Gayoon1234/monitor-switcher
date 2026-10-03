import json
from dataclasses import asdict
from pathlib import Path

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.usb_device import ConfiguredUsbDevice

from app.models.display import (
    Display,
    DisplayInput,
    InputType,
)

class ConfigRepository:

    def __init__(self, path: str = "config.json"):
        self.path = Path(path)

    def load_usb_devices(self) -> list[ConfiguredUsbDevice]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [
            ConfiguredUsbDevice(**device)
            for device in data.get("usb_devices", [])
        ]

    def save_usb_devices(
        self,
        devices: list[ConfiguredUsbDevice],
    ) -> None:
        data = self._load()

        data["usb_devices"] = [
            asdict(device)
            for device in devices
        ]

        self._save(data)

    def load_automations(self) -> list[Automation]:
        data = self._load()

        automations = []

        for automation in data.get("automations", []):
            trigger = Trigger(
                type=TriggerType(automation["trigger"]["type"]),
                device_id=automation["trigger"]["device_id"],
            )

            actions = [
                Action(
                    type=ActionType(action["type"]),
                    display_id=action.get("display_id"),
                    input_id=action.get("input_id"),
                )
                for action in automation.get("actions", [])
            ]

            automations.append(
                Automation(
                    id=automation["id"],
                    name=automation["name"],
                    enabled=automation["enabled"],
                    trigger=trigger,
                    actions=actions,
                )
            )

        return automations

    def save_automations(
        self,
        automations: list[Automation],
    ) -> None:
        data = self._load()

        data["automations"] = [
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

        self._save(data)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}

        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, data: dict) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_displays(self) -> list[Display]:
        data = self._load()

        displays = []

        for display in data.get("displays", []):
            inputs = [
                DisplayInput(
                    input_id=input_["input_id"],
                    input_type=InputType(input_["input_type"]),
                )
                for input_ in display.get("inputs", [])
            ]

            displays.append(
                Display(
                    id=display["id"],
                    name=display["name"],
                    windows_device_id=display["windows_device_id"],
                    inputs=inputs,
                )
            )

        return displays

    def save_displays(
        self,
        displays: list[Display],
    ) -> None:
        data = self._load()

        data["displays"] = [
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

        self._save(data)