import argparse
from datetime import datetime, timedelta
import json
import math
import platform
from pathlib import Path
import statistics
import sys
from time import perf_counter

from PySide6.QtCore import (
    QObject,
    QPoint,
    QPointF,
    QTimer,
    Qt,
    Signal,
    qVersion,
)
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QScrollBar,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.models.activity_event import ActivityEvent
from app.models.display import Display
from app.models.usb_device import ConfiguredUsbDevice, UsbDevice
from app.services.config_repository import ConfigRepository
from app.services.theme_service import ThemeService
from app.services.usb_service import UsbService
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


class SnapshotUsbService(QObject):
    devices_changed = Signal()

    def __init__(
        self,
        devices: list[UsbDevice],
        configured_devices: list[ConfiguredUsbDevice],
    ):
        super().__init__()
        self.devices = devices
        self.configured_devices = configured_devices

    def get_devices(self) -> list[UsbDevice]:
        return self.devices

    def get_configured_devices(self) -> list[ConfiguredUsbDevice]:
        return self.configured_devices


class ReadOnlyDisplayService:
    def __init__(self, displays: list[Display]):
        self.displays = displays

    def get_displays(self) -> list[Display]:
        return self.displays

    def switch_input(self, display_id: str, input_id: str) -> None:
        raise RuntimeError("Display switching is disabled in the benchmark.")


class CountingUsbDeviceMonitor:
    def __init__(self, device_monitor):
        self.device_monitor = device_monitor
        self.reset()

    def reset(self) -> None:
        self.poll_durations_ms: list[float] = []
        self.poll_device_counts: list[int] = []

    def get_devices(self) -> list[UsbDevice]:
        start = perf_counter()
        devices = self.device_monitor.get_devices()
        self.poll_durations_ms.append(
            (perf_counter() - start) * 1000
        )
        self.poll_device_counts.append(len(devices))
        return devices


class EventLoopMonitor(QObject):
    def __init__(self, interval_ms: int = 16, parent=None):
        super().__init__(parent)
        self.interval_seconds = interval_ms / 1000
        self.next_deadline = 0.0
        self.delays_ms: list[float] = []
        self.missed_intervals = 0
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._record_delay)

    def start(self) -> None:
        self.next_deadline = perf_counter() + self.interval_seconds
        self.timer.start()

    def record_callback(self, now: float) -> None:
        self.delays_ms.append(
            max(0.0, now - self.next_deadline) * 1000
        )
        self.next_deadline += self.interval_seconds
        while self.next_deadline <= now:
            self.missed_intervals += 1
            self.next_deadline += self.interval_seconds

    def _record_delay(self) -> None:
        self.record_callback(perf_counter())

    def stop(self) -> None:
        self.timer.stop()


class ScrollTarget:
    def __init__(
        self,
        area: QScrollArea,
        axis: str,
        scrollbar: QScrollBar,
    ):
        self.area = area
        self.axis = axis
        self.scrollbar = scrollbar

    @property
    def name(self) -> str:
        area_name = self.area.objectName() or type(self.area).__name__
        return f"{area_name}.{self.axis}"


def create_events(count: int) -> list[ActivityEvent]:
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


def read_activity_days(config_path: Path) -> int | None:
    if not config_path.is_file():
        return 30

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    settings = config.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("Application settings must be a JSON object.")

    days = settings.get("activity_days", config.get("activity_days", 30))
    if days is not None and (
        isinstance(days, bool) or not isinstance(days, int) or days <= 0
    ):
        raise ValueError("Activity history days must be positive or null.")
    return days


def read_usb_monitor_settings(config_path: Path) -> tuple[bool, int]:
    if not config_path.is_file():
        return True, 500

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    settings = config.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("Application settings must be a JSON object.")

    enabled = settings.get("usb_monitor_enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("USB monitor enabled setting must be a boolean.")

    interval_ms = settings.get("usb_monitor_interval_ms", 500)
    if (
        isinstance(interval_ms, bool)
        or not isinstance(interval_ms, int)
        or interval_ms <= 0
    ):
        raise ValueError("USB monitor interval must be a positive integer.")
    return enabled, interval_ms


def load_benchmark_data(
    page_name: str,
    count: int,
    real_data: bool,
):
    load_start = perf_counter()
    activity_history = None
    activity_days = None
    display_service = None
    usb_service = None
    usb_device_monitor = None
    configured_usb_monitor_enabled = None
    usb_monitor_interval_ms = None
    source_counts = {
        "activity_events": None,
        "connected_usb_devices": None,
        "configured_usb_devices": None,
        "displays": None,
    }

    if not real_data:
        if page_name == "activity":
            activity_history = create_events(count)
            source_counts["activity_events"] = len(activity_history)
        else:
            usb_service = FakeUsbService(count)
            source_counts["connected_usb_devices"] = count
            source_counts["configured_usb_devices"] = count
            if page_name == "my-devices":
                display_service = FakeDisplayService()
                source_counts["displays"] = len(
                    display_service.get_displays()
                )
    else:
        if sys.platform != "win32":
            raise RuntimeError("--real-data requires Windows.")

        configured_usb_monitor_enabled, usb_monitor_interval_ms = (
            read_usb_monitor_settings(ROOT / "config.json")
        )
        from app.hardware.windows_usb import WindowsUsbDeviceMonitor

        usb_device_monitor = WindowsUsbDeviceMonitor()
        if page_name == "activity":
            from perf.profile_activity import load_history_snapshot

            activity_days = read_activity_days(ROOT / "config.json")
            activity_history, _, _ = load_history_snapshot(
                ROOT / "activity.db",
                activity_days,
            )
            source_counts["activity_events"] = len(activity_history)
        else:
            repository = ConfigRepository(str(ROOT / "config.json"))
            real_usb_service = UsbService(
                usb_device_monitor,
                repository,
            )
            connected_devices = real_usb_service.get_devices()
            configured_devices = (
                real_usb_service.get_configured_devices()
            )
            usb_service = SnapshotUsbService(
                connected_devices,
                configured_devices,
            )
            source_counts["connected_usb_devices"] = len(
                connected_devices
            )
            source_counts["configured_usb_devices"] = len(
                configured_devices
            )

            if page_name == "my-devices":
                from app.hardware.windows_monitor import (
                    WindowsMonitorController,
                )

                display_controller = WindowsMonitorController()
                displays = display_controller.get_displays()
                display_service = ReadOnlyDisplayService(displays)
                source_counts["displays"] = len(displays)

        if page_name == "activity":
            item_count = len(activity_history)
        elif page_name == "my-devices":
            item_count = len(configured_devices)
        else:
            item_count = len(connected_devices)

        return (
            activity_history,
            activity_days,
            display_service,
            usb_service,
            usb_device_monitor,
            item_count,
            source_counts,
            (perf_counter() - load_start) * 1000,
            configured_usb_monitor_enabled,
            usb_monitor_interval_ms,
        )

    return (
        activity_history,
        activity_days,
        display_service,
        usb_service,
        usb_device_monitor,
        count,
        source_counts,
        (perf_counter() - load_start) * 1000,
        configured_usb_monitor_enabled,
        usb_monitor_interval_ms,
    )


def find_scroll_targets(page: QWidget) -> list[ScrollTarget]:
    targets = []
    for area in page.findChildren(QScrollArea):
        for axis, scrollbar in (
            ("vertical", area.verticalScrollBar()),
            ("horizontal", area.horizontalScrollBar()),
        ):
            if scrollbar.maximum() > scrollbar.minimum():
                targets.append(ScrollTarget(area, axis, scrollbar))
    return targets


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def summarize(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "median_ms": statistics.median(values) if values else None,
        "p95_ms": percentile(values, 0.95),
        "max_ms": max(values) if values else None,
    }


def format_ms(value: float | None) -> str:
    return f"{value:.2f} ms" if value is not None else "n/a"


def send_wheel_event(
    app: QApplication,
    target: ScrollTarget,
    action_index: int,
) -> tuple[float, int]:
    scrollbar = target.scrollbar
    initial_value = scrollbar.value()
    direction = -1 if action_index % 2 == 0 else 1
    delta = (
        QPoint(0, direction * 120)
        if target.axis == "vertical"
        else QPoint(direction * 120, 0)
    )
    viewport = target.area.viewport()
    local_position = QPointF(viewport.rect().center())
    global_position = QPointF(viewport.mapToGlobal(local_position.toPoint()))
    event = QWheelEvent(
        local_position,
        global_position,
        QPoint(0, 0),
        delta,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )

    start = perf_counter()
    QApplication.sendEvent(viewport, event)
    app.processEvents()
    viewport.grab()
    elapsed_ms = (perf_counter() - start) * 1000
    value_delta = abs(scrollbar.value() - initial_value)
    return elapsed_ms, value_delta


def build_page(
    page_name: str,
    activity_history: list[ActivityEvent] | None,
    activity_days: int | None,
    display_service,
    usb_service,
):
    if page_name == "activity":
        return ActivityPage(
            activity_history=activity_history,
            days=activity_days,
        )
    if page_name == "my-devices":
        return MyDevicesPage(display_service, usb_service)
    return FindMyDevicePage(usb_service)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Automatically scroll a synthetic UI page and measure "
            "scroll-response and event-loop timing."
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
        "--real-data",
        action="store_true",
        help=(
            "use local activity data and live, read-only Windows device "
            "discovery instead of synthetic inputs"
        ),
    )
    parser.add_argument(
        "--usb-monitor",
        choices=("config", "enabled", "disabled"),
        default="config",
        help=(
            "USB monitor state for real-data runs: use config.json, force "
            "enabled, or force disabled (default: config)"
        ),
    )
    parser.add_argument(
        "--scroll-events",
        type=int,
        default=200,
        help="number of automated wheel actions (default: 200)",
    )
    parser.add_argument(
        "--interval-ms",
        type=int,
        default=50,
        help="delay between wheel actions (default: 50)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="write the results as one JSON object",
    )
    args = parser.parse_args()
    if not args.real_data and args.items <= 0:
        parser.error("--items must be positive")
    if not args.real_data and args.usb_monitor != "config":
        parser.error("--usb-monitor overrides require --real-data")
    if args.scroll_events <= 0:
        parser.error("--scroll-events must be positive")
    if args.interval_ms <= 0:
        parser.error("--interval-ms must be positive")

    app = QApplication.instance() or QApplication([])
    theme_path = ROOT / "theme.json"
    if theme_path.is_file():
        app.setStyleSheet(ThemeService(str(theme_path)).get_stylesheet())

    screen = app.primaryScreen()
    screen_geometry = screen.geometry() if screen is not None else None
    window = QMainWindow()
    window.resize(1000, 700)
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.addWidget(
        QLabel(
            "Automated "
            + ("real-data" if args.real_data else "synthetic")
            + " scroll benchmark"
        )
    )

    (
        activity_history,
        activity_days,
        display_service,
        usb_service,
        usb_device_monitor,
        item_count,
        source_counts,
        data_loading_ms,
        configured_usb_monitor_enabled,
        usb_monitor_interval_ms,
    ) = load_benchmark_data(args.page, args.items, args.real_data)
    if args.real_data:
        if args.usb_monitor == "config":
            usb_monitor_enabled = configured_usb_monitor_enabled
        else:
            usb_monitor_enabled = args.usb_monitor == "enabled"
    else:
        usb_monitor_enabled = False
    setup_start = perf_counter()
    page = build_page(
        args.page,
        activity_history,
        activity_days,
        display_service,
        usb_service,
    )
    for button in page.findChildren(QPushButton):
        button.setEnabled(False)
    for selector in page.findChildren(QComboBox):
        selector.setEnabled(False)
    setup_ms = (perf_counter() - setup_start) * 1000

    layout.addWidget(page, 1)
    window.setCentralWidget(content)
    window.show()
    paint_start = perf_counter()
    app.processEvents()
    window.grab()
    initial_paint_ms = (perf_counter() - paint_start) * 1000

    targets = find_scroll_targets(page)

    monitor = EventLoopMonitor(parent=window)
    usb_monitor_service = None
    usb_monitor_proxy = None
    usb_monitor_startup_ms = 0.0
    if args.real_data and usb_monitor_enabled:
        from app.services.usb_monitor_service import UsbMonitorService

        usb_monitor_proxy = CountingUsbDeviceMonitor(usb_device_monitor)
        usb_monitor_service = UsbMonitorService(usb_monitor_proxy)
        usb_monitor_proxy.reset()
        start = perf_counter()
        usb_monitor_service.start(usb_monitor_interval_ms)
        usb_monitor_startup_ms = (perf_counter() - start) * 1000

    action_times_ms = []
    changed_actions = 0
    action_index = 0
    action_timer = QTimer(window)
    action_timer.setSingleShot(True)
    finish_timer = QTimer(window)
    finish_timer.setSingleShot(True)

    def finish() -> None:
        monitor.stop()
        if usb_monitor_service is not None:
            usb_monitor_service.stop()
        window.close()

    def perform_scroll() -> None:
        nonlocal action_index, changed_actions
        target = targets[action_index % len(targets)]
        elapsed_ms, value_delta = send_wheel_event(
            app,
            target,
            action_index,
        )
        action_times_ms.append(elapsed_ms)
        changed_actions += value_delta > 0
        action_index += 1

        if action_index == args.scroll_events:
            finish()
        else:
            action_timer.start(args.interval_ms)

    if targets:
        monitor.start()
        action_timer.timeout.connect(perform_scroll)
        action_timer.start(0)
        app.exec()
    elif args.real_data:
        monitor.start()
        finish_timer.timeout.connect(finish)
        finish_timer.start(args.scroll_events * args.interval_ms)
        app.exec()
    else:
        window.close()

    usb_poll_times = (
        usb_monitor_proxy.poll_durations_ms
        if usb_monitor_proxy is not None
        else []
    )
    usb_poll_device_counts = (
        usb_monitor_proxy.poll_device_counts
        if usb_monitor_proxy is not None
        else []
    )

    result = {
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "qt": qVersion(),
            "screen_size": (
                [screen_geometry.width(), screen_geometry.height()]
                if screen_geometry is not None
                else None
            ),
        },
        "page": args.page,
        "data_source": "real" if args.real_data else "synthetic",
        "items": item_count,
        "source_counts": source_counts,
        "activity_days": activity_days,
        "data_loading_ms": data_loading_ms,
        "usb_monitor_configured_enabled": configured_usb_monitor_enabled,
        "usb_monitor_enabled": usb_monitor_enabled,
        "usb_monitor_interval_ms": (
            usb_monitor_interval_ms if usb_monitor_enabled else None
        ),
        "usb_monitor_startup_ms": usb_monitor_startup_ms,
        "usb_monitor_poll_count": len(usb_poll_times),
        "usb_monitor_poll_device_counts": usb_poll_device_counts,
        "usb_monitor_poll_duration_ms": summarize(usb_poll_times),
        "scroll_targets": [target.name for target in targets],
        "requested_scroll_events": args.scroll_events,
        "scroll_interval_ms": args.interval_ms,
        "completed_scroll_events": len(action_times_ms),
        "scroll_events_that_moved": changed_actions,
        "widget_construction_ms": setup_ms,
        "initial_paint_and_snapshot_ms": initial_paint_ms,
        "wheel_to_processed_snapshot": summarize(action_times_ms),
        "event_loop_timer_interval_ms": 16,
        "event_loop_timer_samples": summarize(monitor.delays_ms),
        "event_loop_missed_intervals": monitor.missed_intervals,
        "event_loop_callbacks_over_16_67ms": sum(
            delay >= 16.67 for delay in monitor.delays_ms
        ),
    }

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(
            f"Page: {result['page']} ({result['items']} items; "
            f"{result['data_source']} data)"
        )
        print(f"Data loading: {result['data_loading_ms']:.2f} ms")
        print(
            "Scrollable targets: "
            + (", ".join(result["scroll_targets"]) or "none")
        )
        print(
            "Wheel actions: "
            f"{result['completed_scroll_events']}/"
            f"{result['requested_scroll_events']} completed; "
            f"{result['scroll_events_that_moved']} moved the scrollbar"
        )
        print(
            f"Widget construction: {result['widget_construction_ms']:.2f} ms; "
            "initial paint/snapshot: "
            f"{result['initial_paint_and_snapshot_ms']:.2f} ms"
        )
        response = result["wheel_to_processed_snapshot"]
        timer = result["event_loop_timer_samples"]
        print(
            "Wheel-to-processed-snapshot latency: "
            f"median {format_ms(response['median_ms'])}, "
            f"p95 {format_ms(response['p95_ms'])}, "
            f"max {format_ms(response['max_ms'])}"
        )
        print(
            "16 ms event-loop timer lateness: "
            f"median {format_ms(timer['median_ms'])}, "
            f"p95 {format_ms(timer['p95_ms'])}, "
            f"max {format_ms(timer['max_ms'])}; "
            f"{result['event_loop_missed_intervals']} missed intervals; "
            f"{result['event_loop_callbacks_over_16_67ms']} callbacks "
            "at least 16.67 ms late"
        )
        print(
            "These are Qt event-loop and QWidget snapshot timings, "
            "not physical display frame times."
        )


if __name__ == "__main__":
    main()
