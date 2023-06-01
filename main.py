import os
import sys
import shlex
import logging
import argparse
import subprocess
from datetime import datetime

current_path = os.path.dirname(os.path.realpath(__file__))


def create_logger():
    """
    Creates a logger with two handlers: terminal output and file output.
    Both handlers have the same logging level (INFO) and share the same formatter.
    The formatter includes timestamp, log level, and the log message.

    Returns:
        logging.Logger: Configured logger.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_filename = f"/var/log/gentoo_updater/log_{timestamp}"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    formater = logging.Formatter(
        "[%(asctime)s %(levelname)s] ::: %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    terminal_handler.setFormatter(formater)
    file_handler.setFormatter(formater)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)

    return logger


def run_shell_script(script_path, *args):
    """
    Run a shell script and stream standard output and standard error
    to terminal and a log file.

    Args:
        script_path (str): Shell script path.
        *args (str): Arguments for the shell script.
                     They need to be handled by the script.
    """
    logger = create_logger()
    command = shlex.split(f"sh {script_path} {' '.join(args)}")
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as p:
        for line in p.stdout:
            logger.info(line.decode().rstrip("\n"))
        p.wait()
        if p.returncode != 0:
            logger.error(f"{script_path} exited with error code {p.returncode}")
            sys.exit(p.returncode)


# Run the updater
def create_cli():
    parser = argparse.ArgumentParser(
        description="Automate updates on Gentoo Linux."
    )

    parser.add_argument(
        "-m",
        "--upgrade-mode",
        default="safe",
        choices=["skip", "safe", "autofix"],
        help="Set the upgrade mode. Default: safe",
    )
    parser.add_argument(
        "-c",
        "--config-update-mode",
        default="ignore",
        choices=["ignore", "merge", "interactive", "dispatch"],
        help="Set the way new configuration are handled after an update. Default: ignore",
    )
    parser.add_argument(
        "-o",
        "--optional-dependencies",
        default="n",
        choices=["y", "n"],
        help="Set whether to install optional dependencies. Default: n",
    )
    parser.add_argument(
        "-d",
        "--daemon-restart",
        default="n",
        choices=["y", "n"],
        help="Set whether to restart services and daemons after an update. Default: n",
    )
    parser.add_argument(
        "-e",
        "--clean",
        default="n",
        choices=["y", "n"],
        help="Set wether to clean orphaned packaged after an update. Default: n",
    )

    args = parser.parse_args()
    return args


def main():
    args = create_cli()

    run_shell_script(
        f"{current_path}/updater.sh",
        args.upgrade_mode,
        args.config_update_mode,
        args.optional_dependencies,
        args.daemon_restart,
        args.clean,
    )


if __name__ == "__main__":
    main()
