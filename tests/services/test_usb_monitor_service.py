from PySide6.QtCore import QCoreApplication

from app.hardware.usb import UsbDeviceMonitor
from app.models.device_event import DeviceEventType
from app.models.usb_device import UsbDevice
from app.services.usb_monitor_service import UsbMonitorService


class FakeUsbDeviceMonitor(UsbDeviceMonitor):

    def __init__(self, devices: list[UsbDevice] | None = None):
        self.devices = devices or []
        self.error: Exception | None = None

    def get_devices(self) -> list[UsbDevice]:
        if self.error is not None:
            raise self.error

        return self.devices


def create_service(
    devices: list[UsbDevice] | None = None,
) -> tuple[UsbMonitorService, FakeUsbDeviceMonitor]:
    monitor = FakeUsbDeviceMonitor(devices)

    service = UsbMonitorService(
        device_monitor=monitor,
        device_id="USB\\TEST_DEVICE",
    )

    return service, monitor


def test_disconnected_to_connected_emits_connected_event(qapp):
    device = UsbDevice(
        windows_device_id="USB\\TEST_DEVICE",
        name="Test USB Device",
    )

    service, monitor = create_service()

    service.previous_connected = False
    monitor.devices = [device]

    events = []
    service.device_event.connect(events.append)

    service._check_device()

    assert len(events) == 1
    assert events[0].device_id == "USB\\TEST_DEVICE"
    assert events[0].event_type == DeviceEventType.CONNECTED
    assert service.previous_connected is True


def test_connected_to_disconnected_emits_disconnected_event(qapp):
    device = UsbDevice(
        windows_device_id="USB\\TEST_DEVICE",
        name="Test USB Device",
    )

    service, monitor = create_service([device])

    service.previous_connected = True
    monitor.devices = []

    events = []
    service.device_event.connect(events.append)

    service._check_device()

    assert len(events) == 1
    assert events[0].device_id == "USB\\TEST_DEVICE"
    assert events[0].event_type == DeviceEventType.DISCONNECTED
    assert service.previous_connected is False


def test_connected_to_connected_emits_no_event(qapp):
    device = UsbDevice(
        windows_device_id="USB\\TEST_DEVICE",
        name="Test USB Device",
    )

    service, monitor = create_service([device])

    service.previous_connected = True

    events = []
    service.device_event.connect(events.append)

    service._check_device()

    assert events == []
    assert service.previous_connected is True


def test_disconnected_to_disconnected_emits_no_event(qapp):
    service, monitor = create_service()

    service.previous_connected = False

    events = []
    service.device_event.connect(events.append)

    service._check_device()

    assert events == []
    assert service.previous_connected is False


def test_hardware_failure_does_not_emit_event_or_change_state(qapp):
    service, monitor = create_service()

    service.previous_connected = True
    monitor.error = RuntimeError("WMI unavailable")

    events = []
    service.device_event.connect(events.append)

    service._check_device()

    assert events == []
    assert service.previous_connected is True