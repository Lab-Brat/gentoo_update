import os
import argparse
from .shell_runner import ShellRunner
from typing import List

__version__ = "0.1.5"
current_path = os.path.dirname(os.path.realpath(__file__))


def create_cli() -> argparse.Namespace:
    """
    Define CLI command flags using argparse.

    Returns:
        parser.parse_args: Argparse commands
    """
    formatter = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        description="Automate updates on Gentoo Linux.",
        formatter_class=formatter,
    )

    parser.add_argument(
        "-m",
        "--update-mode",
        default="security",
        choices=["security", "full"],
        help="Set the update mode.\n"
        "Options:\n"
        "* security: update only security patches (GLSA)\n"
        "* full: do a full @world update\n"
        "Default: security\n",
    )
    parser.add_argument(
        "-a",
        "--args",
        nargs="*",
        help="Additional arguments to be passed when in 'full' update mode.",
    )
    parser.add_argument(
        "-c",
        "--config-update-mode",
        default="ignore",
        choices=["ignore", "merge", "interactive", "dispatch"],
        help="Set the way new configurations are handled after an update.\n"
        "Options:\n"
        "* ignore: do not update configuration files at all.\n"
        "* merge: automatically merge changes in configuration files.\n"
        "* interactive: launch interactive etc-upgrade.\n"
        "* dispatch: launch interactive dispatch-conf.\n"
        "Default: ignore\n",
    )
    parser.add_argument(
        "-d",
        "--daemon-restart",
        default="n",
        choices=["y", "n"],
        help="Set whether to restart services and daemons after an update.\n"
        "Default: n\n",
    )
    parser.add_argument(
        "-e",
        "--clean",
        default="n",
        choices=["y", "n"],
        help="Set whether to clean orphaned packaged after an update.\n"
        "Default: n\n",
    )
    parser.add_argument(
        "-l",
        "--read-logs",
        default="n",
        choices=["y", "n"],
        help="Set whether to read elogs after an update.\n" "Default: n\n",
    )
    parser.add_argument(
        "-n",
        "--read-news",
        default="n",
        choices=["y", "n"],
        help="Set whether to read news after an update.\n" "Default: n\n",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        default="n",
        choices=["y", "n"],
        help="Do not show logs on the terminal screen.\n" "Default: n\n",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print updater version.\n",
    )

    args = parser.parse_args()
    return args


def add_prefixes(args_list: List[str]) -> List[str]:
    """
    Function to add prefixes to a list of arguments passed to
    --update-mode full.

    Parameters:
    args_list (List[str]): A list of arguments without prefixes,
        example: v quiet-build=y

    Returns:
    List[str]: A new list of arguments with added prefixes,
        example: -v --quiet-build=y
    """
    prefixed_args = []

    for arg in args_list:
        if len(arg) == 1:
            prefixed_args.append("-" + arg)
        else:
            prefixed_args.append("--" + arg)

    return prefixed_args


def main() -> None:
    args = create_cli()
    runner = ShellRunner(args.quiet)

    runner.run_shell_script(
        args.update_mode,
        " ".join(add_prefixes(args.args)) if args.args else "NOARGS",
        args.config_update_mode,
        args.daemon_restart,
        args.clean,
        args.read_logs,
        args.read_news,
    )


if __name__ == "__main__":
    main()
