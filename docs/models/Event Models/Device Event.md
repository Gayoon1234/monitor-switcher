---
id: device-event
title: Device Event
sidebar_position: 2
---

## Device events

Device events represent USB state changes detected by the application. The USB monitor emits a `DeviceEvent` when a configured or detected device connects or disconnects.

The `AutomationService` handles these events and compares their type against automation triggers. A matching connected or disconnected trigger can then execute the automation's actions.

## Model definition

```python
class DeviceEventType(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

@dataclass
class DeviceEvent:
    device_id: str
    event_type: DeviceEventType
```

- `DeviceEventType`: Restricts the USB state change to one of two values: `CONNECTED` or `DISCONNECTED`.
- `device_id`: The internal identifier of the USB device associated with the state change.
- `event_type`: The type of state change represented by the event.

The class currently has no relationship enforcement between a device ID and the corresponding saved device configuration.
