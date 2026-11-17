---
title: Usb
sidebar_position: 2
---

## What this class does

This class is the abstract definition to interact with USB devices. All it does is get connected USB devices.

## Abstract Class definition

```python
class UsbDeviceMonitor(ABC):

    @abstractmethod
    def get_devices(self) -> list[UsbDevice]:
        pass
```

- `get_devices()`: Returns all USB devices connected as `UsbDevice` models.
