# Monitor Switcher

A small Windows utility that automatically switches monitor inputs based on which computer is connected to a USB switch.

## How it works

The utility monitors a specific USB hub used by a USB switch.

- **USB hub connected** → PC
  - Monitor 1 → HDMI
  - Monitor 2 → VGA

- **USB hub disconnected** → Mac
  - Monitor 1 → VGA
  - Monitor 2 → DVI

The application runs quietly in the Windows system tray and displays the current PC/Mac state.

## Requirements

- Windows
- Python 3
- A monitor supporting DDC/CI
- A USB switch
- `monitorcontrol`
- `pywin32`
- `pystray`
- `Pillow`

## Installation

Clone the repository and install the dependencies:

```powershell
py -m pip install -r requirements.txt
```

## Configuration

Edit `switcher_system_tray.py` and change `HUB_ID` to the device ID of the USB hub used by your USB switch:

```python
HUB_ID = r"USB\VID_05E3&PID_0626\5&21296CF&0&17"
```

The monitor input mappings can also be changed in:

```python
set_pc_inputs()
set_mac_inputs()
```

## Running

```powershell
py switcher_system_tray.py
```

The application will appear in the Windows system tray.

## Building the EXE

Install PyInstaller:

```powershell
py -m pip install pyinstaller
```

Build:

```powershell
py -m PyInstaller --onefile --noconsole --name MonitorSwitcher switcher_system_tray.py
```

The executable will be created in:

```text
dist/MonitorSwitcher.exe
```

## Automatic startup

Create a shortcut to `MonitorSwitcher.exe` in:

```text
shell:startup
```

This allows the monitor switcher to start automatically when Windows logs in.

## License

MIT
