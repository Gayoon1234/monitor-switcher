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

| Command | Database events | Snapshot (ms) | Query + decode (ms) | Events supplied (visible) | Render median (min-max, ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `--days 30 --repeat 5` | 978 | 5.30 | 1.96 | 978 (25) | 44.91 (44.83-45.40) |
| `--synthetic-events 5000 --days all --repeat 5` | 1,293 | 2.94 | 2.05 | 5,000 (25) | 50.39 (49.11-70.27) |

The second run queries 1,293 database events but renders 5,000 synthetic
events. Rendering is repeated five times; only 25 event widgets are created on
each render.

### Automated scroll sample

One automated run per scenario, with 20 wheel actions at 30 ms intervals.
Stress cases were run sequentially to avoid competing benchmark processes.
These are verification samples, not multi-run baselines. Times are milliseconds.

| Page | Items | Construction | Initial paint/snapshot | Wheel snapshot median / p95 / max | Timer max lateness | Missed 16 ms intervals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity | 50 | 30.35 | 28.11 | 6.56 / 8.06 / 8.08 | 3.35 | 0 |
| My Devices | 22 | 49.37 | 14.72 | 5.04 / 6.71 / 6.87 | 3.02 | 0 |
| My Devices | 5,000 | 4,589.93 | 1,369.65 | 11.33 / 14.48 / 141.38 | 226.37 | 21 |
| Find My Device | 5,000 | 7,997.91 | 1,704.98 | 16.25 / 18.31 / 356.06 | 433.12 | 40 |

Every scroll action moved the target scrollbar. At two Find My Device items
there was no scrollable range, so no wheel latency could be measured. Repeat
each scenario several times before treating these sample values as a baseline.

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
