import os


current_path = os.path.dirname(os.path.realpath(__file__))

def update_safe_mode():
    try:
        os.system(f"{current_path}/bash_scripts/glsa-check.sh")
        # Continue processing the result...
    except RuntimeError as e:
        print(e)
        # Handle the error...

def updater():
    os.system(f"{current_path}/bash_scripts/dependencies.sh")
    update_safe_mode()

