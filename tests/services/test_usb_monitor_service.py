import time
from threading import Event

from PySide6.QtCore import QTimer

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


class BlockingUsbDeviceMonitor(FakeUsbDeviceMonitor):

    def __init__(self):
        super().__init__()
        self.started = Event()
        self.finished = Event()
        self.release = Event()

    def get_devices(self) -> list[UsbDevice]:
        self.started.set()
        self.release.wait(timeout=1)
        self.finished.set()
        return super().get_devices()


def create_service(
    devices: list[UsbDevice] | None = None,
) -> tuple[UsbMonitorService, FakeUsbDeviceMonitor]:
    monitor = FakeUsbDeviceMonitor(devices)

    service = UsbMonitorService(
        device_monitor=monitor,
        device_id="USB\\TEST_DEVICE",
    )

    return service, monitor


def wait_for_poll(service: UsbMonitorService, qapp) -> None:
    deadline = time.monotonic() + 2
    while service._poller._poll_in_flight and time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.001)
    qapp.processEvents()

    assert not service._poller._poll_in_flight


def poll_once(service: UsbMonitorService, qapp) -> None:
    service._poller._monitoring = True
    service._poller._check_device()
    wait_for_poll(service, qapp)
    service._poller._monitoring = False


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

    poll_once(service, qapp)

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

    poll_once(service, qapp)

    assert len(events) == 1
    assert events[0].device_id == "USB\\TEST_DEVICE"
    assert events[0].event_type == DeviceEventType.DISCONNECTED
    assert service.previous_connected is False


def test_connected_to_connected_emits_no_event(qapp):
    device = UsbDevice(
        windows_device_id="USB\\TEST_DEVICE",
        name="Test USB Device",
    )

    service, _ = create_service([device])

    service.previous_connected = True

    events = []
    service.device_event.connect(events.append)

    poll_once(service, qapp)

    assert events == []
    assert service.previous_connected is True


def test_disconnected_to_disconnected_emits_no_event(qapp):
    service, _ = create_service()

    service.previous_connected = False

    events = []
    service.device_event.connect(events.append)

    poll_once(service, qapp)

    assert events == []
    assert service.previous_connected is False


def test_all_devices_are_monitored(qapp):
    device_1 = UsbDevice(
        windows_device_id="USB\\DEVICE_1",
        name="Device 1",
    )
    device_2 = UsbDevice(
        windows_device_id="USB\\DEVICE_2",
        name="Device 2",
    )

    monitor = FakeUsbDeviceMonitor([device_1])
    service = UsbMonitorService(device_monitor=monitor)
    service.previous_connected = {device_1.windows_device_id}

    monitor.devices = [device_1, device_2]

    events = []
    service.device_event.connect(events.append)

    poll_once(service, qapp)

    assert len(events) == 1
    assert events[0].device_id == "USB\\DEVICE_2"
    assert events[0].event_type == DeviceEventType.CONNECTED
    assert service.previous_connected == {"USB\\DEVICE_1", "USB\\DEVICE_2"}


def test_hardware_failure_does_not_emit_event_or_change_state(qapp):
    service, monitor = create_service()

    service.previous_connected = True
    monitor.error = RuntimeError("WMI unavailable")

    events = []
    service.device_event.connect(events.append)

    poll_once(service, qapp)

    assert events == []
    assert service.previous_connected is True


def test_polling_interval_can_be_changed_while_running(qapp):
    service, _ = create_service()
    service.start(500)

    assert service._poller.timer.interval() == 500
    assert service._poller.timer.isActive()

    service.set_interval(1250)

    assert service._poller.timer.interval() == 1250
    assert service._poller.timer.isActive()

    service.stop()

    assert not service._poller.timer.isActive()
    wait_for_poll(service, qapp)


def test_start_establishes_initial_state_without_emitting_events(qapp):
    device = UsbDevice(
        windows_device_id="USB\\TEST_DEVICE",
        name="Test USB Device",
    )
    service, _ = create_service([device])
    events = []
    service.device_event.connect(events.append)

    service.start(500)
    wait_for_poll(service, qapp)
    service.stop()

    assert service.previous_connected is True
    assert events == []


def test_usb_enumeration_does_not_block_the_ui_thread(qapp):
    monitor = BlockingUsbDeviceMonitor()
    service = UsbMonitorService(
        device_monitor=monitor,
        device_id="USB\\TEST_DEVICE",
    )
    ui_timer_fired = []
    ui_timer = QTimer()
    ui_timer.setSingleShot(True)
    ui_timer.timeout.connect(lambda: ui_timer_fired.append(True))

    try:
        service.start(500)
        assert monitor.started.wait(timeout=0.5)

        ui_timer.start(0)
        qapp.processEvents()

        assert ui_timer_fired == [True]
        assert not monitor.finished.is_set()
    finally:
        monitor.release.set()
        service.stop()
        wait_for_poll(service, qapp)