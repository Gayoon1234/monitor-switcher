---
title: Services
---

The services in `app/services/` coordinate application behavior between the
hardware adapters, data models, persistence, and UI. They contain the app's
main workflows while leaving Windows-specific device access to the hardware
implementations.

| Service | Responsibility |
| --- | --- |
| [ActivityRepository](./activity-repository) | Store and retrieve activity history in SQLite. |
| [AutomationService](./automation-service) | Match USB events to automations, run actions, and report activity. |
| [ConfigRepository](./config-repository) | Load and save configured devices, automations, and displays in JSON. |
| [DisplayService](./display-service) | Discover displays, maintain their state, and switch inputs. |
| [ThemeService](./theme-service) | Load theme palettes and provide UI colors and stylesheets. |
| [UsbMonitorService](./usb-monitor-service) | Poll for USB connection changes and emit device events. |
| [UsbService](./usb-service) | Read connected and configured USB devices and manage saved devices. |

These services are generally composed by the application or CLI startup code.
Hardware-dependent services receive their hardware interfaces as constructor
arguments, which also makes them testable with fakes.
