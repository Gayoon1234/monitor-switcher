import argparse
import sys

from app.cli.commands import activity, automations, find_my_device, my_devices, settings
from app.cli.services import create_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="monitor-switcher",
        description="Control Monitor Switcher from the command line.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    my_devices.configure_parser(commands)
    find_my_device.configure_parser(commands)
    automations.configure_parser(commands)
    activity.configure_parser(commands)
    settings.configure_parser(commands)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "my-devices": my_devices.handle,
        "find-my-device": find_my_device.handle,
        "automations": automations.handle,
        "activity": activity.handle,
        "settings": settings.handle,
    }
    with_hardware = args.command in {
        "my-devices",
        "find-my-device",
        "automations",
    }

    context = None
    try:
        context = create_context(with_hardware=with_hardware)
        return handlers[args.command](args, context)
    except (ValueError, OSError, RuntimeError, ImportError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        if context is not None:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
