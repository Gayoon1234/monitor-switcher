import argparse
import math
import platform
import statistics
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def percentile(values: list[float], percentage: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(percentage * len(ordered)) - 1)
    return ordered[index]


def report_measurements(
    label: str,
    measurements: list[tuple[float, int, int]],
    primary_count_name: str,
    secondary_count_name: str | None = None,
) -> None:
    durations = [duration_ms for duration_ms, _, _ in measurements]
    counts = {
        (primary_count, secondary_count)
        for _, primary_count, secondary_count in measurements
    }
    if len(counts) != 1:
        raise RuntimeError(
            f"{label} result counts changed during benchmark: {counts}"
        )

    primary_count, secondary_count = counts.pop()
    count_text = f"{primary_count_name}={primary_count}"
    if secondary_count_name is not None:
        count_text += f", {secondary_count_name}={secondary_count}"
    print(
        f"{label}: {count_text}; "
        f"median={statistics.median(durations):.2f} ms, "
        f"p95={percentile(durations, 0.95):.2f} ms, "
        f"min={min(durations):.2f} ms, max={max(durations):.2f} ms"
    )
    print(
        "  runs (ms): "
        + ", ".join(f"{duration:.2f}" for duration in durations)
    )


def benchmark_usb(warmups: int, iterations: int) -> None:
    from app.hardware.windows_usb import WindowsUsbDeviceMonitor

    monitor = WindowsUsbDeviceMonitor()

    for _ in range(warmups):
        monitor.get_devices()

    measurements = []
    for _ in range(iterations):
        started = perf_counter()
        devices = monitor.get_devices()
        duration_ms = (perf_counter() - started) * 1000
        measurements.append((duration_ms, len(devices), 0))

    report_measurements(
        "USB enumeration",
        measurements,
        "present USB devices",
    )


def benchmark_displays(warmups: int, iterations: int) -> None:
    from app.hardware.windows_monitor import WindowsMonitorController

    started = perf_counter()
    controller = WindowsMonitorController()
    initialization_ms = (perf_counter() - started) * 1000
    print(f"Monitor object initialization: {initialization_ms:.2f} ms")

    for _ in range(warmups):
        controller.get_displays()

    measurements = []
    for _ in range(iterations):
        started = perf_counter()
        displays = controller.get_displays()
        duration_ms = (perf_counter() - started) * 1000
        input_count = sum(len(display.inputs) for display in displays)
        measurements.append((duration_ms, len(displays), input_count))

    report_measurements(
        "Display discovery and input queries",
        measurements,
        "displays",
        "inputs",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark read-only Windows USB and display discovery "
            "without changing configuration or monitor inputs."
        )
    )
    parser.add_argument(
        "--target",
        choices=("usb", "displays", "all"),
        default="all",
        help="hardware path to measure (default: all)",
    )
    parser.add_argument(
        "--warmups",
        type=int,
        default=1,
        help="unreported discovery calls before timing (default: 1)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="timed discovery calls (default: 5)",
    )
    args = parser.parse_args()
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")
    if args.iterations <= 0:
        parser.error("--iterations must be positive")
    if sys.platform != "win32":
        parser.error("hardware discovery benchmark requires Windows")

    print(
        f"Environment: Windows {platform.release()}, "
        f"Python {platform.python_version()}, "
        f"warmups={args.warmups}, iterations={args.iterations}"
    )
    print(
        "Discovery is read-only. Display measurements query monitor "
        "capabilities and current inputs; no inputs are switched."
    )

    if args.target in ("usb", "all"):
        benchmark_usb(args.warmups, args.iterations)
    if args.target in ("displays", "all"):
        benchmark_displays(args.warmups, args.iterations)


if __name__ == "__main__":
    main()
