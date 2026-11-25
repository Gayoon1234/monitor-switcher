import argparse
import cProfile
from datetime import datetime, timedelta
from pathlib import Path
import pstats
import sqlite3
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from statistics import median

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.models.activity_event import ActivityEvent
from app.services.activity_repository import ActivityRepository
from app.services.theme_service import ThemeService
from app.ui.pages.activity import ActivityPage


def parse_days(value: str) -> int | None:
    if value.lower() == "all":
        return None

    days = int(value)
    if days <= 0:
        raise argparse.ArgumentTypeError("days must be positive or 'all'")
    return days


def load_history_snapshot(
    database_path: Path,
    days: int | None,
) -> tuple[list[ActivityEvent], float, float]:
    if not database_path.is_file():
        raise FileNotFoundError(f"Activity database not found: {database_path}")

    with TemporaryDirectory(prefix="monitor-switcher-perf-") as directory:
        snapshot_path = Path(directory) / "activity.db"
        source_uri = f"{database_path.resolve().as_uri()}?mode=ro"
        source = sqlite3.connect(source_uri, uri=True)
        snapshot = sqlite3.connect(snapshot_path)
        try:
            snapshot_start = perf_counter()
            source.backup(snapshot)
            snapshot_ms = (perf_counter() - snapshot_start) * 1000
        finally:
            snapshot.close()
            source.close()

        repository = ActivityRepository(snapshot_path)
        try:
            query_start = perf_counter()
            events = repository.load(days)
            query_ms = (perf_counter() - query_start) * 1000
        finally:
            repository.close()
        return events, snapshot_ms, query_ms


def create_synthetic_history(count: int) -> list[ActivityEvent]:
    now = datetime.now()
    return [
        ActivityEvent(
            timestamp=now - timedelta(minutes=count - index),
            event_type="device_event" if index % 2 == 0 else "action",
            message=f"Synthetic performance test event {index + 1}",
            success=index % 5 != 0,
        )
        for index in range(count)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Measure Activity history loading and rendering without "
            "modifying the source database."
        )
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=ROOT / "activity.db",
        help="SQLite activity database (default: activity.db in the repo root)",
    )
    parser.add_argument(
        "--days",
        type=parse_days,
        default=30,
        help="history window in days, or 'all' (default: 30)",
    )
    parser.add_argument(
        "--synthetic-events",
        type=int,
        help="use this many generated events for rendering instead of database events",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="number of render measurements (default: 5)",
    )
    args = parser.parse_args()

    if args.repeat <= 0:
        parser.error("--repeat must be positive")
    if args.synthetic_events is not None and args.synthetic_events < 0:
        parser.error("--synthetic-events cannot be negative")

    database_events, snapshot_ms, query_ms = load_history_snapshot(
        args.database,
        args.days,
    )
    print(
        f"Read-only database snapshot: {snapshot_ms:.2f} ms; "
        f"history query + decode: {len(database_events)} events in "
        f"{query_ms:.2f} ms (source left unchanged)"
    )

    if args.synthetic_events is None:
        events = database_events
        source_description = "database history"
    else:
        events = create_synthetic_history(args.synthetic_events)
        source_description = "synthetic history"

    app = QApplication.instance() or QApplication([])
    theme_path = ROOT / "theme.json"
    if theme_path.is_file():
        app.setStyleSheet(ThemeService(str(theme_path)).get_stylesheet())

    page = ActivityPage(days=args.days)
    page.resize(1000, 700)
    page.show()
    app.processEvents()

    render_times = []
    for _ in range(args.repeat):
        start = perf_counter()
        page.set_events(events)
        app.processEvents()
        render_times.append((perf_counter() - start) * 1000)

    print(
        f"Activity render: {len(events)} total events, "
        f"{page.activity_container.count()} visible event widgets; "
        f"median {median(render_times):.2f} ms, "
        f"min {min(render_times):.2f} ms, max {max(render_times):.2f} ms "
        f"over {args.repeat} runs ({source_description})"
    )

    profiler = cProfile.Profile()
    profiler.enable()
    page.set_events(events)
    app.processEvents()
    profiler.disable()
    print("\nTop Python render calls by cumulative time:")
    pstats.Stats(profiler).strip_dirs().sort_stats("cumulative").print_stats(15)

    page.close()
    app.processEvents()


if __name__ == "__main__":
    main()
