#!/bin/bash

set -euo pipefail

# ---------------------- VARIABLES ----------------------- #
UPDATE_MODE="${1}"
UPDATE_FLAGS="${2}"
if [[ "${UPDATE_FLAGS}" == "NOARGS" ]]; then
	UPDATE_FLAGS=""
fi
CONFIG_UPDATE_MODE="${3}"
DAEMON_RESTART="${4}"
CLEAN="${5}"
READ_ELOGS="${6}"
READ_NEWS="${7}"

# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
	# Update main Portage tree
	echo "Syncing Portage Tree"
	emerge --sync
}

# -------------------- UPDATE_SYSTEM --------------------- #
function update_security() {
	# Check for GLSAs and install updates if necessary
	glsa=$(glsa-check --list affected)

	if [ -z "${glsa}" ]; then
		echo "No affected GLSAs found."
	else
		echo "Affected GLSAs found. Applying updates..."
		glsa-check --fix affected
		echo "Updates applied."
	fi
}

function update_full() {
	# Do a full system update
	IFS=' ' read -r -a update_flags <<<"${UPDATE_FLAGS}"

	echo "Running Update: Check Pretend First"
	if emerge --pretend --update --newuse --deep @world; then
		echo "emerge pretend was successful, updating..."
		emerge --verbose --quiet-build y \
			--update --newuse --deep "${update_flags[@]}" @world
	else
		echo "emerge pretend has failed, not updating"
	fi
}

function update() {
	update_mode="${UPDATE_MODE}"
	# Do security updates or full system updates
	if [[ "${update_mode}" == 'security' ]]; then
		echo -e "installing security updates only\n"
		update_security
		echo ""

	elif [[ "${update_mode}" == 'full' ]]; then
		echo -e "updating @world\n"
		update_full
		echo ""

	else
		echo "Invalid update mode, exiting...."
		exit 1
	fi
}

# ---------------- UPDATE_CONFIGURATIONS ----------------- #
function config_update() {
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
	clean="${CLEAN}"
	if [[ "${clean}" == 'y' ]]; then
		echo "Cleaning packages that are not part of the tree..."
		emerge --depclean

		if command -v revdep-rebuild >/dev/null 2>&1; then
			echo "Checking reverse dependencies..."
			revdep-rebuild

			echo "Clean source code..."
			eclean --deep distfiles
		else
			echo "app-portage/gentoolkit is not installed"
		fi

	else
		echo "Clean up is not enabled."
	fi
}

# -------------------- CHECK_RESTART --------------------- #
function check_restart() {
	restart="${DAEMON_RESTART}"

	if command -v needrestart >/dev/null 2>&1; then
		echo "Checking is any service needs a restart"
		if [[ "${restart}" == 'y' ]]; then
			# automatically restart all services
			needrestart -r a
		else
			# list services that require a restart
			needrestart -r l
		fi
	else
		echo "app-admin/needrestart is not installed"
	fi
}

# ---------------------- GET_ELOGS ----------------------- #
function read_elogs() {
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

function get_logs() {
	read_elogs="${READ_ELOGS}"
	if [[ "${read_elogs}" == 'y' ]]; then
		echo "reading elogs"
		read_elogs
	else
		echo "not reading elogs"
	fi
}

# ----------------------- GET_NEWS ----------------------- #
function get_news() {
	read_news="${READ_NEWS}"
	if [[ "${read_news}" == 'y' ]]; then
		echo "Getting important news"
		eselect news read new
	else
		echo "not reading news"
	fi
}

# --------------------- RUN_PROGRAM ---------------------- #
echo -e "{{ SYNC PORTAGE TREE }}\n"
sync_tree

echo -e "{{ UPDATE SYSTEM }}\n"
update
echo ""

echo -e "\n{{ UPDATE SYSTEM CONFIGURATION FILES }}\n"
config_update
echo ""

echo -e "\n{{ CLEAN UP }}\n"
clean_up
echo ""

echo -e "\n{{ RESTART SERVICES }}\n"
check_restart
echo ""

echo -e "\n{{ READ ELOGS }}\n"
get_logs
echo ""

echo -e "\n{{ READ NEWS }}\n"
get_news
echo -e "\n"
