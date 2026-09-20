from monitorcontrol import get_monitors

monitors = get_monitors()

for i, monitor in enumerate(monitors, 1):
    print(f"\n=== Monitor {i} ===")

    try:
        with monitor:
            print("VCP capabilities:")
            print(monitor.get_vcp_capabilities())

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")