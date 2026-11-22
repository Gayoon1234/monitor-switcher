---
id: performance-testing
title: Performance Testing (UI)
sidebar_position: 2
---

## Hypothesis

Scrolling lag may be caused by UI work increasing with the number of visible
widgets. Activity pagination should keep rendered event cards bounded; device
pages create one card per item.

## Data/Results

Measurements were collected on 22 November 2026 using synthetic UI data,
configured activity history, and live Windows device/display discovery.

`profile_activity.py` copies the activity database to a temporary snapshot,
times history loading/decoding, then measures repeated `set_events()` rendering.
The source database is read-only. Activity displays 25 event cards per page.

`measure_ui_responsiveness.py` uses the production page widgets and automatically
sends wheel events to scrollable areas. Synthetic data preparation and real
data discovery are timed separately from widget construction. Real-data mode
reads the configured activity period and a read-only database snapshot, USB
devices through the Windows monitor, and displays through read-only discovery.
Page actions and display selectors are disabled; the benchmark does not start
the app's automation monitor or write to configuration, activity data, or
display inputs. It records wheel-to-processed-widget-snapshot latency and
lateness for a 16 ms Qt timer, including missed timer intervals. Snapshot
latency includes event handling, event processing, and `QWidget.grab()`; it is
not physical display frame presentation or a direct frame-rate measure.

Run from the repository root:

```powershell
py perf\profile_activity.py --database activity.db --days 30 --repeat 5
py perf\measure_ui_responsiveness.py --page find-my-device --items 50 --scroll-events 200 --json
py perf\run_ui_benchmark_matrix.py --real-data --json
```

### Activity history

| Command | Database events | Snapshot (ms) | Query + decode (ms) | Events supplied (visible) | Render median (ms) | Render min (ms) | Render max (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `--days 30 --repeat 5` | 978 | 5.30 | 1.96 | 978 (25) | 44.91 | 44.83 | 45.40 |
| `--synthetic-events 5000 --days all --repeat 5` | 1,293 | 2.94 | 2.05 | 5,000 (25) | 50.39 | 49.11 | 70.27 |

The second run queries 1,293 database events but renders 5,000 synthetic
events. Rendering is repeated five times; only 25 event widgets are created on
each render.

### Automated scroll sample

Run the full synthetic 27-scenario matrix (three pages, three item counts, and
three repeats) sequentially with one command:

```powershell
py perf\run_ui_benchmark_matrix.py
```

Each run sends 20 wheel actions at 30 ms intervals. Add `--json` to output
settings, every raw run, and the aggregate results as JSON. All wheel actions
in these runs moved the target scrollbar. Times are milliseconds.

Data loading is measured separately; synthetic data generation is not included
in construction time. Median columns below are medians across the three runs;
max columns are the worst value across those runs; missed intervals are totals
across all three.

| Page | Items | Data load median (ms) | Construction median (ms) | Initial paint/snapshot median (ms) | Wheel snapshot median (ms) | Wheel snapshot p95 (ms) | Wheel snapshot max (ms) | Timer max lateness (ms) | Missed 16 ms intervals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity | 50 | 0.09 | 31.06 | 21.44 | 7.02 | 9.06 | 10.09 | 6.33 | 0 |
| Activity | 500 | 0.84 | 31.36 | 22.32 | 7.00 | 9.68 | 11.65 | 8.00 | 0 |
| Activity | 5,000 | 5.99 | 31.01 | 21.47 | 7.40 | 9.71 | 11.67 | 7.93 | 0 |
| My Devices | 50 | 0.34 | 71.45 | 17.81 | 5.77 | 8.91 | 10.51 | 9.27 | 0 |
| My Devices | 500 | 0.88 | 477.32 | 53.52 | 5.83 | 8.61 | 20.17 | 18.61 | 3 |
| My Devices | 5,000 | 8.53 | 4,621.91 | 1,292.49 | 11.95 | 15.25 | 145.51 | 228.61 | 62 |
| Find My Device | 50 | 0.34 | 96.99 | 19.78 | 7.72 | 10.47 | 11.63 | 6.89 | 0 |
| Find My Device | 500 | 0.88 | 795.02 | 85.73 | 8.69 | 11.24 | 43.52 | 43.74 | 9 |
| Find My Device | 5,000 | 8.15 | 7,817.59 | 1,706.28 | 16.21 | 19.29 | 357.81 | 435.52 | 120 |

### Read-only real-data comparison

Run three real-data repetitions per page with:

```powershell
py perf\run_ui_benchmark_matrix.py --real-data --json
```

This uses the production page widgets with read-only snapshots from the
configured activity database, USB WMI enumeration, and display discovery.
Buttons and input selectors are disabled. The benchmark does not start
`main.py`, its USB automation monitor, or any display-switch actions. Item
counts remained stable across repeats. Median columns are medians across the
three runs; maximum columns are worst values across the runs. Times are
milliseconds.

| Page | Real data shown | Data load median (ms) | Construction median (ms) | Initial paint/snapshot median (ms) | Wheel snapshot median (ms) | Wheel snapshot p95 (ms) | Wheel snapshot max (ms) | Timer max lateness (ms) | Missed 16 ms intervals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity | 306 events, last 7 days | 43.65 | 31.79 | 19.68 | 7.38 | 8.79 | 10.26 | 8.95 | 0 |
| My Devices | 2 saved cards; 22 connected USB devices; 2 displays | 3,958.67 | 34.29 | 13.49 | n/a | n/a | n/a | n/a | 0 |
| Find My Device | 22 connected USB devices; 2 saved devices | 476.92 | 72.19 | 20.02 | 6.37 | 8.20 | 17.10 | 16.26 | 1 |

The My Devices run had no scrollable range with two saved cards, so it has no
wheel or timer samples. Its approximately 3.96 s data-loading time includes
live device/display discovery and is separate from the 34 ms widget
construction time.

Synthetic comparisons at the same item counts were also run three times.
At 306 Activity events, synthetic versus real widget construction was
30.76 ms versus 31.79 ms, with wheel p95 of 9.51 ms versus 8.79 ms. At 22
Find My Device cards, construction was 54.32 ms versus 72.19 ms, with wheel
p95 of 9.83 ms versus 8.20 ms. My Devices at two saved cards had no scroll
range in either case.

The totals and worst-case timings show occasional long UI-thread stalls as
item counts rise, particularly at 5,000 items. The two-device Find My Device
case has no scrollable range and is not included in this matrix.

### Previous manual-stress baseline

These results were collected with the earlier manually scrolled probe. They
remain useful as historical setup/event-loop measurements but cannot be
compared directly to the automated wheel-to-snapshot results. Times are
milliseconds; timer columns show median, p95, and maximum lateness among
delivered timer callbacks.

#### Activity

| Items | Duration | Widget construction | Initial layout/paint | Timer samples | Timer median | Timer p95 | Timer max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 30 s | 29.59 | 15.39 | 1,872 | 0.26 | 1.86 | 22.89 |
| 500 | 30 s | 29.37 | 15.28 | 1,863 | 0.14 | 1.20 | 31.66 |
| 5,000 | 30 s | 29.81 | 16.30 | 1,864 | 0.42 | 1.47 | 30.66 |

#### My Devices

| Items | Duration | Widget construction | Initial layout/paint | Timer samples | Timer median | Timer p95 | Timer max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 30 s | 69.72 | 15.43 | 1,875 | 0.30 | 1.48 | 13.50 |
| 500 | 30 s | 480.69 | 45.98 | 1,874 | 0.00 | 0.00 | 18.35 |
| 5,000 | 30 s | 4,474.34 | 1,269.26 | 1,857 | 0.00 | 12.08 | 205.18 |

#### Find My Device

| Items | Duration | Widget construction | Initial layout/paint | Timer samples | Timer median | Timer p95 | Timer max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 30 s | 91.73 | 23.76 | 1,875 | 0.26 | 2.08 | 13.04 |
| 100 | 30 s | 173.03 | 19.86 | 1,875 | 0.00 | 1.35 | 6.17 |
| 200 | 30 s | 325.03 | 34.36 | 1,875 | 0.41 | 2.45 | 14.27 |
| 500 | 30 s | 906.69 | 75.74 | 1,873 | 4.58 | 7.15 | 37.69 |
| 5,000 | 30 s | 7,459.84 | 1,742.67 | 1,837 | 0.00 | 0.57 | 414.54 |

## Conclusion

- Overall, UI responsiveness looks good for the current real-world device
  counts; no immediate UI optimization is indicated. However, the device pages
  do not scale well to very large lists.
- Activity stayed near 31 ms of widget construction from 50 to 5,000 synthetic
  events, consistent with rendering only its first 25 event cards.
- Device-card construction and initial paint grew substantially at high
  synthetic counts. At 5,000 cards, worst timer lateness was 229 ms for My
  Devices and 436 ms for Find My Device.
- With current real data (22 connected USB devices and 2 saved devices), the
  Find My Device page had a 6.37 ms median wheel response and one missed timer
  interval across three runs. My Devices had no overflow with two saved cards.
- Data loading is a separate concern: My Devices real-data discovery took
  about 3.96 s, compared with about 34 ms for widget construction. Profile
  hardware discovery separately before attributing that delay to UI rendering.
- These are QWidget snapshot and event-loop measurements, not physical display
  frame times. They do not prove frame-rate or compositor behavior.
