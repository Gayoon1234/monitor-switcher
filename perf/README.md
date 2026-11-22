# UI performance probes

These scripts provide repeatable measurements without changing application
behavior or writing to the real activity database.

From the repository root:

```powershell
python perf\profile_activity.py --database activity.db --days 30
python perf\profile_activity.py --synthetic-events 5000 --days all
python perf\measure_ui_responsiveness.py --page activity --items 500
python perf\measure_ui_responsiveness.py --page my-devices --items 50
python perf\measure_ui_responsiveness.py --page find-my-device --items 50
python perf\run_ui_benchmark_matrix.py
```

`profile_activity.py` reports database load time, median Activity rendering
time, and the most expensive Python calls in one render. The database is copied
using SQLite's read-only backup API before it is opened by the repository.

`measure_ui_responsiveness.py` opens a test window populated with synthetic
events or devices and automatically sends wheel events to its scrollable
areas. It reports widget construction time, initial paint/snapshot processing
time, wheel-to-processed-snapshot latency (median, p95, and maximum), and
16 ms event-loop timer lateness including missed timer intervals. Results can
be emitted as JSON for repeatable comparison:

```powershell
python perf\measure_ui_responsiveness.py --page find-my-device --items 50 --scroll-events 200 --json
```

The script captures a QWidget snapshot after each wheel event. These timings
measure Qt event handling and widget rendering in-process, not physical display
frame presentation or monitor refresh. Use the same page, item count, event
count, and interval when comparing runs; compare multiple-run medians. Synthetic
device counts should be kept realistic when comparing against normal use.

For useful comparisons, run each scenario several times on the same machine and
compare medians. A high render/setup time points toward Python-side widget
construction or layout work; event-loop lateness while scrolling indicates
that the UI thread is missing scheduled timer intervals. Neither measurement
alone proves the cause, and Qt's native painting time is not fully represented
in Python's `cProfile` output.

`run_ui_benchmark_matrix.py` sequentially runs all three pages at 50, 500, and
5,000 items, three times per scenario, with 20 automated wheel actions per
run. It reports medians across runs, worst-case timings, and total missed
timer intervals. Pass `--json` to include settings and raw per-run results.
