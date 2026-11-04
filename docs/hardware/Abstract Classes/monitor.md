---
title: Monitor
sidebar_position: 1
---

## What this class does

At a high level this application needs to interact with connected monitors to switch the input source on the fly.

This is broken up into two classes, `MonitorController` responsible for connecting to the monitors and `DisplayDiscovery` which is responsible for dynamically mapping out the available monitors.

To mitigate perfomance issues `DisplayDiscovery` runs once on the first time the app loads and writes the output to `config.json`, subsequent launches reuse the same monitor configs.

## Abstract Class definition

```python
from abc import ABC, abstractmethod

from app.models.display import Display


class MonitorController(ABC):

    @abstractmethod
    def set_displays(self, displays: list[Display]) -> None:
        pass

    @abstractmethod
    def switch_input(self, display_id: str, input_id: str) -> None:
        pass


class DisplayDiscovery(ABC):

    @abstractmethod
    def get_displays(self) -> list[Display]:
        pass
```

- `set_displays(displays)`: Configures the controller with the monitors to use for subsequent operations.
- `switch_input(display_id, input_id)`: Switches the input source of the monitor to the specified value. Both display_id and input_id are stored in the `Display` model.
- `get_displays()`: Discovers and returns the connected monitors as `Display` models.
