import json

import pytest

from app.models.usb_device import UsbDevice
from perf.measure_ui_responsiveness import (
    CountingUsbDeviceMonitor,
    EventLoopMonitor,
    read_usb_monitor_settings,
    summarize,
)


def test_event_loop_monitor_counts_deadlines_missed_during_a_stall():
    monitor = EventLoopMonitor(interval_ms=16)
    monitor.next_deadline = 1.0

    monitor.record_callback(1.05)

    assert monitor.delays_ms == pytest.approx([50.0])
    assert monitor.missed_intervals == 3


def test_summarize_uses_nearest_rank_p95():
    result = summarize([1.0, 2.0, 3.0, 4.0, 5.0])

    assert result == {
        "count": 5,
        "median_ms": 3.0,
        "p95_ms": 5.0,
        "max_ms": 5.0,
    }


def test_read_usb_monitor_settings_uses_default_values(tmp_path):
    settings_path = tmp_path / "config.json"
    settings_path.write_text("{}", encoding="utf-8")

    assert read_usb_monitor_settings(settings_path) == (True, 500)


def test_read_usb_monitor_settings_reads_configured_values(tmp_path):
    settings_path = tmp_path / "config.json"
    settings_path.write_text(
        json.dumps(
            {
                "settings": {
                    "usb_monitor_enabled": False,
                    "usb_monitor_interval_ms": 750,
                }
            }
        ),
        encoding="utf-8",
    )

    assert read_usb_monitor_settings(settings_path) == (False, 750)


def test_counting_usb_monitor_records_calls():
    class DeviceMonitor:
        def get_devices(self):
            return [
                UsbDevice(windows_device_id="USB\\TEST", name="Test device")
            ]

    monitor = CountingUsbDeviceMonitor(DeviceMonitor())

    assert len(monitor.get_devices()) == 1
    assert monitor.poll_device_counts == [1]
    assert monitor.poll_durations_ms[0] >= 0
