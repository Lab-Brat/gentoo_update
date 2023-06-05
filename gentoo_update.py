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
    Create a logger with two handlers:
        1. terminal output
        2. file output
    Both handlers have the same logging level (INFO)
    and share the same formatter.
    Formatters include timestamp, log level and the message.

    Returns:
        logging.Logger: Configured logger.
        log_filename: Log filename.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_dir = "/var/log/gentoo_update"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filename = f"{log_dir}/log_{timestamp}"

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

    return logger, log_filename


def run_shell_script(*args):
    """
    Run a shell script and stream standard output
    and standard error to terminal and a log file.

    Args:
        script_path (str): Shell script path.
        *args (str): Arguments for the shell script.
                     They need to be handled by the script.
    """
    logger, log_file = create_logger()
    command = shlex.split(f"updater.sh {' '.join(args)}")
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as script_stream:
        # Process stdout
        for line in script_stream.stdout:
            logger.info(line.decode().rstrip("\n"))

        # Process stderr
        stderr_output = []
        for line in script_stream.stderr:
            line = line.decode().rstrip("\n")
            stderr_output.append(line)
            logger.error(line)

        script_stream.wait()

        if script_stream.returncode != 0:
            error_message = (
                "updater.sh exited with error code {script_stream.returncode}"
            )
            if stderr_output:
                stderr_output_message = "n".join(stderr_output)
                error_message += (
                    f"\nStandard error output:\n{stderr_output_message}"
                )
            logger.error(error_message)
            sys.exit(script_stream.returncode)
    logger.info("gentoo_update completed it's tasks!")
    logger.info(f"log file can be found at: {log_file}")


def create_cli():
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
        help="Set wether to clean orphaned packaged after an update.\n"
        "Default: n\n",
    )
    parser.add_argument(
        "-l",
        "--read-logs",
        default="n",
        choices=["y", "n"],
        help="Set wether to read elogs after an update.\n" "Default: n\n",
    )
    parser.add_argument(
        "-n",
        "--read-news",
        default="n",
        choices=["y", "n"],
        help="Set wether to read news after an update.\n" "Default: n\n",
    )

    args = parser.parse_args()
    return args


def add_prefixes(args_list):
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


def main():
    args = create_cli()

    run_shell_script(
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
