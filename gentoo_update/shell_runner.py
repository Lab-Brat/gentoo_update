import os
import sys
import shlex
import logging
import subprocess
from configparser import ConfigParser
from datetime import datetime
from typing import Tuple, List


class ShellRunner:
    def __init__(self, quiet: str) -> None:
        self.quiet = True if quiet == "y" else False

        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.make_conf = self.make_conf_reader()
        self.log_dir, self.log_dir_messages = self.initiate_log_directory()
        self.log_filename = f"{self.log_dir}/log_{self.timestamp}"
        self.logger = self.initiate_logger()

        self.script_dir = os.path.join(os.path.dirname(__file__), "scripts")
        self.script_path = os.path.join(self.script_dir, "updater.sh")

    def make_conf_reader(self) -> ConfigParser:
        """
        Read /etc/portage/make.conf with configparser.

        Returns:
            configparser.ConfigParser: ConfigParser object.
        """
        config = ConfigParser()
        with open("/etc/portage/make.conf") as config_string:
            config.read_string("[DEFAULT]\n" + config_string.read())
        return config

    def initiate_log_directory(self) -> Tuple[str, List[str]]:
        """
        Create log directory if it does not exist.
        If PORTAGE_LOGDIR is not set, use the default directory.

        Returns:
            str: Log directory path.
            List[str]: List of messages to be logged.
        """
        try:
            log_dir = self.make_conf["DEFAULT"]["PORTAGE_LOGDIR"]
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

    def initiate_logger(self) -> logging.Logger:
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
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formater = logging.Formatter(
            "[%(asctime)s %(levelname)s] ::: %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
        )

        if not self.quiet:
            terminal_handler = logging.StreamHandler()
            terminal_handler.setLevel(logging.INFO)
            terminal_handler.setFormatter(formater)
            logger.addHandler(terminal_handler)

        file_handler = logging.FileHandler(self.log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formater)
        logger.addHandler(file_handler)

        for message in self.log_dir_messages:
            logger.info(message)

        return logger

    def _log_stream_output(
        self, stream_obj: subprocess.Popen, type: str
    ) -> List[str]:
        """
        Process sterr from the upadte script.

        Args:
            stream: output stream from subprocess.Popen
            type: output type, stderr or stdout
        Returns:
            List[str]: List containing the output
        """
        output = []
        if type == "stdout":
            stream = stream_obj.stdout
        elif type == "stderr":
            stream = stream_obj.stderr
        else:
            self.logger.error("Invalid Output Stream Type")

        for line in stream:
            line = line.decode().rstrip("\n")
            output.append(line)
            if type == "stdout":
                self.logger.info(line)
            elif type == "stderr":
                self.logger.error(line)
        return output

    def _exit_with_error_message(self, stream: subprocess.Popen) -> None:
        """
        Exit runner if updater.sh encounters an error and
        print/log that error.

        Args:
            stream: output stream from subprocess.Popen
            stderr_output:
        """
        error_message = (
            "updater.sh exited with error code {script_stream.returncode}"
        )
        if self.stderr_output:
            stderr_output_message = "n".join(self.stderr_output)
            error_message += (
                f"\nStandard error output:\n{stderr_output_message}"
            )
        self.logger.error(error_message)
        sys.exit(stream.returncode)

    def run_shell_script(self, *args: str) -> None:
        """
        Run a shell script and stream standard output
        and standard error to terminal and a log file.

        Args:
            script_path (str): Shell script path.
            *args (str): Arguments for the shell script.
                         They need to be handled by the script.
        """
        command = shlex.split(f"{self.script_path} {' '.join(args)}")
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as script_stream:
            self.stdout_output = self._log_stream_output(
                script_stream, "stdout"
            )
            self.stderr_output = self._log_stream_output(
                script_stream, "stderr"
            )
            script_stream.wait()

            if script_stream.returncode != 0:
                self._exit_with_error_message(script_stream)

        final_message = f"gentoo-update is done! Log:file: {self.log_filename}"
        self.logger.info(final_message)
        if self.quiet:
            print(final_message)

    def __del__(self) -> None:
        """
        Closed all file handlers after ShellRunner is closed.
        """
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
