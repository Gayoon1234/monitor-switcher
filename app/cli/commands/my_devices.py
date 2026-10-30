import argparse


def configure_parser(commands: argparse._SubParsersAction) -> None:
    parser = commands.add_parser(
        "my-devices",
        help="Manage saved devices and displays",
    )
    actions = parser.add_subparsers(dest="my_devices_action", required=True)

    actions.add_parser("list", help="List saved devices and displays")

    rename = actions.add_parser("rename", help="Rename a saved USB device")
    rename.add_argument("device_id", help="Saved device ID or Windows device ID")
    rename.add_argument("nickname")

    remove = actions.add_parser("remove", help="Remove a saved USB device")
    remove.add_argument("device_id", help="Saved device ID or Windows device ID")
    remove.add_argument("--yes", action="store_true", help="Skip confirmation")

    displays = actions.add_parser("displays", help="List connected displays")
    display_actions = displays.add_subparsers(
        dest="display_action",
        required=True,
    )
    display_actions.add_parser("list", help="List displays and supported inputs")
    display_actions.add_parser("refresh", help="Rediscover displays")
    switch = display_actions.add_parser("switch", help="Switch a display input")
    switch.add_argument("display_id")
    switch.add_argument("input_id")


def handle(args: argparse.Namespace, context) -> int:
    if args.my_devices_action == "list":
        displays = context.display_service.get_displays()
        devices = context.usb_service.get_configured_devices()
        connected_ids = {
            device.windows_device_id
            for device in context.usb_service.get_devices()
        }

        print("Displays")
        if not displays:
            print("  No displays found.")
        for display in displays:
            current = display.current_input or "unknown"
            print(f"  {display.id}: {display.name} (input: {current})")
            for input_ in display.inputs:
                print(f"    {input_.input_id} ({input_.input_type.value})")

        print("\nSaved USB devices")
        if not devices:
            print("  No devices saved.")
        for device in devices:
            status = (
                "connected"
                if device.windows_device_id in connected_ids
                else "disconnected"
            )
            print(f"  {device.id}: {device.nickname} ({status})")
            print(f"    {device.windows_device_id}")
        return 0

    if args.my_devices_action == "rename":
        device = _find_configured_device(context, args.device_id)
        device.nickname = args.nickname.strip()
        if not device.nickname:
            raise ValueError("Nickname cannot be empty.")
        context.usb_service.update_device(device)
        print(f"Renamed device to {device.nickname}.")
        return 0

    if args.my_devices_action == "remove":
        device = _find_configured_device(context, args.device_id)
        if not args.yes:
            answer = input(f"Remove '{device.nickname}'? [y/N] ").strip().lower()
            if answer not in {"y", "yes"}:
                print("Cancelled.")
                return 0
        context.usb_service.remove_device(device.id)
        print(f"Removed {device.nickname}.")
        return 0

    if args.display_action == "list":
        _print_displays(context.display_service.get_displays())
    elif args.display_action == "refresh":
        _print_displays(context.display_service.refresh_displays())
    elif args.display_action == "switch":
        context.display_service.switch_input(args.display_id, args.input_id)
        print(f"Switched {args.display_id} to {args.input_id}.")
    return 0


def _find_configured_device(context, reference: str):
    for device in context.usb_service.get_configured_devices():
        if device.id == reference or device.windows_device_id == reference:
            return device
    raise ValueError(f"Saved USB device not found: {reference}")


def _print_displays(displays) -> None:
    if not displays:
        print("No displays found.")
        return
    for display in displays:
        current = display.current_input or "unknown"
        print(f"{display.id}: {display.name} (current input: {current})")
        for input_ in display.inputs:
            print(f"  {input_.input_id} ({input_.input_type.value})")
