"""Automate updates on Gentoo Linux.

This module provides a command-line interface for automating updates on
Gentoo Linux.
It defines CLI command flags using argparse and provides functions for
reading make.conf, creating log directories, and generating reports.
"""

import argparse
import os
import sys
from typing import Dict, List, Tuple

from ._version import __version__
from .notifier import Notifier
from .parser import Parser
from .reporter import Reporter
from .shell_runner import ShellRunner

current_path = os.path.dirname(os.path.realpath(__file__))
sys.tracebacklimit = -1


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

    subparsers = parser.add_subparsers(dest="command")
    update = subparsers.add_parser("update", help="Run security or full update.")
    report = subparsers.add_parser("report", help="Generate or send update reports.")
    version = subparsers.add_parser("version", help="Print gentoo-update version.")

    # define update subparser
    update.add_argument(
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
    update.add_argument(
        "-a",
        "--args",
        default="",
        help="""
Additional arguments to be passed when in 'full' update mode.
Example:
--args 'quiet-build=n color=y keep-going'
""",
    )
    update.add_argument(
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
    update.add_argument(
        "-u",
        "--disk-usage-limit",
        default="0",
        help="""
Do not run update if available disk space is lower than a limit (in GB).
Default: 0 - do not set a limit.
""",
    )
    update.add_argument(
        "-d",
        "--daemon-restart",
        action="store_true",
        help="Set whether to restart services and daemons after an update.",
    )
    update.add_argument(
        "-e",
        "--clean",
        action="store_true",
        help="Set whether to clean orphaned packaged after an update.",
    )
    update.add_argument(
        "-l",
        "--read-logs",
        action="store_true",
        help="Set whether to read elogs after an update.",
    )
    update.add_argument(
        "-n",
        "--read-news",
        action="store_true",
        help="Set whether to read news after an update.",
    )
    update.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not show logs on the terminal screen.",
    )

    # define report subparser
    report.add_argument(
        "-r",
        "--report",
        nargs="?",
        const="LAST",
        default=None,
        help="Show report. By default shows report from the last update log.",
    )
    report.add_argument(
        "-o",
        "--last-n-logs",
        type=int,
        help="Show last n log filenames.",
    )
    report.add_argument(
        "-s",
        "--send-report",
        default="none",
        choices=["irc", "email", "mobile", "none"],
        help="""
Send update report via IRC bot, email (SendGrid) or mobile app.
Default: none
""",
    )
    report.add_argument(
        "-t",
        "--short-report",
        action="store_true",
        help="Show or send only update status without package info.",
    )

    # define version subparser
    version.add_argument("-v", "--verbose", action="store_true")

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


def show_available_reports(log_dir: str, last_n_logs: int) -> None:
    """Short last n reports in the log directory.

    Args
    ----
        log_dir (str): Directory where gentoo_update stores logs.
        last_n_logs (int): Last n amount of reports in the directory.
    """
    log_filesnames = os.listdir(log_dir)
    log_filesnames.sort()
    if len(log_filesnames) < last_n_logs:
        raise ValueError(f"There are less than {last_n_logs} in {log_dir}")

    if not log_filesnames:
        raise ValueError(f"No log files found in the directory {log_dir}")

    logs = log_filesnames[-last_n_logs:]
    print(f"The last {last_n_logs} log file filenames")
    for log in logs:
        print(log)


def generate_report(
    log_dir: str, log_filename: str = None, short_report: bool = False
) -> Reporter:
    """Show report for the <log_filename> located in $PORTAGE_LOGDIR.

    Args
    ----
        log_dir (str): Directory where gentoo_update stores logs.
        log_filename (str, optional): File name of the update log.
                Defaults to the latest log if not provided.
        short_report (bool): Short report format.

    Returns
    -------
        Reporter: Object containing the update report information.
    """
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"The log directory {log_dir} does not exist")

    if log_filename is None:
        files = os.listdir(log_dir)
        paths = [
            os.path.join(log_dir, basename)
            for basename in files
            if basename[0:4] == "log_"
        ]
        if not paths:
            raise ValueError(f"No log files found in the directory {log_dir}")
        full_log_path = max(paths, key=os.path.getctime)
    else:
        full_log_path = os.path.join(log_dir, log_filename)

        if not os.path.exists(full_log_path):
            raise FileNotFoundError(
                f"The log file {log_filename} does not exist in {log_dir}"
            )

    update_info = Parser(full_log_path).extract_info_for_report()
    return Reporter(update_info, short_report)


def main() -> None:
    """Execute it all."""
    args = create_cli()

    make_conf = make_conf_reader()
    log_dir, log_dir_messages = initiate_log_directory(make_conf)

    if args.command == "version":
        if args.verbose:
            print(f"gento-update version: {__version__}")
        else:
            print(__version__)
    elif args.command == "update":
        runner = ShellRunner("y" if args.quiet else "n", log_dir, log_dir_messages)
        runner.run_shell_script(
            args.update_mode,
            args.args if args.args else "NOARGS",
            args.disk_usage_limit,
            args.config_update_mode,
            "y" if args.daemon_restart else "n",
            "y" if args.clean else "n",
            "y" if args.read_logs else "n",
            "y" if args.read_news else "n",
        )
    elif args.command == "report":
        if args.last_n_logs:
            show_available_reports(log_dir, args.last_n_logs)
        elif args.send_report in ["irc", "email", "mobile"]:
            log_filename = None if args.report == "LAST" else args.report
            report = generate_report(
                log_dir, log_filename, args.short_report
            ).create_report()
            short = False if args.send_report != "irc" else True
            Notifier(notification_type=args.send_report, report=report, short=short)
        else:
            log_filename = None if args.report == "LAST" else args.report
            report = generate_report(log_dir, log_filename, args.short_report)
            report.print_report()


if __name__ == "__main__":
    main()
