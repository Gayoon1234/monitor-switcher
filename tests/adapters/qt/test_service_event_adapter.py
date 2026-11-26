from types import SimpleNamespace

from app.adapters.qt.service_event_adapter import QtServiceEventAdapter
from app.events import EventHook


def test_qt_adapter_bridges_service_events_and_unsubscribes_on_close(qapp):
    activity_events = EventHook()
    devices_changed = EventHook()
    automation_service = SimpleNamespace(activity_events=activity_events)
    usb_service = SimpleNamespace(devices_changed=devices_changed)
    adapter = QtServiceEventAdapter(automation_service, usb_service)
    activities = []
    device_notifications = []
    adapter.activity_event.connect(activities.append)
    adapter.usb_devices_changed.connect(
        lambda: device_notifications.append(True)
    )

    activity_events.emit("activity")
    devices_changed.emit(None)
    adapter.close()
    activity_events.emit("ignored")
    devices_changed.emit(None)

    assert activities == ["activity"]
    assert device_notifications == [True]
