import argparse
import time
import uuid

from app.models.usb_device import ConfiguredUsbDevice


def configure_parser(commands: argparse._SubParsersAction) -> None:
    parser = commands.add_parser(
        "find-my-device",
        help="Find and save connected USB devices",
    )
    actions = parser.add_subparsers(dest="find_action", required=True)
    actions.add_parser("list", help="List connected USB devices")

    detect = actions.add_parser(
        "detect",
        help="Wait for a newly connected USB device",
    )
    detect.add_argument(
        "--timeout",
        type=float,
        default=60,
        help="Stop waiting after this many seconds (default: 60)",
    )
    detect.add_argument(
        "--nickname",
        help="Save the first detected device with this nickname",
    )


def handle(args: argparse.Namespace, context) -> int:
    if args.find_action == "list":
        devices = context.usb_service.get_devices()
        configured_by_id = {
            device.windows_device_id: device
            for device in context.usb_service.get_configured_devices()
        }
        if not devices:
            print("No connected USB devices found.")
            return 0
        for device in devices:
            saved = configured_by_id.get(device.windows_device_id)
            label = f" ({saved.nickname})" if saved else " (not saved)"
            print(f"{device.name}{label}")
            print(f"  {device.windows_device_id}")
        return 0

    if args.timeout <= 0:
        raise ValueError("Detection timeout must be greater than zero.")

    initial_ids = {
        device.windows_device_id
        for device in context.usb_service.get_devices()
    }
    deadline = time.monotonic() + args.timeout
    print("Waiting for a new USB device. Press Ctrl+C to cancel.")

    while time.monotonic() < deadline:
        for device in context.usb_service.get_devices():
            if device.windows_device_id in initial_ids:
                continue
            print(f"Detected: {device.name}")
            print(f"  {device.windows_device_id}")
            if args.nickname:
                nickname = args.nickname.strip()
                if not nickname:
                    raise ValueError("Nickname cannot be empty.")
                configured = ConfiguredUsbDevice(
                    id=str(uuid.uuid4()),
                    windows_device_id=device.windows_device_id,
                    nickname=nickname,
                )
                context.usb_service.add_device(configured)
                print(f"Saved as {nickname}.")
            return 0
        time.sleep(1)

    print("No new USB device detected before the timeout.")
    return 1
