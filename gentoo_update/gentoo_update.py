import os
import argparse
from typing import Tuple, List
from configparser import ConfigParser
from .shell_runner import ShellRunner
from .parser import Parser
from .reporter import Reporter
from .notifier import Notifier
from ._version import __version__

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
        default="",
        help="Additional arguments to be passed when in 'full' update mode.\n"
        "Example:\n"
        "--args 'quiet-build=n color=y keep-going'",
    )
    parser.add_argument(
        "-c",
        "--config-update-mode",
        default="ignore",
        choices=["ignore", "merge"],
        help="Set the way new configurations are handled after an update.\n"
        "Options:\n"
        "* ignore: do not update configuration files at all.\n"
        "* merge: automatically merge changes in configuration files.\n"
        "Default: ignore\n",
    )
    parser.add_argument(
        "-d",
        "--daemon-restart",
        action="store_true",
        help="Set whether to restart services and daemons after an update.\n",
    )
    parser.add_argument(
        "-e",
        "--clean",
        action="store_true",
        help="Set whether to clean orphaned packaged after an update.\n",
    )
    parser.add_argument(
        "-l",
        "--read-logs",
        action="store_true",
        help="Set whether to read elogs after an update.\n",
    )
    parser.add_argument(
        "-n",
        "--read-news",
        action="store_true",
        help="Set whether to read news after an update.\n",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not show logs on the terminal screen.\n",
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Show report or the last update log.\n",
    )
    parser.add_argument(
        "-s",
        "--send-report",
        default="none",
        choices=["irc", "email", "none"],
        help="Send update report via IRC bot or email (SendGrid).\n"
        "Default: none\n",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print updater version.\n",
    )

    args = parser.parse_args()
    return args


def make_conf_reader() -> ConfigParser:
    """
    Read /etc/portage/make.conf with configparser.

    Returns:
        configparser.ConfigParser: ConfigParser object.
    """
    config = ConfigParser()
    with open("/etc/portage/make.conf") as config_string:
        config.read_string("[DEFAULT]\n" + config_string.read())
    return config


def initiate_log_directory(make_conf) -> Tuple[str, List[str]]:
    """
    Create log directory if it does not exist.
    If PORTAGE_LOGDIR is not set, use the default directory.

    Returns:
        str: Log directory path.
        List[str]: List of messages to be logged.
    """
    try:
        log_dir = make_conf["DEFAULT"]["PORTAGE_LOGDIR"]
    except KeyError:
        log_dir = ""

    log_dir_messages = []
    if log_dir == "":
        log_dir = "/var/log/portage/gentoo-update"
        log_dir_messages.append(
            f"PORTAGE_LOGDIR not set, using default: {log_dir}"
        )
    else:
        log_dir = log_dir.replace('"', "")
        log_dir = f"{log_dir}/gentoo-update"
        log_dir_messages.append(f"PORTAGE_LOGDIR set, using: {log_dir}")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
        log_dir_messages.append(f"Created log directory: {log_dir}")

    return log_dir, log_dir_messages


def generate_last_report(log_dir: str) -> None:
    """
    Show report for the last log located in $PORTAGE_LOGDIR.

    Parameters:
        log_dir (str): Directory where gentoo_update stores logs.
    """
    files = os.listdir(log_dir)
    paths = [os.path.join(log_dir, basename) for basename in files]
    last_log = max(paths, key=os.path.getctime)
    update_info = Parser(last_log).extract_info_for_report()
    return Reporter(update_info)


def add_prefixes(args: str) -> str:
    """
    Function to add prefixes to a list of arguments passed to
    --update-mode full.

    Parameters:
    args_list (str): A string of space separated arguments without prefixes
        example: "quiet-build=n color=y keep-going"

    Returns:
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
    args = create_cli()

    make_conf = make_conf_reader()
    log_dir, log_dir_messages = initiate_log_directory(make_conf)

    if args.report:
        generate_last_report(log_dir).print_report()
    elif args.send_report in ["irc", "email"]:
        report = generate_last_report(log_dir).create_report()
        short = False if args.send_report == "email" else True
        Notifier(notification_type=args.send_report, report=report, short=short)
    else:
        runner = ShellRunner(
            "y" if args.quiet else "n", log_dir, log_dir_messages
        )
        runner.run_shell_script(
            args.update_mode,
            add_prefixes(args.args) if args.args else "NOARGS",
            "y" if args.config_update_mode else "n",
            "y" if args.daemon_restart else "n",
            "y" if args.clean else "n",
            "y" if args.read_logs else "n",
            "y" if args.read_news else "n",
        )


if __name__ == "__main__":
    main()
