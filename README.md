# Monitor Switcher

Monitor Switcher is a Windows desktop utility for automatically switching monitor inputs when USB devices connect or disconnect.

It is designed for setups where a display should change to a specific source when a particular device is plugged in or removed, such as switching a monitor to a laptop, console, or docking station based on USB activity.

## Features

- Discover available displays and their supported inputs
- Track USB devices that are currently present
- Save configured USB devices with friendly nicknames
- Create automations that trigger on device connect or disconnect events
- Switch a display to a target input when the automation fires
- Keep a local activity log of device and automation events
- Persist configuration in a local JSON file

## How it works

The application monitors:

- Windows display devices and their inputs
- USB device connect/disconnect events

When a configured USB device matches an automation trigger, it executes one or more actions such as switching a display to a specific input. This enables simple "plug in device, monitor changes to the right port" workflows.

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- Access to the Windows device APIs used by the app

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the app

From the project root:

```bash
python main.py
```

This launches the PySide6 desktop application.

## Configuration

The app stores config data in a local `config.json` file created in the project root. It can contain:

- `usb_devices`: configured USB devices
- `automations`: automation rules triggered by USB events
- `displays`: discovered monitor definitions and inputs

A simplified example:

```json
{
  "usb_devices": [
    {
      "id": "device1",
      "windows_device_id": "USB\\VID_1234&PID_5678\\...",
      "nickname": "Laptop Dock"
    }
  ],
  "automations": [
    {
      "id": "automation1",
      "name": "Dock connected",
      "enabled": true,
      "trigger": {
        "type": "device_connected",
        "device_id": "device1"
      },
      "actions": [
        {
          "type": "switch_input",
          "display_id": "display1",
          "input_id": "HDMI1"
        }
      ]
    }
  ],
  "displays": [
    {
      "id": "display1",
      "name": "Living Room Monitor",
      "windows_device_id": "DISPLAY\\...",
      "inputs": [
        {"input_id": "HDMI1", "input_type": "HDMI"}
      ]
    }
  ]
}
```

Application palettes are configured in `theme.json` under the `themes` object.
The Settings tab lets you switch among Dark, Light, Hacker, and Harlequin while
the app is running; the selected theme is saved for the next launch. Palette
color values must be six-digit hex strings:

```json
{
  "active_theme": "dark",
  "themes": {
    "dark": {
      "background": "#1e1e1e",
      "surface": "#252526",
      "text": "#f1f1f1",
      "primary": "#4c8dff",
      "primary_text": "#ffffff"
    },
    "light": {
      "background": "#f4f5f7",
      "surface": "#ffffff",
      "text": "#202124",
      "primary": "#2563eb",
      "primary_text": "#ffffff"
    }
  }
}
```

Activity history shows the last 30 days by default. In Settings, you can choose
7, 30, 90, or 365 days, or show all saved events. Changing this filter does not
delete older events. Use **Delete all activity logs** in Settings to permanently
clear the activity database.

## Project layout

```text
app/
  hardware/        Windows monitor and USB integration
  models/         Data models for displays, USB devices, and automations
  services/       Loading, saving, switching, and automation logic
  ui/             PySide6 user interface screens and widgets
main.py           Application entry point
requirements.txt  Python dependencies
tests/            Automated test coverage for repository and service behavior
```

## Notes

- This project currently targets Windows-specific hardware APIs and is not intended to be a cross-platform application.
- The app is best suited to local desktop usage with direct monitor access on a Windows machine.
- If no config exists yet, the app will discover current displays and persist them automatically.
