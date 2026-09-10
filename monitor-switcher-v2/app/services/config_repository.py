import json
from pathlib import Path
from dataclasses import asdict

from app.models.usb_device import ConfiguredUsbDevice


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
        data = {
            "usb_devices": [
                asdict(device)
                for device in devices
            ]
        }

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)