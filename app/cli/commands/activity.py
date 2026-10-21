import argparse


def configure_parser(commands: argparse._SubParsersAction) -> None:
    parser = commands.add_parser("activity", help="View or clear activity history")
    actions = parser.add_subparsers(dest="activity_action", required=True)
    listing = actions.add_parser("list", help="Show recent activity")
    listing.add_argument(
        "--days",
        default="30",
        help="History range in days, or 'all' (default: 30)",
    )
    clear = actions.add_parser("clear", help="Delete all saved activity")
    clear.add_argument("--yes", action="store_true", help="Skip confirmation")


def handle(args: argparse.Namespace, context) -> int:
    if args.activity_action == "list":
        days = None if args.days.lower() == "all" else int(args.days)
        events = context.activity_repository.load(days)
        if not events:
            print("No activity found.")
            return 0
        for event in events:
            status = "succeeded" if event.success else "failed"
            print(
                f"{event.timestamp:%Y-%m-%d %H:%M:%S} "
                f"[{status}] {event.event_type}: {event.message}"
            )
        return 0

    if not args.yes:
        answer = input("Delete all saved activity logs? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 0
    context.activity_repository.clear()
    print("Activity history cleared.")
    return 0
