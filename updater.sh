#!/bin/bash

set -e

# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE=${GENTOO_UPDATE_MODE:-safe}
CONFIG_UPDATE_MODE=${GENTOO_UPDATE_CONFIG_MODE:-merge}
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

	if [ -z "$glsa" ]; then
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
	if command -v layman >/dev/null 2>&1; then
		echo "Syncting layman overlays"
		layman -S | tee -a "$UPGRADE_REPORT"
	fi

	# Update the eix cache if eix is installed
	if command -v eix >/dev/null 2>&1; then
		echo "Updating eix binary cache"
		eix-update | tee -a "$UPGRADE_REPORT"
	fi
}

# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
upgrade() {
  upgrade_mode=$UPGRADE_MODE
	local emerge_options="--update --newuse --deep --quiet-build y @world"
	local emerge_command="emerge --verbose $emerge_options --color y"

	if [[ $upgrade_mode == 'skip' ]]; then
		echo "Running Upgrade: Skipping Errors"
		$emerge_command | tee -a "$UPGRADE_REPORT"
	elif [[ $upgrade_mode == 'safe' ]]; then
		echo "Running Upgrade: Check Pretend First"
		if emerge --pretend $emerge_options; then
			echo "emerge pretend was successful, upgrading..."
			$emerge_command | tee -a "$UPGRADE_REPORT"
		else
			echo "Command failed"
		fi
	elif [[ $upgrade_mode == 'autofix' ]]; then
		echo "Running Upgrade: Full Upgrade"
		echo "Beep Beep Boop Bop"
	else
		echo "Invalid or undefined Upgrade Mode"
    exit 1
	fi
}

# ---------------- UPDATE_CONFIGURATIONS ----------------- #
function config_update() {
	update_mode=$CONFIG_UPDATE_MODE

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

# ----------------------- CLEAN_UP ----------------------- #
function clean_up() {
	echo "Cleaning packages that are not part of the tree..."
	emerge --depclean | tee -a $UPGRADE_REPORT

	echo "Checking reverse dependencies..."
	revdep-rebuild | tee -a $UPGRADE_REPORT

	echo "Clean source code..."
	eclean -d distfiles | tee -a $UPGRADE_REPORT
}

# -------------------- CHECK_RESTART --------------------- #
function check_restart() {
	echo "Checking is any service needs a restart"
	needrestart | tee -a $UPGRADE_REPORT
}

# -------------- GET_IMPORTANT_LOG_MESSAGES -------------- #
function get_logs() {
	echo "Getting important logs"
	elogv -p -t -l 1000 | tee -a $UPGRADE_REPORT
}

# ----------------------- GET_NEWS ----------------------- #
function get_news() {
	echo "Getting important news"
	eselect news read new | tee -a $UPGRADE_REPORT
}

# --------------------- RUN_PROGRAM ---------------------- #
install_dependencies
update_security
sync_tree
upgrade
config_update
clean_up
check_restart
get_logs
get_news

echo "Upgrade complete!"
echo "Upgrade report can be found at: $UPGRADE_REPORT"
