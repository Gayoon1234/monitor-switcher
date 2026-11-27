import logging

from app.models.device_event import DeviceEventType
from app.services.usb_monitor_service import UsbMonitorService


def test_device_state_changes_emit_connected_and_disconnected_events():
    service = UsbMonitorService("USB\\TEST_DEVICE")
    events = []
    service.device_events.subscribe(events.append)

    service.handle_state(True)
    service.handle_state(False)

    assert [
        (event.device_id, event.event_type)
        for event in events
    ] == [
        ("USB\\TEST_DEVICE", DeviceEventType.CONNECTED),
        ("USB\\TEST_DEVICE", DeviceEventType.DISCONNECTED),
    ]


def test_monitoring_baseline_does_not_emit_for_already_connected_device():
    service = UsbMonitorService("USB\\TEST_DEVICE")
    events = []
    service.device_events.subscribe(events.append)

    service.begin_monitoring()
    service.handle_state(True)
    service.handle_state(True)

    assert service.previous_connected is True
    assert events == []


def test_all_device_mode_emits_sorted_additions_and_removals():
    service = UsbMonitorService()
    service.previous_connected = {"USB\\B", "USB\\C"}
    events = []
    service.device_events.subscribe(events.append)

    service.handle_state({"USB\\A", "USB\\B"})

    assert [
        (event.device_id, event.event_type)
        for event in events
    ] == [
        ("USB\\A", DeviceEventType.CONNECTED),
        ("USB\\C", DeviceEventType.DISCONNECTED),
    ]
    assert service.previous_connected == {"USB\\A", "USB\\B"}


def test_poll_error_leaves_previous_state_and_clears_initial_baseline(caplog):
    service = UsbMonitorService("USB\\TEST_DEVICE")
    service.begin_monitoring()
    service.handle_poll_error(RuntimeError("WMI unavailable"))

    assert service._baseline_pending is False
    assert service.previous_connected is False
    assert "Failed to initialize USB monitoring state" in caplog.text
    assert caplog.records[-1].levelno == logging.ERROR


def test_stop_cancels_pending_baseline():
    service = UsbMonitorService("USB\\TEST_DEVICE")
    service.begin_monitoring()
    service.stop_monitoring()

    assert service._baseline_pending is False
