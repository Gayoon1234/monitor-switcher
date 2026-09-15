from monitorcontrol import get_monitors

for i, monitor in enumerate(get_monitors(), 1):
    print(f"\n=== Monitor {i} ===")
    print(monitor)

    try:
        with monitor:
            capabilities = monitor.get_vcp_capabilities()
            print(capabilities)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        