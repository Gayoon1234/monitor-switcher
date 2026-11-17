---
title: AutomationService
---

`AutomationService` handles USB [`DeviceEvent`](../models/Event%20Models/device-event)
values, checks them against configured [`Automation`](../models/Data%20Models/automation)
objects, and executes matching actions. It depends on a `DisplayService` for
input switching and an `ActivityRepository` for history.

## Construction

```python
AutomationService(display_service, activity_repository, automations)
```

The service is a Qt `QObject` and exposes the `activity_event` signal. The
signal emits each `ActivityEvent` after it has been appended to the repository.

## Event handling

Call `handle_device_event(event)` when the USB monitor reports a connection or
disconnection. The service:

1. Records a successful `device_event`.
2. Checks each automation, skipping disabled entries and requiring both the
   configured device ID and connected/disconnected trigger type to match.
3. Records an `automation_triggered` event and runs the matching automation's
   actions in order.

`DO_NOTHING` actions are skipped. `SWITCH_INPUT` actions call
`DisplayService.switch_input(display_id, input_id)`. A failed switch is logged
and recorded as a failed `action` event; remaining actions continue.

## Activity methods

- `get_activity_history(days=30)` delegates to `ActivityRepository.load`.
- `clear_activity_history()` clears the repository.

Automations are passed in at construction and held as a list; this service does
not load or save them itself.
