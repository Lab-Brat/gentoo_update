#!/bin/bash

set -e

### [done] Move these to python and pass them in where through cmdline (e.g. UPGRADE_MODE=$1)
# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE="${1}"
CONFIG_UPDATE_MODE="${2}"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
UPGRADE_LOG="${3}/upgrade-log_${TIMESTAMP}"


# ----------------- CREATE_LOG_DIRECTORY ----------------- #
if [[ ! -d "${3}" ]]; then
  mkdir "${3}"
  echo "Directory created: ${3}"
fi


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
		### Layman should be optional, not default - I'd split this list into "required_dependencies" and "optional_dependencies'
		### I'd actually not do this here at all and instead have these come from the ebuild that is requirement for this project :)
		"layman"
	)

	# Filter the programs that are not installed
	not_installed=()
	for program in "${programs[@]}"; do
		if ! command -v "${program}" >/dev/null 2>&1; then
			not_installed+=("${program}")
		fi
	done

	# Install the programs
	if [[ ${#not_installed[@]} -gt 0 ]]; then
		echo "Installing ${not_installed[@]}"
		### See comment about about moving this into the ebuild for this script. You also don't want this in unattended mode - you want to pass `--ask`
		emerge --verbose "${not_installed[@]}"
		echo "Installation completed."
	else
		echo "All dependencies are already installed."
	fi

}

# ------------------- SECURITY_UPDATES ------------------- #
function update_security() {
	# Check for GLSAs and install updates if necessary
	### Use long-form --list
	glsa=$(glsa-check -l affected)

	if [ -z "${glsa}" ]; then
		echo "No affected GLSAs found."
	else
		echo "Affected GLSAs found. Applying updates..."
		### Use long form --fix
		glsa-check -f affected | tee -a "${UPGRADE_LOG}"
		echo "Updates applied."
	fi
}

# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
	# Update main Portage tree
	echo "Syncing Portage Tree"
	### [done] Wrap all vars with braces: e.g. "${UPGRADE_REPORT}"
	emerge --sync | tee -a "${UPGRADE_LOG}"

	# Update layman overlays if layman is installed
	if command -v layman >/dev/null 2>&1; then
		echo "Syncting layman overlays"
		layman -S | tee -a "${UPGRADE_LOG}"
	fi

	# Update the eix cache if eix is installed
	if command -v eix >/dev/null 2>&1; then
		echo "Updating eix binary cache"
		eix-update | tee -a "${UPGRADE_LOG}"
	fi
}

# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
upgrade() {
    upgrade_mode=$UPGRADE_MODE
	local emerge_options="--update --newuse --deep --quiet-build y @world"
	local emerge_command="emerge --verbose ${emerge_options} --color y"

	if [[ "${upgrade_mode}" == 'skip' ]]; then
		echo "Running Upgrade: Skipping Errors"
		"${emerge_command}" | tee -a "${UPGRADE_LOG}"

	elif [[ "${upgrade_mode}" == 'safe' ]]; then
		echo "Running Upgrade: Check Pretend First"
		if emerge --pretend "${emerge_options}"; then
			echo "emerge pretend was successful, upgrading..."
			"${emerge_command}" | tee -a "${UPGRADE_LOG}"
		else
			echo "Command failed"
		fi
		
	elif [[ "${upgrade_mode}" == 'autofix' ]]; then
		echo "Running Upgrade: Full Upgrade"
		echo "Beep Beep Boop Bop"

	else
		echo "Invalid or undefined Upgrade Mode"
    exit 1
	fi
}

# ---------------- UPDATE_CONFIGURATIONS ----------------- #
function config_update() {
	### [done] Make it "${CONFIG_UPDATE_MODE} and add curly braces on the ones below"
	update_mode="${CONFIG_UPDATE_MODE}"

	# Perform the update based on the update mode
	if [[ "${update_mode}" == "merge" ]]; then
		dispatch-conf -a
	elif [[ "${update_mode}" == "preview" ]]; then
		dispatch-conf -p
	elif [[ "${update_mode}" == "interactive" ]]; then
		dispatch-conf
	else
		echo "Invalid update mode: ${update_mode}" >&2
		echo "Please set UPDATE_MODE to 'merge', 'preview', or 'interactive'." >&2
		exit 1
	fi
}

# ----------------------- CLEAN_UP ----------------------- #
function clean_up() {
	echo "Cleaning packages that are not part of the tree..."
	### This is something I think is dangerous to automate - it should go out as a notification to user to it themselves
	emerge --depclean | tee -a "${UPGRADE_LOG}"

	echo "Checking reverse dependencies..."
	revdep-rebuild | tee -a "${UPGRADE_LOG}"

	echo "Clean source code..."
	eclean -d distfiles | tee -a "${UPGRADE_LOG}"
}

# -------------------- CHECK_RESTART --------------------- #
function check_restart() {
	echo "Checking is any service needs a restart"
	### Use long-form option flags
	needrestart -r a | tee -a "${UPGRADE_LOG}"
}

# -------------- GET_IMPORTANT_LOG_MESSAGES -------------- #
function get_logs() {
	echo "Getting important logs"
	### Use long-form option flags
	elogv -p -t -l 1000 | tee -a "${UPGRADE_LOG}"
}

# ----------------------- GET_NEWS ----------------------- #
function get_news() {
	echo "Getting important news"
	### Use long-form option flags
	eselect news read new | tee -a "${UPGRADE_LOG}"
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
### [done] Right now this is more of an upgrade log than a report. A report is something we'd get after parsing the output to a summary or something like that
echo "Upgrade log can be found at: ${UPGRADE_LOG}"
