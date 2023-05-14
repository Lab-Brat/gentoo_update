#!/bin/bash

# List of programs to install
programs=(
"elogv"
"emaint"
"eclean"
"needrestart"
"euse"
"equery"
"eix"
"glsa-check"
"layman"
)

# Filter the programs that are not installed
not_installed=()
for program in "${programs[@]}"; do
  if ! command -v "$program" >/dev/null 2>&1; then
    not_installed+=("$program")
  fi
done

# Install the programs using a single emerge command
if [[ ${#not_installed[@]} -gt 0 ]]; then
  emerge --verbose "${not_installed[@]}"
  echo "Installation completed."
else
  echo "All dependencies are already installed."
fi

