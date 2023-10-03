"""Automate updates on Gentoo Linux.

This module provides a command-line interface for automating updates on
Gentoo Linux.
It defines CLI command flags using argparse and provides functions for
reading make.conf, creating log directories, and generating reports.
"""

import argparse
import os
from typing import Dict, List, Tuple

from ._version import __version__
from .notifier import Notifier
from .parser import Parser
from .reporter import Reporter
from .shell_runner import ShellRunner

current_path = os.path.dirname(os.path.realpath(__file__))


def create_cli() -> argparse.Namespace:
    """Define CLI command flags using argparse.

    Returns
    -------
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
        help="""
Set the update mode.
Options:
* security: update only security patches (GLSA)
* full: do a full @world update
Default: security
""",
    )
    parser.add_argument(
        "-a",
        "--args",
        default="",
        help="""
Additional arguments to be passed when in 'full' update mode.
Example:
--args 'quiet-build=n color=y keep-going'
""",
    )
    parser.add_argument(
        "-c",
        "--config-update-mode",
        default="ignore",
        choices=["ignore", "merge"],
        help="""
Set the way new configurations are handled after an update.
Options:
* ignore: do not update configuration files at all.
* merge: automatically merge changes in configuration files.
Default: ignore
""",
    )
    parser.add_argument(
        "-u",
        "--disk-usage-limit",
        default="0",
        help="""
Do not run update if available disk space is lower than a limit (in GB).
Default: 0 - do not set a limit.
""",
    )
    parser.add_argument(
        "-d",
        "--daemon-restart",
        action="store_true",
        help="Set whether to restart services and daemons after an update.",
    )
    parser.add_argument(
        "-e",
        "--clean",
        action="store_true",
        help="Set whether to clean orphaned packaged after an update.",
    )
    parser.add_argument(
        "-l",
        "--read-logs",
        action="store_true",
        help="Set whether to read elogs after an update.",
    )
    parser.add_argument(
        "-n",
        "--read-news",
        action="store_true",
        help="Set whether to read news after an update.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not show logs on the terminal screen.",
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Show report or the last update log.",
    )
    parser.add_argument(
        "-s",
        "--send-report",
        default="none",
        choices=["irc", "email", "mobile", "none"],
        help="""
Send update report via IRC bot, email (SendGrid) or mobile app.
Default: none
""",
    )
    parser.add_argument(
        "-t",
        "--short-report",
        action="store_true",
        help="Show or send only update status without package info.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print updater version.",
    )

    args = parser.parse_args()
    return args


def make_conf_reader() -> Dict:
    """Read /etc/portage/make.conf.

    Returns
    -------
        Dict: Parameters in the key:value format.
        Example: {'COMMON_FLAGS': '"-O2 -pipe"'}
    """
    make_conf = {}
    with open("/etc/portage/make.conf", encoding="utf-8") as make_conf_raw:
        lines = make_conf_raw.read().splitlines()
    key, value = None, []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue
        if "=" in line_stripped:
            if key:
                make_conf[key] = " ".join(value)
            parts = line_stripped.split("=", 1)
            key = parts[0].strip()
            value = [parts[1].strip()]
        else:
            value.append(line_stripped)
    if key:
        make_conf[key] = " ".join(value)
    return make_conf


def initiate_log_directory(make_conf) -> Tuple[str, List[str]]:
    """Create log directory if it does not exist.

    If PORTAGE_LOGDIR is not set, use the default directory.

    Returns
    -------
        str: Log directory path.
        List[str]: List of messages to be logged.
    """
    try:
        log_dir = make_conf["PORTAGE_LOGDIR"].replace('"', "")
    except KeyError:
        log_dir = ""

    log_dir_messages = []
    if log_dir == "":
        log_dir = "/var/log/portage/gentoo-update"
        log_dir_messages.append(f"PORTAGE_LOGDIR not set, using default: {log_dir}")
    else:
        log_dir = log_dir.replace('"', "")
        log_dir = f"{log_dir}/gentoo-update"
        log_dir_messages.append(f"PORTAGE_LOGDIR set, using: {log_dir}")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        log_dir_messages.append(f"Created log directory: {log_dir}")

    return log_dir, log_dir_messages


def generate_last_report(log_dir: str, short_report: bool) -> None:
    """Show report for the last log located in $PORTAGE_LOGDIR.

    Args:
    ----
        log_dir (str): Directory where gentoo_update stores logs.
        short_report (bool): Short report format.

    """
    files = os.listdir(log_dir)
    paths = [os.path.join(log_dir, basename) for basename in files]
    last_log = max(paths, key=os.path.getctime)
    update_info = Parser(last_log).extract_info_for_report()
    return Reporter(update_info, short_report)


def add_prefixes(args: str) -> str:
    """Add prefixes to a list of arguments passed to --update-mode full.

    Args:
    ----
    args (str): A string of space separated arguments without prefixes
        example: "quiet-build=n color=y keep-going"

    Returns:
    -------
    str: A new string of space separated arguments with added prefixes,
        example: "--quiet-build=n --color=y --keep-going"
    """
    args = args.split(" ")
    prefixed_args = []

    for arg in args:
        if len(arg) == 1:
            prefixed_args.append("-" + arg)
        else:
            prefixed_args.append("--" + arg)
    return " ".join(prefixed_args)


def main() -> None:
    """Execute it all."""
    args = create_cli()

    make_conf = make_conf_reader()
    log_dir, log_dir_messages = initiate_log_directory(make_conf)

    if args.report:
        generate_last_report(log_dir, args.short_report).print_report()
    elif args.send_report in ["irc", "email", "mobile"]:
        report = generate_last_report(log_dir, args.short_report).create_report()
        short = False if args.send_report != "irc" else True
        Notifier(notification_type=args.send_report, report=report, short=short)
    else:
        runner = ShellRunner("y" if args.quiet else "n", log_dir, log_dir_messages)
        runner.run_shell_script(
            args.update_mode,
            add_prefixes(args.args) if args.args else "NOARGS",
            args.disk_usage_limit,
            args.config_update_mode,
            "y" if args.daemon_restart else "n",
            "y" if args.clean else "n",
            "y" if args.read_logs else "n",
            "y" if args.read_news else "n",
        )


if __name__ == "__main__":
    main()
