import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys


SINGLE_RUN_SCRIPT = Path(__file__).with_name("measure_ui_responsiveness.py")
PAGES = ("activity", "my-devices", "find-my-device")


def summarize_runs(records: list[dict]) -> dict:
    if len({record["items"] for record in records}) != 1:
        raise RuntimeError("Item counts changed between benchmark repeats.")
    if len({json.dumps(record["source_counts"], sort_keys=True) for record in records}) != 1:
        raise RuntimeError("Real data counts changed between benchmark repeats.")

    wheel_medians = [
        record["wheel_to_processed_snapshot"]["median_ms"]
        for record in records
    ]
    wheel_p95s = [
        record["wheel_to_processed_snapshot"]["p95_ms"]
        for record in records
    ]
    wheel_maxima = [
        record["wheel_to_processed_snapshot"]["max_ms"]
        for record in records
    ]
    timer_maxima = [
        record["event_loop_timer_samples"]["max_ms"]
        for record in records
    ]
    return {
        "page": records[0]["page"],
        "items": records[0]["items"],
        "runs": len(records),
        "data_source": records[0]["data_source"],
        "source_counts": records[0]["source_counts"],
        "data_loading_median_ms": statistics.median(
            record["data_loading_ms"] for record in records
        ),
        "construction_median_ms": statistics.median(
            record["widget_construction_ms"] for record in records
        ),
        "initial_median_ms": statistics.median(
            record["initial_paint_and_snapshot_ms"]
            for record in records
        ),
        "wheel_median_ms": (
            statistics.median(wheel_medians)
            if all(value is not None for value in wheel_medians)
            else None
        ),
        "wheel_p95_median_ms": (
            statistics.median(wheel_p95s)
            if all(value is not None for value in wheel_p95s)
            else None
        ),
        "wheel_max_worst_ms": (
            max(wheel_maxima)
            if all(value is not None for value in wheel_maxima)
            else None
        ),
        "timer_max_worst_ms": (
            max(timer_maxima)
            if all(value is not None for value in timer_maxima)
            else None
        ),
        "missed_intervals_total": sum(
            record["event_loop_missed_intervals"] for record in records
        ),
    }


def run_scenario(
    page: str,
    items: int | None,
    real_data: bool,
    repeats: int,
    scroll_events: int,
    interval_ms: int,
) -> list[dict]:
    records = []
    for run in range(1, repeats + 1):
        print(
            f"Running {page}, {items} items, run {run}/{repeats}",
            file=sys.stderr,
            flush=True,
        )
        command = [
            sys.executable,
            str(SINGLE_RUN_SCRIPT),
            "--page",
            page,
            "--scroll-events",
            str(scroll_events),
            "--interval-ms",
            str(interval_ms),
            "--json",
        ]
        if real_data:
            command.append("--real-data")
        else:
            command.extend(("--items", str(items)))
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            raise RuntimeError(
                f"Benchmark failed for {page}, {items} items, run {run}.\n"
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )

        record = json.loads(completed.stdout)
        has_scroll_target = bool(record["scroll_targets"])
        expected_actions = scroll_events if has_scroll_target else 0
        if (
            record["completed_scroll_events"] != expected_actions
            or record["scroll_events_that_moved"] != expected_actions
        ):
            raise RuntimeError(
                f"Benchmark did not complete all scroll actions for "
                f"{page}, {items} items, run {run}: "
                f"{record['completed_scroll_events']}/"
                f"{expected_actions} actions completed, "
                f"{record['scroll_events_that_moved']} moved the scrollbar."
            )
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a sequential UI scroll benchmark matrix and aggregate "
            "repeat results."
        )
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        choices=PAGES,
        default=PAGES,
        help="pages to benchmark (default: all three)",
    )
    parser.add_argument(
        "--items",
        nargs="+",
        type=int,
        default=(50, 500, 5000),
        help="synthetic item counts (default: 50 500 5000)",
    )
    parser.add_argument(
        "--real-data",
        action="store_true",
        help="use real local activity/device data instead of synthetic tiers",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="runs per page/item combination (default: 3)",
    )
    parser.add_argument(
        "--scroll-events",
        type=int,
        default=20,
        help="wheel actions per run (default: 20)",
    )
    parser.add_argument(
        "--interval-ms",
        type=int,
        default=30,
        help="delay between wheel actions (default: 30)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="write settings, raw runs, and summaries as JSON",
    )
    args = parser.parse_args()
    if args.repeats <= 0:
        parser.error("--repeats must be positive")
    if args.scroll_events <= 0:
        parser.error("--scroll-events must be positive")
    if args.interval_ms <= 0:
        parser.error("--interval-ms must be positive")
    if any(items <= 0 for items in args.items):
        parser.error("all --items values must be positive")

    all_records = []
    summaries = []
    for page in args.pages:
        item_counts = (None,) if args.real_data else args.items
        for items in item_counts:
            records = run_scenario(
                page,
                items,
                args.real_data,
                args.repeats,
                args.scroll_events,
                args.interval_ms,
            )
            all_records.extend(records)
            summaries.append(summarize_runs(records))

    result = {
        "settings": {
            "pages": args.pages,
            "items": None if args.real_data else args.items,
            "real_data": args.real_data,
            "repeats": args.repeats,
            "scroll_events": args.scroll_events,
            "interval_ms": args.interval_ms,
        },
        "environment": all_records[0]["environment"],
        "summary": summaries,
        "runs": all_records,
    }
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("Median columns aggregate runs; max columns are worst values.")
        print(
            "Page,Data,Items,Data load median ms,Construction median ms,"
            "Initial median ms,Wheel median ms,Wheel p95 median ms,"
            "Wheel max worst ms,Timer max worst ms,Missed intervals total"
        )
        for summary in summaries:
            def format_ms(value):
                return "n/a" if value is None else f"{value:.2f}"

            print(
                f"{summary['page']},{summary['data_source']},"
                f"{summary['items']},"
                f"{summary['data_loading_median_ms']:.2f},"
                f"{summary['construction_median_ms']:.2f},"
                f"{summary['initial_median_ms']:.2f},"
                f"{format_ms(summary['wheel_median_ms'])},"
                f"{format_ms(summary['wheel_p95_median_ms'])},"
                f"{format_ms(summary['wheel_max_worst_ms'])},"
                f"{format_ms(summary['timer_max_worst_ms'])},"
                f"{summary['missed_intervals_total']}"
            )


if __name__ == "__main__":
    main()
