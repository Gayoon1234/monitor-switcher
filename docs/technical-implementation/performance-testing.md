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

Measurements were collected on 22 November 2026 using synthetic UI data and the
local activity database.

`profile_activity.py` copies the activity database to a temporary snapshot,
times history loading/decoding, then measures repeated `set_events()` rendering.
The source database is read-only. Activity displays 25 event cards per page.

`measure_ui_responsiveness.py` creates the page from synthetic data, then
automatically sends wheel events to its scrollable areas. Widget construction
is timed with `perf_counter`; synthetic data generation is outside that
interval. It records wheel-to-processed-widget-snapshot latency and lateness
for a 16 ms Qt timer, including the number of missed timer intervals. The
snapshot latency includes event handling, event processing, and `QWidget.grab()`;
it is not physical display frame presentation or a direct frame-rate measure.
The probe does not measure Windows PnP enumeration/filtering or real hardware.

Run from the repository root:

```powershell
py perf\profile_activity.py --database activity.db --days 30 --repeat 5
py perf\measure_ui_responsiveness.py --page find-my-device --items 50 --scroll-events 200 --json
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

Run the full 27-scenario matrix (three pages, three item counts, and three
repeats) sequentially with one command:

```powershell
py perf\run_ui_benchmark_matrix.py
```

Each run sends 20 wheel actions at 30 ms intervals. Add `--json` to output
settings, every raw run, and the aggregate results as JSON. All wheel actions
in these runs moved the target scrollbar. Times are milliseconds.

Median columns below are medians across the three runs; max columns are the
worst value across those runs; missed intervals are totals across all three.

| Page | Items | Construction median (ms) | Initial paint/snapshot median (ms) | Wheel snapshot median (ms) | Wheel snapshot p95 (ms) | Wheel snapshot max (ms) | Timer max lateness (ms) | Missed 16 ms intervals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity | 50 | 30.87 | 20.39 | 6.81 | 9.50 | 10.91 | 5.43 | 0 |
| Activity | 500 | 32.37 | 20.03 | 7.65 | 9.90 | 12.71 | 7.37 | 0 |
| Activity | 5,000 | 37.24 | 20.32 | 7.59 | 9.79 | 11.52 | 6.47 | 0 |
| My Devices | 50 | 72.13 | 15.98 | 5.51 | 7.69 | 8.78 | 6.87 | 0 |
| My Devices | 500 | 476.45 | 53.30 | 6.26 | 8.79 | 22.13 | 21.61 | 3 |
| My Devices | 5,000 | 4,629.04 | 1,226.25 | 11.47 | 13.71 | 142.95 | 229.37 | 62 |
| Find My Device | 50 | 96.30 | 18.74 | 8.41 | 10.95 | 11.98 | 7.05 | 0 |
| Find My Device | 500 | 791.12 | 85.98 | 8.77 | 11.53 | 42.54 | 40.39 | 9 |
| Find My Device | 5,000 | 8,080.27 | 1,764.79 | 15.29 | 17.76 | 370.32 | 450.08 | 123 |

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

- Activity construction stayed near 30 ms from 50 to 5,000 events, consistent
  with its 25-card page limit.
- Device-page construction and initial layout increased substantially with
  card count. At 5,000 cards, My Devices took 4.47 s to construct and 1.27 s
  for initial layout/paint; Find My Device took 7.46 s and 1.74 s.
- The 5,000-card runs had maximum timer lateness of 205 ms (My Devices) and
  415 ms (Find My Device). Their low p95 values do not exclude these individual
  stalls; the probe reports delivered timer callbacks, not missed intervals.
- The user's typical lists are 22 connected devices and 2 saved devices. These
  synthetic stress results do not show whether actual scrolling animation is
  choppy. The automated probe improves repeatability and records missed timer
  deadlines, but still does not measure physical display frame presentation.
