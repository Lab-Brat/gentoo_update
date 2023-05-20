#!/bin/bash

# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE='safe'
CONFIG_UPDATE_MODE='merge'
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
UPGRADE_REPORT="./_logs/upgrade_report$TIMESTAMP"
echo "Upgrade Report: $UPGRADE_REPORT"


# ----------------- INSTALL_DEPENDENCIES ----------------- #
function install_dependencies() {
    # List of programs that the updater will be using
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
    
    # Install the programs
    if [[ ${#not_installed[@]} -gt 0 ]]; then
        echo "Installing ${not_installed[@]}"
        emerge --verbose "${not_installed[@]}"
        echo "Installation completed."
    else
        echo "All dependencies are already installed."
    fi

}


# ------------------- SECURITY_UPDATES ------------------- #
function update_security() {
    # Check for GLSAs and install updates if necessary
    glsa=$(glsa-check -l affected)
    
    if [ -z "$glsa" ]
    then
    	echo "No affected GLSAs found."
    else
    	echo "Affected GLSAs found. Applying updates..."
    	glsa-check -f affected | tee -a "$UPGRADE_REPORT"
    	echo "Updates applied."
    fi
}


# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
    # Update main Portage tree
    echo "Syncing Portage Tree"
    emerge --sync | tee -a "$UPGRADE_REPORT"
    
    # Update layman overlays if layman is installed
    if command -v layman >/dev/null 2>&1 ; then
	echo "Syncting layman overlays"
        layman -S | tee -a "$UPGRADE_REPORT"
    fi
    
    # Update the eix cache if eix is installed
    if command -v eix >/dev/null 2>&1 ; then
	echo "Updating eix binary cache"
        eix-update | tee -a "$UPGRADE_REPORT"
    fi
}


# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
function upgrade() {
    # Update @world
    if [[ $UPGRADE_MODE == 'skip' ]]; then
	echo "Running Upgrade: Skipping Errors"
        emerge  --verbose --update --newuse --deep \
		--keep-going --color y @world | \
		tee -a "$UPGRADE_REPORT"
    elif [[ $UPGRADE_MODE == 'safe' ]]; then
	echo "Running Upgrade: Check Pretend First"
	emerge  --verbose --update --newuse --deep \
		--pretend --color y @world | \
		tee -a "$UPGRADE_REPORT"
	# re-run if pretend didn't find any errors
    elif [[ $UPGRADE_MODE == 'autofix' ]]; then
	echo "Running Upgrade: Full Upgrade"
	# parse errors and try to fix them
	echo "Beep Beep Boop Bop"
    else 
	echo "Invalid Upgrade Mode"
    fi
}


# ---------------- UPDATE_CONFIGURATIONS ----------------- #
function config_update() {
  update_mode=${CONFIG_UPDATE_MODE:-merge}
  
  # Perform the update based on the update mode
  if [[ "$update_mode" == "merge" ]]; then
      dispatch-conf -a
  elif [[ "$update_mode" == "preview" ]]; then
      dispatch-conf -p
  elif [[ "$update_mode" == "interactive" ]]; then
      dispatch-conf
  else
      echo "Invalid update mode: $update_mode" >&2
      echo "Please set UPDATE_MODE to 'merge', 'preview', or 'interactive'." >&2
      exit 1
  fi
}


# --------------------- RUN_PROGRAM ---------------------- #
install_dependencies
update_security
sync_tree
upgrade
config_update
