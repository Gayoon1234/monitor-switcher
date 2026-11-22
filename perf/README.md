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
```

`profile_activity.py` reports database load time, median Activity rendering
time, and the most expensive Python calls in one render. The database is copied
using SQLite's read-only backup API before it is opened by the repository.

`measure_ui_responsiveness.py` opens a test window populated with synthetic
events or devices. Scroll during the measurement interval; it reports event-loop
timer lateness (median, p95, and maximum), widget construction time, and
initial layout/paint processing time. Timer lateness indicates UI-thread
responsiveness, not exact frame rate. Synthetic device counts should be kept
realistic when comparing against normal use.

For useful comparisons, run each scenario several times on the same machine and
compare medians. A high render/setup time points toward Python-side widget
construction or layout work; event-loop lateness while scrolling indicates
that the UI thread is missing scheduled timer intervals. Neither measurement
alone proves the cause, and Qt's native painting time is not fully represented
in Python's `cProfile` output.
