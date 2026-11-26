---
id: performance-testing
title: Performance Testing
sidebar_position: 2
---

## Hypothesis

Scrolling lag may be caused by UI work increasing with the number of visible
widgets. Activity pagination should keep rendered event cards bounded; device
pages create one card per item. Separately, USB monitoring may delay the UI:
the 500 ms poll calls synchronous Windows device enumeration.

## Data/Results

Measurements were collected on 22, 24, 25, and 26 November 2026 using
synthetic UI data, configured activity history, and live Windows
device/display discovery.

`profile_activity.py` copies the activity database to a temporary snapshot,
times history loading/decoding, then measures repeated `set_events()` rendering.
The source database is read-only. Activity displays 25 event cards per page.

`measure_ui_responsiveness.py` uses the production page widgets and automatically
sends wheel events to scrollable areas. Synthetic data preparation and real
data discovery are timed separately from widget construction. Real-data mode
reads the configured activity period and a read-only database snapshot, USB
devices through the Windows monitor, and displays through read-only discovery.
Page actions and display selectors are disabled; the benchmark does not start
`main.py`, connect USB events to automations, or write to configuration,
activity data, or display inputs. In real-data mode, `--usb-monitor` selects
the configured monitor state or forces it on/off without changing config. When
enabled, the production `QtUsbMonitorAdapter` enumerates USB devices in a worker
thread and passes snapshots to `UsbMonitorService`, with no automation receiver
attached. The pre-change baseline below
was collected when polling still ran on the Qt main thread. The probe records
wheel-to-processed-widget-snapshot latency and lateness for a 16 ms Qt timer,
including missed timer intervals. Snapshot latency includes event handling,
event processing, and `QWidget.grab()`; it is not physical display frame
presentation or a direct frame-rate measure.

Run from the repository root:

```powershell
py perf\profile_activity.py --database activity.db --days 30 --repeat 5
py perf\benchmark_hardware.py --target usb --iterations 5 --warmups 1
py perf\benchmark_hardware.py --target displays --iterations 3 --warmups 1
py perf\measure_ui_responsiveness.py --page find-my-device --items 50 --scroll-events 200 --json
py perf\run_ui_benchmark_matrix.py --real-data --json
py perf\run_ui_benchmark_matrix.py --real-data --usb-monitor enabled --scroll-events 20 --interval-ms 500 --json
py perf\run_ui_benchmark_matrix.py --real-data --usb-monitor disabled --scroll-events 20 --interval-ms 500 --json
```

`benchmark_hardware.py` separately times live USB enumeration and display
discovery. It queries monitor capabilities and current inputs but does not
switch inputs or modify application data.

### Activity history

| Command | Database events | Snapshot (ms) | Query + decode (ms) | Events supplied (visible) | Render median (ms) | Render min (ms) | Render max (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `--days 30 --repeat 5` | 978 | 5.30 | 1.96 | 978 (25) | 44.91 | 44.83 | 45.40 |
| `--synthetic-events 5000 --days all --repeat 5` | 1,293 | 2.94 | 2.05 | 5,000 (25) | 50.39 | 49.11 | 70.27 |

The second run queries 1,293 database events but renders 5,000 synthetic
events. Rendering is repeated five times; only 25 event widgets are created on
each render.

### Hardware discovery (Windows 11, 24 November 2026)

One warmup was excluded. USB enumeration ran five timed iterations; display
discovery ran three. Times are milliseconds; p95 uses these small samples.

| Operation | Result count | Runs | Median (ms) | p95 (ms) | Min (ms) | Max (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| USB enumeration | 22 present USB devices | 5 | 394.78 | 402.31 | 389.79 | 402.31 |
| Display discovery and input queries | 2 displays; 4 inputs | 3 | 3,576.60 | 4,337.26 | 3,464.84 | 4,337.26 |

Monitor-object initialization took 1.29 ms (one measurement). The reported
p95 is based on only three or five samples and is therefore a coarse estimate.

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

Run three real-data repetitions per page with periodic monitoring disabled,
to isolate page loading and rendering:

```powershell
py perf\run_ui_benchmark_matrix.py --real-data --usb-monitor disabled --json
```

This uses the production page widgets with read-only snapshots from the
configured activity database, USB WMI enumeration, and display discovery.
Buttons and input selectors are disabled. The benchmark does not start
`main.py`, connect USB events to automations, or perform display-switch
actions. Periodic USB monitoring was explicitly disabled for this baseline.
Item counts remained stable across repeats. Median columns are medians across
the three runs; maximum columns are worst values across the runs. Times are
milliseconds.

| Page | Real data shown | Data load median (ms) | Construction median (ms) | Initial paint/snapshot median (ms) | Wheel snapshot median (ms) | Wheel snapshot p95 (ms) | Wheel snapshot max (ms) | Timer max lateness (ms) | Missed 16 ms intervals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity | 306 events, last 7 days | 43.65 | 31.79 | 19.68 | 7.38 | 8.79 | 10.26 | 8.95 | 0 |
| My Devices | 2 saved cards; 22 connected USB devices; 2 displays | 3,958.67 | 34.29 | 13.49 | n/a | n/a | n/a | n/a | 0 |
| Find My Device | 22 connected USB devices; 2 saved devices | 476.92 | 72.19 | 20.02 | 6.37 | 8.20 | 17.10 | 16.26 | 1 |

The My Devices run had no scrollable range with two saved cards, so it has no
wheel samples. Its approximately 3.96 s data-loading time includes live
device/display discovery and is separate from the 34 ms widget construction
time. This earlier real-data comparison did not run periodic USB monitoring;
the controlled comparison below measures its effect separately.

Synthetic comparisons at the same item counts were also run three times.
At 306 Activity events, synthetic versus real widget construction was
30.76 ms versus 31.79 ms, with wheel p95 of 9.51 ms versus 8.79 ms. At 22
Find My Device cards, construction was 54.32 ms versus 72.19 ms, with wheel
p95 of 9.83 ms versus 8.20 ms. My Devices at two saved cards had no scroll
range in either case.

### Original synchronous USB monitor baseline

These results were collected before USB enumeration was moved off the Qt main
thread. They provide the baseline for the worker-thread comparison below.
The benchmark was run three times per page/state with 20 automated wheel
actions spaced 500 ms apart (about 10 seconds per run):

```powershell
py perf\run_ui_benchmark_matrix.py --real-data --usb-monitor enabled --scroll-events 20 --interval-ms 500 --json
py perf\run_ui_benchmark_matrix.py --real-data --usb-monitor disabled --scroll-events 20 --interval-ms 500 --json
```

In enabled baseline runs, the monitor took an initial device snapshot and
continued polling via WMI on the Qt main thread. Device events were not
connected to the automation service, so no automation or display action could
run. Disabled runs did not start the monitor or poll. `config.json` was not
changed. Data at the time was 48 Activity events (last 7 days), 22 connected
USB devices, 2 saved devices, and 2 displays. My Devices had no scrollable
range with two saved cards; it was measured idle for the same 10-second
duration.

Median values are across the three runs; maxima are the worst observed per
state; missed intervals are totals. Times are milliseconds.

| Page | Monitor | Data load median | Construction median | Initial paint median | Wheel median | Wheel p95 | Wheel max | Timer max lateness | Missed 16 ms intervals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Activity (48 events) | On | 77.96 | 31.83 | 19.67 | 5.68 | 7.31 | 8.52 | 448.79 | 1,450 |
| Activity (48 events) | Off | 76.20 | 33.62 | 19.45 | 8.03 | 9.83 | 11.94 | 7.43 | 0 |
| My Devices (2 saved cards) | On | 3,718.14 | 30.88 | 11.30 | n/a | n/a | n/a | 459.36 | 1,440 |
| My Devices (2 saved cards) | Off | 3,814.43 | 32.17 | 12.19 | n/a | n/a | n/a | 1.76 | 0 |
| Find My Device (22 USB devices) | On | 472.49 | 72.46 | 20.51 | 5.71 | 10.34 | 436.18 | 440.55 | 1,485 |
| Find My Device (22 USB devices) | Off | 484.79 | 73.35 | 20.23 | 8.08 | 10.68 | 13.21 | 8.84 | 0 |

| Page | Monitor | Polls/run median | Poll duration median | Poll duration max | Monitor-start snapshot median |
| --- | --- | ---: | ---: | ---: | ---: |
| Activity | On | 20 | 422.07 | 464.54 | 451.48 |
| My Devices | On | 20 | 431.23 | 468.99 | 451.76 |
| Find My Device | On | 20 | 427.97 | 456.46 | 446.11 |
| All pages | Off | 0 | n/a | n/a | 0 |

The roughly 422–431 ms median WMI call blocked the UI thread for most of each
500 ms polling interval. With monitoring on, the timer recorded a worst
lateness of 441–459 ms and about 480 missed 16 ms deadlines per 10-second run.
With monitoring off, no timer intervals were missed and worst lateness was
under 9 ms. Find My Device's worst wheel-to-snapshot latency fell from 436 ms
to 13 ms; median and p95 wheel response were similar.

Widget construction and page data-loading times were essentially unchanged.
For example, My Devices data loading remained about 3.7–3.8 seconds because
its initial display discovery is still performed even when periodic USB
monitoring is disabled. Thus the setting improves responsiveness during
background monitoring but does not fix slow initial hardware discovery.

The totals and worst-case timings show occasional long UI-thread stalls as
item counts rise, particularly at 5,000 items. The two-device Find My Device
case has no scrollable range and is not included in this matrix.

### Worker-thread USB monitor comparison

After moving USB enumeration to a worker thread, the same controlled comparison
was run three times per state on Find My Device. Each run used 22 connected USB
devices, 20 wheel actions at 500 ms intervals, and a 500 ms monitor interval.
Device events remained disconnected from automations. These commands do not
change `config.json`:

```powershell
py perf\run_ui_benchmark_matrix.py --pages find-my-device --real-data --usb-monitor enabled --repeats 3 --scroll-events 20 --interval-ms 500 --json
py perf\run_ui_benchmark_matrix.py --pages find-my-device --real-data --usb-monitor disabled --repeats 3 --scroll-events 20 --interval-ms 500 --json
```

Median values are across the three runs; maximum values are the worst observed
per state. Timer lateness is the worst delivered 16 ms timer callback; missed
intervals are totals across the three runs. Times are milliseconds.

| Monitor | Data load median | Construction median | Timer max lateness | Missed 16 ms intervals | Wheel median | Wheel p95 median | Wheel max | Polls/run median | Poll duration median | Poll duration max | Monitor-start call median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| On | 463.50 | 72.43 | 9.25 | 0 | 5.46 | 6.39 | 11.53 | 20 | 424.83 | 458.79 | 0.18 |
| Off | 468.43 | 70.29 | 8.85 | 0 | 9.58 | 12.26 | 14.26 | 0 | n/a | n/a | 0 |

WMI enumeration still took about 425 ms per poll, but the UI timer stayed
responsive while it ran: the enabled runs had no missed intervals and no
wheel-to-snapshot sample above 12 ms. This confirms moving the I/O to a worker
thread removes the measured main-thread stall without reducing enumeration
time. The enabled monitor's startup call returned in about 0.18 ms because its
initial snapshot is asynchronous. Initial page discovery remains synchronous
and is a separate cost.

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
- The original synchronous USB poll blocked the Qt main thread for about
  422–431 ms per poll, with about 480 missed 16 ms deadlines per 10-second run.
  After moving polling to a worker thread, WMI still took about 425 ms, but
  there were no missed timer intervals across three enabled runs and the worst
  Find My Device scroll snapshot was 12 ms.
  Display discovery took about 3.58 s for two displays, affecting startup/data
  loading rather than each USB polling cycle.
- Disabling USB monitoring does not materially change widget construction or
  the slow initial My Devices discovery; those are separate costs.
- These are QWidget snapshot and event-loop measurements, not physical display
  frame times. They do not prove frame-rate or compositor behavior.
