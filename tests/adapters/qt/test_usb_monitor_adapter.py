import time
from threading import Event

from PySide6.QtCore import QThreadPool, QTimer

from app.adapters.qt.usb_monitor_adapter import QtUsbMonitorAdapter
from app.hardware.usb import UsbDeviceMonitor
from app.models.device_event import DeviceEventType
from app.models.usb_device import UsbDevice
from app.services.usb_monitor_service import UsbMonitorService


class FakeUsbDeviceMonitor(UsbDeviceMonitor):

    def __init__(self, devices=None):
        self.devices = devices or []
        self.started = Event()
        self.finished = Event()
        self.release = Event()
        self.block = False

    def get_devices(self) -> list[UsbDevice]:
        self.started.set()
        if self.block:
            self.release.wait(timeout=2)
        self.finished.set()
        return self.devices


def wait_until(qapp, condition) -> None:
    deadline = time.monotonic() + 2
    while not condition() and time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.001)
    qapp.processEvents()

    assert condition()


def test_usb_enumeration_does_not_block_the_qt_thread(qapp):
    monitor = FakeUsbDeviceMonitor()
    monitor.block = True
    service = UsbMonitorService("USB\\TEST_DEVICE")
    adapter = QtUsbMonitorAdapter(monitor, service)
    ui_timer_fired = []
    ui_timer = QTimer()
    ui_timer.setSingleShot(True)
    ui_timer.timeout.connect(lambda: ui_timer_fired.append(True))

    try:
        adapter.start(500)
        assert monitor.started.wait(timeout=0.5)

        ui_timer.start(0)
        qapp.processEvents()

        assert ui_timer_fired == [True]
        assert not monitor.finished.is_set()
    finally:
        monitor.release.set()
        adapter.stop()
        assert monitor.finished.wait(timeout=2)
        QThreadPool.globalInstance().waitForDone(2_000)
        qapp.processEvents()


def test_adapter_establishes_baseline_then_forwards_device_changes(qapp):
    device = UsbDevice("USB\\TEST_DEVICE", "Test device")
    monitor = FakeUsbDeviceMonitor()
    service = UsbMonitorService("USB\\TEST_DEVICE")
    adapter = QtUsbMonitorAdapter(monitor, service)
    events = []
    service.device_events.subscribe(events.append)

    try:
        adapter.start(500)
        wait_until(qapp, lambda: service._baseline_pending is False)
        assert service.previous_connected is False
        assert events == []

        monitor.devices = [device]
        adapter._check_device()
        wait_until(qapp, lambda: len(events) == 1)

        assert events[0].device_id == device.windows_device_id
        assert events[0].event_type == DeviceEventType.CONNECTED
    finally:
        adapter.stop()
        QThreadPool.globalInstance().waitForDone(2_000)
        qapp.processEvents()


def test_adapter_updates_polling_interval_while_running(qapp):
    adapter = QtUsbMonitorAdapter(
        FakeUsbDeviceMonitor(),
        UsbMonitorService("USB\\TEST_DEVICE"),
    )

    try:
        adapter.start(500)
        assert adapter.timer.interval() == 500
        assert adapter.timer.isActive()

        adapter.set_interval(1250)

        assert adapter.timer.interval() == 1250
        assert adapter.timer.isActive()
    finally:
        adapter.stop()
        QThreadPool.globalInstance().waitForDone(2_000)
        qapp.processEvents()
