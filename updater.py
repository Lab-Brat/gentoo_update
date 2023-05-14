import os

current_path = os.path.dirname(os.path.realpath(__file__))

# Step 1: Ensure that dependencies are installed
os.system(f"{current_path}/bash_scripts/dependencies.sh")

