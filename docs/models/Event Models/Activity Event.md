---
id: activity-event
title: Activity Event
sidebar_position: 1
---

## Activity events

Activity Events are used to store when certain events are triggered. These can be automations being triggered, displays changing or devices connecting/disconnecting.

For example, if an automation is triggered, that would create a "Automation triggered" event, then if that automation defines multiple actions, each action will create an additional event.

These events are stored in the activitydb, which is a sqllite DB. It is what generates the most logs.

In the UI there is a dedicated Activity Tab that lets the user view recent events. The settings tab allows the user to change the time period for when logs are shown as well as the option to delete all logs.

## Model definition

```python
@dataclass
class ActivityEvent:
    timestamp: datetime
    event_type: str
    message: str
    success: bool
```

- timestamp: This is automatically aded by the automation service which creates methods.
- event_type: This can be device_event, automation_triggered or action, although there is no hard validation.
- message: This is a free-text field that is used to store the event being triggered.
- success: This is a bool, and it's only set to false if the event is emitted from a catch block in the try/catch blocks when the internal code interacts with the hardware.
