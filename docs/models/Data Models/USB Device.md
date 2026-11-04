---
id: usb-device
title: USB Device
sidebar_position: 2
---

`UsbDevice` is used in the usb discovery (in the UI this is the `Find my Device` tab), whereas `ConfiguredUsbDevice` is used to store devices that have been saved already. Only the latter can be used in automations.

`ConfiguredUsbDevice` objects are saved in the config.json file, whereas `UsbDevice` objects are calculated on the fly based on what Windows reports. The library `win32com` is used for all USB interactions.

## Model definition

```python
@dataclass
class UsbDevice:
    windows_device_id: str
    name: str

@dataclass
class ConfiguredUsbDevice:
    id: str
    windows_device_id: str
    nickname: str
```

- `windows_device_id` (`UsbDevice`/`ConfiguredUsbDevice`): The Windows device identifier for a connected USB device. This is the standard name that is used to monitor connections via 3rd party libraries.
- `name` (`UsbDevice`): The name reported for the connected USB device.
- `id` (`ConfiguredUsbDevice`): The internal identifier used to store and reference the configured USB device.
- `nickname` (`ConfiguredUsbDevice`): The user-friendly name assigned to the configured USB device and used in the UI.
