---
id: performance-testing
title: Performance Testing
sidebar_position: 2
---

This page documents the lightweight performance probes in the repository's
`perf/` directory and the first recorded UI baseline.

## What the probes measure

Run the commands from the repository root in an environment where the project
dependencies, including PySide6, are installed. In PowerShell, `py` can be used
instead of `python` if it selects the Python environment with those dependencies.

### Activity history and rendering

```powershell
py perf\profile_activity.py --database activity.db --days 30
py perf\profile_activity.py --synthetic-events 5000 --days all
```

`profile_activity.py` reports:

- The time to copy the activity database to a temporary snapshot.
- The time to query and decode matching events from that snapshot.
- Median, minimum, and maximum Activity page rendering times over repeated runs.
- The top Python calls by cumulative time in one render, using `cProfile`.

The source database is opened read-only and copied using SQLite's backup API.
The repository loads from the temporary copy, which is deleted when the script
finishes. `--synthetic-events` measures rendering with generated data instead of
database history. The Activity page currently renders up to 25 event cards per
page, so increasing the synthetic event count does not increase the number of
cards on the first page.

### UI page construction and responsiveness

```powershell
py perf\measure_ui_responsiveness.py --page activity --items 500
py perf\measure_ui_responsiveness.py --page my-devices --items 50
py perf\measure_ui_responsiveness.py --page find-my-device --items 50
```

The script opens a test window populated with synthetic data. Scroll the page
during the measurement interval. It reports:

- **Widget construction:** elapsed time to build the page's widgets.
- **Initial layout/paint processing:** elapsed time processing Qt events after
  the window is shown.
- **UI event-loop timer lateness:** median, p95, and maximum lateness for a
  16 ms timer while the test window is open.

Timer lateness is an indicator of event-loop responsiveness, not a direct
measurement of frame rate or of the time taken to paint an individual frame.
The `cProfile` report covers Python calls and does not fully account for Qt's
native layout and painting work. The probe uses synthetic devices and does not
perform real hardware discovery.

## Initial Find My Device baseline

The first desktop measurement was recorded on 22 November 2026 with:

```powershell
py perf\measure_ui_responsiveness.py --page find-my-device --items 50
```

| Measurement | Result |
| --- | ---: |
| Synthetic connected devices | 50 |
| Widget construction | 143.46 ms |
| Initial layout/paint processing | 12.52 ms |
| Event-loop timer samples | 935 |
| Timer lateness, median | 0.00 ms |
| Timer lateness, p95 | 7.37 ms |
| Timer lateness, maximum | 55.88 ms |

This is an initial reference measurement, not a performance target. In
particular, the single maximum lateness value does not establish a persistent
scrolling problem. Results vary with hardware, OS load, Python/Qt versions,
window system, and user scroll activity.

## Comparing measurements

For a useful comparison:

1. Use the same computer, Python environment, page, item count, and duration.
2. Keep the test window visible and follow the same scrolling pattern.
3. Run each case several times and compare medians as well as p95 and maximum
   timer lateness.
4. Change one factor at a time, such as page type or item count.

High construction time points to page/widget creation as a candidate for
investigation. Elevated event-loop lateness during scrolling indicates that Qt
callbacks are being delayed, but it does not by itself identify whether Python
work, layout, or painting caused the delay. Use the Activity profiler's
function-level results and follow-up measurements to narrow down the cause
before optimizing.
