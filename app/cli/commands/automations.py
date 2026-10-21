import argparse
import time
import uuid

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)
from app.models.device_event import DeviceEvent, DeviceEventType


def configure_parser(commands: argparse._SubParsersAction) -> None:
    parser = commands.add_parser(
        "automations",
        help="Manage and run USB-triggered automations",
    )
    actions = parser.add_subparsers(dest="automation_action", required=True)

    actions.add_parser("list", help="List configured automations")

    add = actions.add_parser("add", help="Create an automation")
    add.add_argument("name")
    add.add_argument(
        "--when",
        choices=("connected", "disconnected"),
        required=True,
        help="Run when the configured USB device connects or disconnects",
    )
    add.add_argument("--device", required=True, help="Saved device ID or Windows device ID")
    add.add_argument("--display", help="Display ID to switch")
    add.add_argument("--input", dest="input_id", help="Target display input ID")
    add.add_argument(
        "--do-nothing",
        action="store_true",
        help="Create a placeholder automation without a switch action",
    )
    add.add_argument("--disabled", action="store_true")

    delete = actions.add_parser("delete", help="Delete an automation")
    delete.add_argument("automation_id")

    toggle = actions.add_parser("enable", help="Enable an automation")
    toggle.add_argument("automation_id")
    disable = actions.add_parser("disable", help="Disable an automation")
    disable.add_argument("automation_id")

    watch = actions.add_parser(
        "watch",
        help="Monitor USB devices and run enabled automations",
    )
    watch.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)",
    )


def handle(args: argparse.Namespace, context) -> int:
    automations = context.repository.load_automations()

    if args.automation_action == "list":
        if not automations:
            print("No automations configured.")
            return 0
        for automation in automations:
            trigger = automation.trigger.type.value.removeprefix("device_")
            status = "enabled" if automation.enabled else "disabled"
            print(
                f"{automation.id}: {automation.name} [{status}] "
                f"when device {automation.trigger.device_id} {trigger}"
            )
            for action in automation.actions:
                if action.type == ActionType.SWITCH_INPUT:
                    print(f"  switch {action.display_id} to {action.input_id}")
                else:
                    print("  do nothing")
        return 0

    if args.automation_action == "add":
        if not args.name.strip():
            raise ValueError("Automation name cannot be empty.")
        configured_devices = context.usb_service.get_configured_devices()
        device = _find_device(configured_devices, args.device)
        if args.do_nothing:
            if args.display or args.input_id:
                raise ValueError("--do-nothing cannot be combined with --display or --input.")
            action = Action(type=ActionType.DO_NOTHING)
        else:
            if not args.display or not args.input_id:
                raise ValueError("Specify both --display and --input, or use --do-nothing.")
            display = next(
                (item for item in context.display_service.get_displays()
                 if item.id == args.display),
                None,
            )
            if display is None:
                raise ValueError(f"Display not found: {args.display}")
            if args.input_id not in {item.input_id for item in display.inputs}:
                raise ValueError(
                    f"Input {args.input_id} is not supported by {display.name}."
                )
            action = Action(
                type=ActionType.SWITCH_INPUT,
                display_id=display.id,
                input_id=args.input_id,
            )

        automation = Automation(
            id=_next_automation_id(automations),
            name=args.name.strip(),
            enabled=not args.disabled,
            trigger=Trigger(
                type=(
                    TriggerType.DEVICE_CONNECTED
                    if args.when == "connected"
                    else TriggerType.DEVICE_DISCONNECTED
                ),
                device_id=device.windows_device_id,
            ),
            actions=[action],
        )
        automations.append(automation)
        context.repository.save_automations(automations)
        print(f"Created automation {automation.id}: {automation.name}.")
        return 0

    if args.automation_action in {"enable", "disable", "delete"}:
        automation = next(
            (item for item in automations if item.id == args.automation_id),
            None,
        )
        if automation is None:
            raise ValueError(f"Automation not found: {args.automation_id}")
        if args.automation_action == "delete":
            automations.remove(automation)
            print(f"Deleted automation {automation.id}.")
        else:
            automation.enabled = args.automation_action == "enable"
            print(
                f"{'Enabled' if automation.enabled else 'Disabled'} "
                f"automation {automation.id}."
            )
        context.repository.save_automations(automations)
        return 0

    if args.interval <= 0:
        raise ValueError("Polling interval must be greater than zero.")
    _watch_devices(context, args.interval)
    return 0


def _find_device(devices, reference: str):
    for device in devices:
        if device.id == reference or device.windows_device_id == reference:
            return device
    raise ValueError(f"Saved USB device not found: {reference}")


def _next_automation_id(automations) -> str:
    existing = {automation.id for automation in automations}
    index = 1
    while f"automation-{index:03d}" in existing:
        index += 1
    return f"automation-{index:03d}"


def _watch_devices(context, interval: float) -> None:
    current_ids = {
        device.windows_device_id
        for device in context.usb_monitor.get_devices()
    }
    print("Monitoring USB devices. Press Ctrl+C to stop.")
    try:
        while True:
            next_ids = {
                device.windows_device_id
                for device in context.usb_monitor.get_devices()
            }
            for device_id in sorted(next_ids - current_ids):
                context.automation_service.handle_device_event(
                    DeviceEvent(device_id, DeviceEventType.CONNECTED)
                )
                print(f"Connected: {device_id}")
            for device_id in sorted(current_ids - next_ids):
                context.automation_service.handle_device_event(
                    DeviceEvent(device_id, DeviceEventType.DISCONNECTED)
                )
                print(f"Disconnected: {device_id}")
            current_ids = next_ids
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped monitoring.")
