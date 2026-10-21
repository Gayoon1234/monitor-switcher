import argparse


def configure_parser(commands: argparse._SubParsersAction) -> None:
    parser = commands.add_parser("settings", help="View or change app settings")
    actions = parser.add_subparsers(dest="settings_action", required=True)
    actions.add_parser("show", help="Show available CLI-compatible settings")
    theme = actions.add_parser("theme", help="Select the theme used by the desktop UI")
    theme.add_argument("name", nargs="?", help="Theme name; omit to list themes")


def handle(args: argparse.Namespace, context) -> int:
    service = context.theme_service
    if args.settings_action == "show":
        print(f"Active theme: {service.get_active_theme()}")
        print(f"Available themes: {', '.join(service.get_theme_names())}")
        print("The theme setting is used by the desktop UI.")
        return 0

    if args.name is None:
        print(f"Active theme: {service.get_active_theme()}")
        print(f"Available themes: {', '.join(service.get_theme_names())}")
        return 0

    service.set_active_theme(args.name)
    print(f"Theme set to {service.get_active_theme()}.")
    return 0
