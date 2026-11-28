import json
from copy import deepcopy
from pathlib import Path
from typing import Literal, Protocol, TypeVar, cast, overload

from app.events import EventHook
from app.models.automation import Automation
from app.models.config import AppConfig, ConfigKey
from app.models.display import Display
from app.models.usb_device import ConfiguredUsbDevice


class _HasId(Protocol):
    id: str


ConfigItem = TypeVar("ConfigItem", bound=_HasId)


class ConfigRepository:

    def __init__(self, path: str | Path = "config.json"):
        self.path = Path(path)
        self._config: AppConfig | None = None
        self.config_changed: EventHook[ConfigKey] = EventHook()

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.AUTOMATIONS],
    ) -> list[Automation]: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.DISPLAYS],
    ) -> list[Display]: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.USB_DEVICES],
    ) -> list[ConfiguredUsbDevice]: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.ACTIVITY_DAYS],
    ) -> int | None: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.STORE_ACTIVITY_LOGS],
    ) -> bool: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.USB_MONITOR_ENABLED],
    ) -> bool: ...

    @overload
    def get_config(
        self,
        key: Literal[ConfigKey.USB_MONITOR_INTERVAL_MS],
    ) -> int: ...

    def get_config(self, key: ConfigKey) -> object:
        config = self._load()
        if key is ConfigKey.AUTOMATIONS:
            value = config.automations
        elif key is ConfigKey.DISPLAYS:
            value = config.displays
        elif key is ConfigKey.USB_DEVICES:
            value = config.usb_devices
        elif key is ConfigKey.ACTIVITY_DAYS:
            value = config.settings.activity_days
        elif key is ConfigKey.STORE_ACTIVITY_LOGS:
            value = config.settings.store_activity_logs
        elif key is ConfigKey.USB_MONITOR_ENABLED:
            value = config.settings.usb_monitor_enabled
        elif key is ConfigKey.USB_MONITOR_INTERVAL_MS:
            value = config.settings.usb_monitor_interval_ms
        else:
            raise ValueError(f"Unsupported configuration key: {key}")
        return deepcopy(value)

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.AUTOMATIONS],
        value: list[Automation],
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.DISPLAYS],
        value: list[Display],
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.USB_DEVICES],
        value: list[ConfiguredUsbDevice],
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.ACTIVITY_DAYS],
        value: int | None,
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.STORE_ACTIVITY_LOGS],
        value: bool,
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.USB_MONITOR_ENABLED],
        value: bool,
    ) -> None: ...

    @overload
    def update_config(
        self,
        key: Literal[ConfigKey.USB_MONITOR_INTERVAL_MS],
        value: int,
    ) -> None: ...

    def update_config(self, key: ConfigKey, value: object) -> None:
        config = deepcopy(self._load())

        if key is ConfigKey.AUTOMATIONS:
            config.automations = _validate_collection(
                value,
                Automation,
                key,
            )
        elif key is ConfigKey.DISPLAYS:
            config.displays = _validate_collection(value, Display, key)
        elif key is ConfigKey.USB_DEVICES:
            config.usb_devices = _validate_collection(
                value,
                ConfiguredUsbDevice,
                key,
            )
        elif key is ConfigKey.ACTIVITY_DAYS:
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                raise TypeError("activity_days must be an integer or None.")
            config.settings.activity_days = value
        elif key is ConfigKey.STORE_ACTIVITY_LOGS:
            if not isinstance(value, bool):
                raise TypeError(f"{key.value} must be a boolean.")
            config.settings.store_activity_logs = value
        elif key is ConfigKey.USB_MONITOR_ENABLED:
            if not isinstance(value, bool):
                raise TypeError(f"{key.value} must be a boolean.")
            config.settings.usb_monitor_enabled = value
        elif key is ConfigKey.USB_MONITOR_INTERVAL_MS:
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not 1 <= value <= 2_147_483_647
            ):
                raise ValueError(
                    "USB monitor polling interval must be between 1 and "
                    "2147483647 milliseconds."
                )
            config.settings.usb_monitor_interval_ms = value
        else:
            raise ValueError(f"Unsupported configuration key: {key}")

        self._write(config)
        self._config = config
        self.config_changed.emit(key)

    @overload
    def add_config(
        self,
        key: Literal[ConfigKey.AUTOMATIONS],
        value: Automation,
    ) -> None: ...

    @overload
    def add_config(
        self,
        key: Literal[ConfigKey.DISPLAYS],
        value: Display,
    ) -> None: ...

    @overload
    def add_config(
        self,
        key: Literal[ConfigKey.USB_DEVICES],
        value: ConfiguredUsbDevice,
    ) -> None: ...

    def add_config(self, key: ConfigKey, value: object) -> None:
        if key is ConfigKey.AUTOMATIONS:
            if not isinstance(value, Automation):
                raise TypeError(
                    "automations entries must be Automation objects."
                )
            items = self.get_config(ConfigKey.AUTOMATIONS)
            _append_unique(items, value, key)
            self.update_config(ConfigKey.AUTOMATIONS, items)
        elif key is ConfigKey.DISPLAYS:
            if not isinstance(value, Display):
                raise TypeError("displays entries must be Display objects.")
            items = self.get_config(ConfigKey.DISPLAYS)
            _append_unique(items, value, key)
            self.update_config(ConfigKey.DISPLAYS, items)
        elif key is ConfigKey.USB_DEVICES:
            if not isinstance(value, ConfiguredUsbDevice):
                raise TypeError(
                    "usb_devices entries must be ConfiguredUsbDevice objects."
                )
            items = self.get_config(ConfigKey.USB_DEVICES)
            _append_unique(items, value, key)
            self.update_config(ConfigKey.USB_DEVICES, items)
        else:
            raise ValueError(
                f"Configuration key does not contain a collection: {key}"
            )

    @overload
    def remove_config(
        self,
        key: Literal[ConfigKey.AUTOMATIONS],
        value: str,
    ) -> bool: ...

    @overload
    def remove_config(
        self,
        key: Literal[ConfigKey.DISPLAYS],
        value: str,
    ) -> bool: ...

    @overload
    def remove_config(
        self,
        key: Literal[ConfigKey.USB_DEVICES],
        value: str,
    ) -> bool: ...

    def remove_config(self, key: ConfigKey, value: str) -> bool:
        if not isinstance(value, str):
            raise TypeError("Collection item ids must be strings.")

        if key is ConfigKey.AUTOMATIONS:
            items = self.get_config(ConfigKey.AUTOMATIONS)
            updated_items = _without_id(items, value)
            if updated_items is None:
                return False
            self.update_config(ConfigKey.AUTOMATIONS, updated_items)
        elif key is ConfigKey.DISPLAYS:
            items = self.get_config(ConfigKey.DISPLAYS)
            updated_items = _without_id(items, value)
            if updated_items is None:
                return False
            self.update_config(ConfigKey.DISPLAYS, updated_items)
        elif key is ConfigKey.USB_DEVICES:
            items = self.get_config(ConfigKey.USB_DEVICES)
            updated_items = _without_id(items, value)
            if updated_items is None:
                return False
            self.update_config(ConfigKey.USB_DEVICES, updated_items)
        else:
            raise ValueError(
                f"Configuration key does not contain a collection: {key}"
            )

        return True

    def _load(self) -> AppConfig:
        if self._config is not None:
            return self._config

        if not self.path.exists():
            self._config = AppConfig()
            return self._config

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        self._config = AppConfig.from_dict(data)
        return self._config

    def _write(self, config: AppConfig) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(config.to_dict(), file, indent=4)

def _validate_collection(
    value: object,
    item_type: type[ConfigItem],
    key: ConfigKey,
) -> list[ConfigItem]:
    if not isinstance(value, list) or not all(
        isinstance(item, item_type)
        for item in value
    ):
        raise TypeError(
            f"{key.value} must be a list of {item_type.__name__} objects."
        )

    ids = [item.id for item in cast(list[ConfigItem], value)]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{key.value} contains duplicate ids.")
    return cast(list[ConfigItem], value)


def _append_unique(
    items: list[ConfigItem],
    value: ConfigItem,
    key: ConfigKey,
) -> None:
    if any(item.id == value.id for item in items):
        raise ValueError(
            f"{key.value} already contains an item with id {value.id!r}."
        )
    items.append(value)


def _without_id(
    items: list[ConfigItem],
    identifier: str,
) -> list[ConfigItem] | None:
    updated = [item for item in items if item.id != identifier]
    return updated if len(updated) != len(items) else None
