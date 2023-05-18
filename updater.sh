#!/bin/bash

# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE='safe'


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
    	glsa-check -f affected
    	echo "Updates applied."
    fi
}


# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
    # Update main Portage tree
    echo "Syncing Portage Tree"
    emerge --sync
    
    # Update layman overlays if layman is installed
    if command -v layman >/dev/null 2>&1 ; then
	echo "Syncting layman overlays"
        layman -S
    fi
    
    # Update the eix cache if eix is installed
    if command -v eix >/dev/null 2>&1 ; then
	echo "Updating eix binary cache"
        eix-update
    fi
}


# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
function upgrade() {
    # Update @world
    if [[ $UPGRADE_MODE == 'skip' ]]; then
	echo "Running Upgrade: Skipping Errors"
        emerge  --verbose --update --newuse --deep \
		--keep-going @world
    elif [[ $UPGRADE_MODE == 'safe' ]]; then
	echo "Running Upgrade: Check Pretend First"
	emerge  --verbose --update --newuse --deep \
		--pretend @world
	# re-run if pretend didn't find any errors
    elif [[ $UPGRADE_MODE == 'autofix' ]]; then
	echo "Running Upgrade: Full Upgrade"
	# parse errors and try to fix them
	echo "Beep Beep Boop Bop"
    else 
	echo "Invalid Upgrade Mode"
    fi
}


# --------------------- RUN_PROGRAM ---------------------- #
install_dependencies
update_security
sync_tree
upgrade

