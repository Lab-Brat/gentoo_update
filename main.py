import os
import subprocess

current_path = os.path.dirname(os.path.realpath(__file__))


def run_bash_script(script_path):
    try:
        result = subprocess.run(
            ["bash", script_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"[Script Output] >> {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        print(
            f"[Error] >>>>>>>>>> {script_path} exited with error code {e.returncode}]"
        )
        print(f"[Error Message] >> {e.stderr.decode()}")


# Run the updater
run_bash_script(f"{current_path}/updater.sh")

