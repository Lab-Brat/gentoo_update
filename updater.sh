#!/bin/bash

set -e

### [done] Move these to python and pass them in where through cmdline (e.g. UPGRADE_MODE=$1)
# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE="${1}"
CONFIG_UPDATE_MODE="${2}"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
UPGRADE_LOG="${3}/upgrade-log_${TIMESTAMP}"
OPTIONAL_DEPENDENCIES="${4}"

# ----------------- CREATE_LOG_DIRECTORY ----------------- #
if [[ ! -d "${3}" ]]; then
	mkdir "${3}"
	echo "Directory created: ${3}"
fi

# ----------------- INSTALL_DEPENDENCIES ----------------- #
function install_dependencies() {
	install_optional_dependencies=$OPTIONAL_DEPENDENCIES

	# List of programs that the updater will be using
	required_dependencies=(
		"elogv"
		"needrestart"
		"gentoolkit" # "eclean", "euse", "equery"
		"glsa-check"
		### [done] Layman should be optional, not default - I'd split this list into "required_dependencies" and "optional_dependencies'
		### I'd actually not do this here at all and instead have these come from the ebuild that is requirement for this project :)
	)

	optional_dependencies=(
		"eix"
		"layman"
	)

	# Combine required and optional dependencies if needed
	if [[ "${install_optional_dependencies}" == "true" ]]; then
		all_dependencies=(
			"${required_dependencies[@]}"
			"${optional_dependencies[@]}"
		)
	else
		all_dependencies="${required_dependencies[@]}"
	fi

	# Filter the programs that are not installed
	not_installed=()
	for dependency in "${all_dependencies[@]}"; do
		if ! command -v "${dependency}" >/dev/null 2>&1; then
			not_installed+=("${dependency}")
		fi
	done

	# Install the programs
	if [[ ${#not_installed[@]} -gt 0 ]]; then
		echo "Installing ${not_installed[@]}"
		### See comment about about moving this into the ebuild for this script. You also don't want this in unattended mode - you want to pass `--ask`
		emerge --verbose --quiet-build y "${not_installed[@]}"
		echo "Installation completed."
	else
		echo "All dependencies are already installed."
	fi

}

# ------------------- SECURITY_UPDATES ------------------- #
function update_security() {
	# Check for GLSAs and install updates if necessary
	### [done] Use long-form --list
	glsa=$(glsa-check --list affected)

	if [ -z "${glsa}" ]; then
		echo "No affected GLSAs found."
	else
		echo "Affected GLSAs found. Applying updates..."
		### [done] Use long form --fix
		glsa-check --fix affected | tee --append "${UPGRADE_LOG}"
		echo "Updates applied."
	fi
}

# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
	update_optional_dependencies=$OPTIONAL_DEPENDENCIES

	# Update main Portage tree
	echo "Syncing Portage Tree"
	### [done] Wrap all vars with braces: e.g. "${UPGRADE_REPORT}"
	emerge --sync | tee --append "${UPGRADE_LOG}"

	if [[ "${update_optional_dependencies}" == 'true' ]]; then
		# Update layman overlays if layman is installed
		if command -v layman >/dev/null 2>&1; then
			echo "Syncting layman overlays"
			layman --sync-all | tee --append "${UPGRADE_LOG}"
		fi

		# Update the eix cache if eix is installed
		if command -v eix >/dev/null 2>&1; then
			echo "Updating eix binary cache"
			eix-update | tee --append "${UPGRADE_LOG}"
		fi
	fi
}

# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
upgrade() {
	upgrade_mode=$UPGRADE_MODE
	local emerge_options="--update --newuse --deep --quiet-build y @world"

	if [[ "${upgrade_mode}" == 'skip' ]]; then
		echo "Running Upgrade: Skipping Errors"
		emerge --verbose --keep-going ${emerge_options} --color y | tee --append "${UPGRADE_LOG}"

	elif [[ "${upgrade_mode}" == 'safe' ]]; then
		echo "Running Upgrade: Check Pretend First"
		if emerge --pretend ${emerge_options}; then
			echo "emerge pretend was successful, upgrading..."
			emerge --verbose ${emerge_options} --color y | tee --append "${UPGRADE_LOG}"
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
		etc-update --automode -5 | tee --append "${UPGRADE_LOG}"
	elif [[ "${update_mode}" == "interactive" ]]; then
		etc-update
	elif [[ "${update_mode}" == "dispatch" ]]; then
		dispatch-conf
	elif [[ "${update_mode}" == "ignore" ]]; then
		echo "Ignoring configuration update for now..." | tee --append "${UPGRADE_LOG}"
		echo "Please UPDATE IT MANUALLY LATER" | tee --append "${UPGRADE_LOG}"
	else
		echo "Invalid update mode: ${update_mode}" >&2 | tee --append "${UPGRADE_LOG}"
		echo "Please set UPDATE_MODE to 'merge', 'interactive', 'dispatch' or 'ignore'." >&2
	fi
}

# ----------------------- CLEAN_UP ----------------------- #
function clean_up() {
	echo "Cleaning packages that are not part of the tree..."
	### This is something I think is dangerous to automate - it should go out as a notification to user to it themselves
	emerge --depclean | tee --append "${UPGRADE_LOG}"

	echo "Checking reverse dependencies..."
	revdep-rebuild | tee --append "${UPGRADE_LOG}"

	echo "Clean source code..."
	eclean --deep distfiles | tee --append "${UPGRADE_LOG}"
}

# -------------------- CHECK_RESTART --------------------- #
function check_restart() {
	echo "Checking is any service needs a restart"
	### [done] Use long-form option flags <<< needrestart doesn't have a long-form option :(
	needrestart -r a | tee --append "${UPGRADE_LOG}"
}

# -------------- GET_IMPORTANT_LOG_MESSAGES -------------- #
function get_logs() {
	echo "Getting elogs"
	### Use long-form option flags <<< elogv can't be automated, will read logs manually
	# elogv -p -t -l 1000 | tee --append "${UPGRADE_LOG}"
}

# ----------------------- GET_NEWS ----------------------- #
function get_news() {
	echo "Getting important news"
	### [done] Use long-form option flags
	eselect news read new | tee --append "${UPGRADE_LOG}"
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
