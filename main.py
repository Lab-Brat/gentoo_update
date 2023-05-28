import os
import subprocess

current_path = os.path.dirname(os.path.realpath(__file__))


def run_shell_script(script_path, *args):
    try:
        result = subprocess.run(
            ### [done] Not all users will have bash - can we default to `sh`?
            ["sh", script_path] + list(args),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ### We need to exit with the same code as the result process once it finishes running
        print(f"[Script Output] >> {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        ### Use python logger - since we'll want to run this from cron, it will really help to have timestamps of all output
        print(
            f"[Error] >>>>>>>>>> {script_path} exited with error code {e.returncode}]"
        )
        print(f"[Error Message] >> {e.stderr.decode()}")


# Variable definitions
UPGRADE_MODE = "safe"
CONFIG_UPDATE_MODE = "ignore"
UPGRADE_LOG_FILEPATH = "/var/log/gentoo_updater"
OPTIONAL_DEPENDENCIES = "true"
DAEMON_RESTART = "true"

# Run the updater
### Since you are running the updater from python, you should create the commandline options flags with help documentation in python and pass them all into the shell script
run_shell_script(
    f"{current_path}/updater.sh",
    UPGRADE_MODE,
    CONFIG_UPDATE_MODE,
    UPGRADE_LOG_FILEPATH,
    OPTIONAL_DEPENDENCIES,
    DAEMON_RESTART,
)
