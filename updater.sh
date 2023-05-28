#!/bin/sh

set -e

### [done] Move these to python and pass them in where through cmdline (e.g. UPGRADE_MODE=$1)
# ---------------------- VARIABLES ----------------------- #
UPGRADE_MODE="${1}"
CONFIG_UPDATE_MODE="${2}"
OPTIONAL_DEPENDENCIES="${3}"
DAEMON_RESTART="${4}"

# ----------------- INSTALL_DEPENDENCIES ----------------- #
function install_dependencies() {
	install_optional_dependencies=$OPTIONAL_DEPENDENCIES

	# List of programs that the updater will be using
	required_dependencies=(
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
	if [[ "${install_optional_dependencies}" == "y" ]]; then
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
		glsa-check --fix affected
		echo "Updates applied."
	fi
}

# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
	update_optional_dependencies=$OPTIONAL_DEPENDENCIES

	# Update main Portage tree
	echo "Syncing Portage Tree"
	### [done] Wrap all vars with braces: e.g. "${UPGRADE_REPORT}"
	emerge --sync

	if [[ "${update_optional_dependencies}" == 'y' ]]; then
		# Update layman overlays if layman is installed
		if command -v layman >/dev/null 2>&1; then
			echo "Syncting layman overlays"
			layman --sync-all
		fi

		# Update the eix cache if eix is installed
		if command -v eix >/dev/null 2>&1; then
			echo "Updating eix binary cache"
			eix-update
		fi
	fi
}

# ----------------- FULL_SYSTEM_UPGRADE ------------------ #
upgrade() {
	upgrade_mode=$UPGRADE_MODE
	local emerge_options="--update --newuse --deep --quiet-build y @world"

	if [[ "${upgrade_mode}" == 'skip' ]]; then
		echo "Running Upgrade: Skipping Errors"
		emerge --verbose --keep-going ${emerge_options} --color y

	elif [[ "${upgrade_mode}" == 'safe' ]]; then
		echo "Running Upgrade: Check Pretend First"
		if emerge --pretend ${emerge_options}; then
			echo "emerge pretend was successful, upgrading..."
			emerge --verbose ${emerge_options} --color y
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
		etc-update --automode -5
	elif [[ "${update_mode}" == "interactive" ]]; then
		etc-update
	elif [[ "${update_mode}" == "dispatch" ]]; then
		dispatch-conf
	elif [[ "${update_mode}" == "ignore" ]]; then
		echo "Ignoring configuration update for now..."
		echo "Please UPDATE IT MANUALLY LATER"
	else
		echo "Invalid update mode: ${update_mode}" >&2
		echo "Please set UPDATE_MODE to 'merge', 'interactive', 'dispatch' or 'ignore'." >&2
	fi
}

# ----------------------- CLEAN_UP ----------------------- #
function clean_up() {
	echo "Cleaning packages that are not part of the tree..."
	### This is something I think is dangerous to automate - it should go out as a notification to user to it themselves
	emerge --depclean

	echo "Checking reverse dependencies..."
	revdep-rebuild

	echo "Clean source code..."
	eclean --deep distfiles
}

# -------------------- CHECK_RESTART --------------------- #
function check_restart() {
	restart="${DAEMON_RESTART}"
	echo "Checking is any service needs a restart"
	if [[ "${restart}" == 'y' ]]; then
		### [done] Use long-form option flags <<< needrestart doesn't have a long-form option :(
		# automatically restart all services
		needrestart -r a
	else
		# list services that require a restart
		needrestart -r l
	fi
}

# ---------------------- GET_ELOGS ----------------------- #
function get_logs() {
	echo "Reading elogs"
	### Use long-form option flags <<< elogv can't be automated, will read logs manually
	elog_dir="/var/log/portage/elog"

	# Check if the elog directory exists
	if [[ ! -d "${elog_dir}" ]]; then
		echo "Elog directory does not exist."
		return
	fi

	current_time=$(date +%s)
	timeframe=24

	# Find and print elogs that have been modified in the last 24 hours
	find "${elog_dir}" -type f -mmin -$((60 * "${timeframe}")) -print0 |
		while IFS= read -r -d '' file; do
			modification_time=$(stat -c %Y "${file}")
			if ((modification_time > (current_time - 60 * 60 * 24))); then
				echo ""
				echo ">>> Log filename: ${file}"
				echo ">>> Log start <<<"
				cat "${file}"
				echo ">>> Log end <<<"
				echo ""
			fi
		done
}

# ----------------------- GET_NEWS ----------------------- #
function get_news() {
	echo "Getting important news"
	### [done] Use long-form option flags
	eselect news read new
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
