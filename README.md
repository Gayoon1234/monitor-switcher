# Monitor Switcher

Monitor Switcher is a Windows desktop utility for automatically switching monitor inputs when a specific USB device connects or disconnects.

It is designed for setups where a display should change to the correct source when a laptop, dock, console, or other USB device appears. Typical uses include:

- switching a monitor to a laptop dock when the dock is plugged in
- changing a TV or monitor to a console when a controller/console adapter is connected
- switching back to a different input when the device is unplugged

## What the software does

The app does three things:

1. Discovers connected displays and their supported inputs.
2. Tracks USB devices currently connected to the machine.
3. Runs user-defined automations to switch a display to a target input when a configured USB event occurs.

The software uses Windows WMI and the `monitorcontrol` library to enumerate hardware, then exposes the result through a PySide6 desktop UI.

## Features

- Discover current displays and list valid input sources
- Monitor USB device connect/disconnect events
- Save configured USB devices with friendly labels
- Create automations based on device connection state
- Switch a display to a target input when an automation triggers
- Keep a local activity log of automation and device events
- Persist configuration in JSON files and SQLite activity history
- Change the UI theme from Settings

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- A machine with a supported monitor that can be controlled through Windows APIs
- A monitor and USB device setup that you want to automate

## Installation

1. Clone the repository.
2. Open a terminal in the project root.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the project dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

## Running the app

From the project root, start the app with:

```powershell
python main.py
```

This launches the PySide6 desktop application.

## Typical usage workflow

### 1. Start the app

When the main window opens, you will see a sidebar with these sections:

- My Devices
- Find My Device
- Automations
- Activity
- Settings

### 2. Add or detect USB devices

Use the Find My Device page to discover connected USB hardware.

- Click `Detect New Device`.
- Connect the target USB device.
- The app will detect the new device and show it as a card.
- Add it with a nickname such as `Laptop Dock`, `Nintendo Switch`, or `Work USB`.

You can also review previously configured devices on the My Devices page.

### 3. Review displays and inputs

On My Devices:

- Displays are listed with their detected name and available inputs.
- Each display card shows the current input if the hardware reports it.
- If needed, you can manually trigger a switch from the card actions.

### 4. Create an automation

Open Automations and click `Add Automation`.

Configure:

- a trigger type: connected or disconnected
- the USB device to watch
- one or more actions: switch a display to a specific input

Example:

- Trigger: `Laptop Dock connected`
- Action: switch `Living Room Monitor` to `HDMI 2`

When the dock is plugged in, the app will send the input-change command to the selected display.

### 5. Check activity and logs

The Activity page shows device and automation events, including success/failure state.

The Settings page lets you:

- choose the UI theme
- filter activity history by time range
- clear all saved activity logs

## Configuration files

The project stores configuration in the repository root:

- `config.json` stores configured USB devices, displays, and automations
- `theme.json` stores the selected application theme and custom colors
- `activity.db` stores the event log used by the Activity page

If the app starts with no `config.json`, it will discover current displays and save them automatically.

A simplified example of the persisted config looks like this:

```json
{
  "usb_devices": [
    {
      "id": "device-uuid",
      "windows_device_id": "USB\\VID_1234&PID_5678\\...",
      "nickname": "Laptop Dock"
    }
  ],
  "automations": [
    {
      "id": "automation-001",
      "name": "Dock connected",
      "enabled": true,
      "trigger": {
        "type": "device_connected",
        "device_id": "device-uuid"
      },
      "actions": [
        {
          "type": "switch_input",
          "display_id": "display-001",
          "input_id": "HDMI2"
        }
      ]
    }
  ],
  "displays": [
    {
      "id": "display-001",
      "name": "Living Room Monitor",
      "windows_device_id": "DISPLAY\\...",
      "inputs": [
        {"input_id": "HDMI2", "input_type": "HDMI"}
      ]
    }
  ]
}
```

## Important implementation notes

- This project is tightly targeted at Windows. It depends on `pywin32` and the Windows WMI APIs.
- By default, the app watches all connected USB devices and emits a device event for each one that connects or disconnects.
- The current automation model is intentionally simple: it can trigger on USB connect/disconnect and execute a switch-input action.
- The app is best suited to local desktop usage on a single Windows machine with direct access to the display hardware.

## Project layout

```text
app/
  hardware/        Windows monitor and USB integration
  models/          Data models for displays, USB devices, and automations
  services/        Loading, saving, switching, and automation logic
  ui/              PySide6 user interface screens and widgets
main.py            Application entry point
requirements.txt   Python dependencies
config.json        Local runtime configuration
theme.json         UI palette definitions
activity.db        Activity log database
tests/             Automated unit tests
docs/              Technical implementation notes
```

## Further reading

- [docs/technical-implementation.md](docs/technical-implementation.md)
