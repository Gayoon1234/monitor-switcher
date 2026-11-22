import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys


SINGLE_RUN_SCRIPT = Path(__file__).with_name("measure_ui_responsiveness.py")
PAGES = ("activity", "my-devices", "find-my-device")


def summarize_runs(records: list[dict]) -> dict:
    return {
        "page": records[0]["page"],
        "items": records[0]["items"],
        "runs": len(records),
        "construction_median_ms": statistics.median(
            record["widget_construction_ms"] for record in records
        ),
        "initial_median_ms": statistics.median(
            record["initial_paint_and_snapshot_ms"]
            for record in records
        ),
        "wheel_median_ms": statistics.median(
            record["wheel_to_processed_snapshot"]["median_ms"]
            for record in records
        ),
        "wheel_p95_median_ms": statistics.median(
            record["wheel_to_processed_snapshot"]["p95_ms"]
            for record in records
        ),
        "wheel_max_worst_ms": max(
            record["wheel_to_processed_snapshot"]["max_ms"]
            for record in records
        ),
        "timer_max_worst_ms": max(
            record["event_loop_timer_samples"]["max_ms"]
            for record in records
        ),
        "missed_intervals_total": sum(
            record["event_loop_missed_intervals"] for record in records
        ),
    }


def run_scenario(
    page: str,
    items: int,
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
            "--items",
            str(items),
            "--scroll-events",
            str(scroll_events),
            "--interval-ms",
            str(interval_ms),
            "--json",
        ]
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
        if (
            record["completed_scroll_events"] != scroll_events
            or record["scroll_events_that_moved"] != scroll_events
        ):
            raise RuntimeError(
                f"Benchmark did not complete all scroll actions for "
                f"{page}, {items} items, run {run}: "
                f"{record['completed_scroll_events']}/"
                f"{scroll_events} actions completed, "
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
        for items in args.items:
            records = run_scenario(
                page,
                items,
                args.repeats,
                args.scroll_events,
                args.interval_ms,
            )
            all_records.extend(records)
            summaries.append(summarize_runs(records))

    result = {
        "settings": {
            "pages": args.pages,
            "items": args.items,
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
        print(
            "Median columns are medians across runs; max columns are worst "
            "across runs; missed intervals are totals."
        )
        print(
            "Page,Items,Construction median ms,Initial median ms,"
            "Wheel median ms,Wheel p95 median ms,Wheel max worst ms,"
            "Timer max worst ms,Missed intervals total"
        )
        for summary in summaries:
            print(
                f"{summary['page']},{summary['items']},"
                f"{summary['construction_median_ms']:.2f},"
                f"{summary['initial_median_ms']:.2f},"
                f"{summary['wheel_median_ms']:.2f},"
                f"{summary['wheel_p95_median_ms']:.2f},"
                f"{summary['wheel_max_worst_ms']:.2f},"
                f"{summary['timer_max_worst_ms']:.2f},"
                f"{summary['missed_intervals_total']}"
            )


if __name__ == "__main__":
    main()
