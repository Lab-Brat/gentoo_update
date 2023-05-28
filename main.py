import os
import sys
import shlex
import logging
import subprocess
from datetime import datetime

current_path = os.path.dirname(os.path.realpath(__file__))

# Code review comments
### [done] Not all users will have bash - can we default to `sh`?
### [done] We need to exit with the same code as the result process once it finishes running
### [done] Use python logger - since we'll want to run this from cron, it will really help to have timestamps of all output


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


# Variable definitions
UPGRADE_MODE = "safe"
CONFIG_UPDATE_MODE = "ignore"
OPTIONAL_DEPENDENCIES = "true"
DAEMON_RESTART = "true"

# Run the updater
### Since you are running the updater from python, you should create the commandline options flags with help documentation in python and pass them all into the shell script
run_shell_script(
    f"{current_path}/updater.sh",
    UPGRADE_MODE,
    CONFIG_UPDATE_MODE,
    OPTIONAL_DEPENDENCIES,
    DAEMON_RESTART,
)
