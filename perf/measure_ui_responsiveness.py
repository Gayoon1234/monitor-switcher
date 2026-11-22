import argparse
from datetime import datetime, timedelta
from pathlib import Path
import statistics
import sys
from time import perf_counter

from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.models.activity_event import ActivityEvent
from app.models.display import Display
from app.models.usb_device import ConfiguredUsbDevice, UsbDevice
from app.services.theme_service import ThemeService
from app.ui.pages.activity import ActivityPage
from app.ui.pages.find_my_device import FindMyDevicePage
from app.ui.pages.my_devices import MyDevicesPage


class FakeDisplayService:
    def get_displays(self) -> list[Display]:
        return [
            Display(
                id=f"display-{index + 1:03d}",
                name=f"Test display {index + 1}",
                windows_device_id=f"DISPLAY\\TEST{index + 1}",
                inputs=[],
            )
            for index in range(2)
        ]

    def switch_input(self, display_id: str, input_id: str) -> None:
        return None


class FakeUsbService(QObject):
    devices_changed = Signal()

    def __init__(self, count: int):
        super().__init__()
        self.devices = [
            UsbDevice(
                windows_device_id=f"USB\\TEST{index + 1:04d}",
                name=f"Test USB device {index + 1}",
            )
            for index in range(count)
        ]
        self.configured_devices = [
            ConfiguredUsbDevice(
                id=f"configured-{index + 1:04d}",
                windows_device_id=device.windows_device_id,
                nickname=f"Test device {index + 1}",
            )
            for index, device in enumerate(self.devices)
        ]

    def get_devices(self) -> list[UsbDevice]:
        return self.devices

    def get_configured_devices(self) -> list[ConfiguredUsbDevice]:
        return self.configured_devices


class EventLoopMonitor(QObject):
    def __init__(self, interval_ms: int = 16, parent=None):
        super().__init__(parent)
        self.interval_seconds = interval_ms / 1000
        self.next_deadline = 0.0
        self.delays_ms: list[float] = []
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._record_delay)

    def start(self) -> None:
        self.next_deadline = perf_counter() + self.interval_seconds
        self.timer.start()

    def _record_delay(self) -> None:
        now = perf_counter()
        self.delays_ms.append(
            max(0.0, now - self.next_deadline) * 1000
        )
        self.next_deadline += self.interval_seconds
        while self.next_deadline <= now:
            self.next_deadline += self.interval_seconds

    def stop(self) -> None:
        self.timer.stop()


def create_events(count: int):
    now = datetime.now()
    return [
        ActivityEvent(
            timestamp=now - timedelta(minutes=count - index),
            event_type="device_event" if index % 2 == 0 else "action",
            message=f"Synthetic scroll-test event {index + 1}",
            success=index % 5 != 0,
        )
        for index in range(count)
    ]


def report_delays(delays_ms: list[float]) -> None:
    if not delays_ms:
        print("No timer samples were collected.")
        return

    ordered = sorted(delays_ms)
    p95_index = min(int(len(ordered) * 0.95), len(ordered) - 1)
    print(
        f"UI event-loop timer lateness: {len(ordered)} samples; "
        f"median {statistics.median(ordered):.2f} ms, "
        f"p95 {ordered[p95_index]:.2f} ms, "
        f"max {max(ordered):.2f} ms"
    )
    print(
        "This is event-loop responsiveness, not a direct measurement "
        "of rendered frames per second."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Open a synthetic Activity or device page and measure "
            "UI event-loop delays while scrolling."
        )
    )
    parser.add_argument(
        "--page",
        choices=("activity", "my-devices", "find-my-device"),
        default="activity",
    )
    parser.add_argument(
        "--items",
        type=int,
        default=100,
        help="synthetic event/device count (default: 100)",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=15,
        help="measurement duration (default: 15)",
    )
    args = parser.parse_args()
    if args.items <= 0:
        parser.error("--items must be positive")
    if args.seconds <= 0:
        parser.error("--seconds must be positive")

    app = QApplication.instance() or QApplication([])
    theme_path = ROOT / "theme.json"
    if theme_path.is_file():
        app.setStyleSheet(ThemeService(str(theme_path)).get_stylesheet())

    usb_service = FakeUsbService(args.items)
    window = QMainWindow()
    window.resize(1000, 700)
    monitor = EventLoopMonitor(parent=window)

    content = QWidget()
    layout = QVBoxLayout(content)
    instruction = QLabel(
        f"Scroll the {args.page} page during the next {args.seconds} seconds. "
        "Close this window to stop early."
    )
    layout.addWidget(instruction)

    setup_start = perf_counter()
    if args.page == "activity":
        page = ActivityPage(activity_history=create_events(args.items), days=None)
    elif args.page == "my-devices":
        page = MyDevicesPage(FakeDisplayService(), usb_service)
    else:
        page = FindMyDevicePage(usb_service)
    setup_ms = (perf_counter() - setup_start) * 1000
    layout.addWidget(page, 1)
    window.setCentralWidget(content)

    print(f"Widget construction: {setup_ms:.2f} ms")
    window.show()
    display_start = perf_counter()
    app.processEvents()
    display_ms = (perf_counter() - display_start) * 1000
    print(f"Initial layout/paint processing: {display_ms:.2f} ms")
    monitor.start()

    def finish() -> None:
        monitor.stop()
        report_delays(monitor.delays_ms)

    app.aboutToQuit.connect(finish)
    QTimer.singleShot(args.seconds * 1000, window.close)
    app.exec()


if __name__ == "__main__":
    main()
