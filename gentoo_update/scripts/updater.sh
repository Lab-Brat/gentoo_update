#!/bin/bash

set -euo pipefail

# ---------------------- VARIABLES ----------------------- #
FUNCTION="${1}"
UPDATE_MODE="${2}"
UPDATE_FLAGS="${3}"
if [[ "${UPDATE_FLAGS}" == "NOARGS" ]]; then
    UPDATE_FLAGS=""
fi
CONFIG_UPDATE_MODE="${4}"
DAEMON_RESTART="${5}"
CLEAN="${6}"
READ_ELOGS="${7}"
READ_NEWS="${8}"

# ------------------- CHECK_DISK_USAGE ------------------- #
function check_disk_usage() {
    mount_point_found=false

    while read -r line; do
        if [[ "${line}" = \#* ]] || [[ -z "${line}" ]]; then
            continue
        fi

        mount_point=$(echo "${line}" | awk '{print $2}')

        if [[ ${mount_point} = "/tmp" || "${mount_point}" = "swap" || "${mount_point}" == "/boot/efi" ]]; then
            continue
        fi

        if [[ ! -d "${mount_point}" ]]; then
            echo "Warning: mount point ${mount_point} does not exist."
            continue
        fi

        mount_point_found=true

        df -h "${mount_point}" |
            awk -v OFS=", " 'NR==2 {print "Disk usage for " "'"${mount_point}"'"" ===> Total=" $2, "Used=" $3, "Free=" $4, "Percent used=" $5}'

    done </etc/fstab

    if [[ "${mount_point_found}" == false ]]; then
        df -h "/" |
            awk -v OFS=", " 'NR==2 {print "Disk usage for " "/"" ===> Total=" $2, "Used=" $3, "Free=" $4, "Percent used=" $5}'
    fi
}

function check_disk_usage_before_update() {
    echo -e "\n{{ CALCULATE DISK USAGE 1 }}\n"
    check_disk_usage
}

function check_disk_usage_after_update() {
    echo -e "\n{{ CALCULATE DISK USAGE 2 }}\n"
    check_disk_usage
}

# ------------------ SYNC_PORTAGE_TREE ------------------- #
function sync_tree() {
    echo -e "\n{{ SYNC PORTAGE TREE }}\n"

    # Update main Portage tree
    echo "Syncing Portage Tree"
    emerge --sync
}

# -------------------- UPDATE_SYSTEM --------------------- #
function get_update_packages_and_commands() {
    update_mode="${UPDATE_MODE}"
    update_flags="${UPDATE_FLAGS}"

    # Get a list of security patches or just use @world
    if [[ "${update_mode}" == 'security' ]]; then
        glsa=$(glsa-check --list --quiet affected)
        AFFECTED_PACKAGES=$(echo "${glsa}" | awk 'NF>1 {print $(NF-1)}' | paste -sd " " -)
        UPDATE_PRETEND_COMMAND="emerge --verbose --pretend --quiet-build --update ${update_flags} ${AFFECTED_PACKAGES}"
        UPDATE_COMMAND="emerge --verbose  --quiet-build --update ${update_flags} ${AFFECTED_PACKAGES}"

    elif [[ "${update_mode}" == 'full' ]]; then
        AFFECTED_PACKAGES='@world'
        UPDATE_PRETEND_COMMAND="emerge --verbose  --pretend --quiet-build --update --newuse --deep ${update_flags} ${AFFECTED_PACKAGES}"
        UPDATE_COMMAND="emerge --verbose --quiet-build --update --newuse --deep ${update_flags} ${AFFECTED_PACKAGES}"

    else
        echo "Invalid update mode, exiting...."
        exit 1
    fi
}
get_update_packages_and_commands

function emerge_pretend() {
    echo -e "\n{{ PRETEND EMERGE }}\n"

    # run emerge in pretend mode to detect some issues before updating
    update_mode="${UPDATE_MODE}"
    update_flags="${UPDATE_FLAGS}"
    affected_packages="${AFFECTED_PACKAGES}"

    if [ -n "${affected_packages}" ]; then
        echo "emerging with --pretend..."
        echo "Updating: ${affected_packages}"
        if eval "${UPDATE_PRETEND_COMMAND}"; then
            echo "emerge pretend was successful, updating..."
        else
            echo "emerge pretend has failed, exiting"
            exit 1
        fi
    else
        echo "There are no packages to update, skipping.."
    fi
}

function update() {
    echo -e "\n{{ UPDATE SYSTEM }}\n"

    affected_packages="${AFFECTED_PACKAGES}"

    if [ -n "${affected_packages}" ]; then
        echo "emerging..."
        echo "Updating: ${affected_packages}"
        echo "Update command:"
        echo "${UPDATE_COMMAND}"
        eval "${UPDATE_COMMAND}"
        echo "update was successful"

    else
        echo "There are no packages to update, skipping..."
    fi
}

# ---------------- UPDATE_CONFIGURATIONS ----------------- #
function config_update() {
    echo -e "\n{{ UPDATE SYSTEM CONFIGURATION FILES }}\n"

    update_mode="${CONFIG_UPDATE_MODE}"

    # Perform the update based on the update mode
    if [[ "${update_mode}" == "merge" ]]; then
        etc-update --automode -5
    elif [[ "${update_mode}" == "ignore" ]]; then
        echo "Ignoring configuration update for now..."
        echo "Please UPDATE IT MANUALLY LATER"
    else
        echo "Invalid update mode: ${update_mode}" >&2
        echo "Please set UPDATE_MODE to 'merge' or 'ignore'." >&2
    fi
}

# ----------------------- CLEAN_UP ----------------------- #
function clean_up() {
    echo -e "\n{{ CLEAN UP }}\n"

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
    echo -e "\n{{ RESTART SERVICES }}\n"

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
    echo -e "\n{{ READ ELOGS }}\n"

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
    echo -e "\n{{ READ NEWS }}\n"

    read_news="${READ_NEWS}"

    if [[ "${read_news}" == 'y' ]]; then
        echo "Getting important news"
        eselect news read new
    else
        echo "not reading news"
    fi
}

# --------------------- RUN_PROGRAM ---------------------- #
case ${FUNCTION} in
check_disk_usage_before_update)
    "$@"
    exit
    ;;
check_disk_usage_after_update)
    "$@"
    exit
    ;;
sync_tree)
    "$@"
    exit
    ;;
emerge_pretend)
    "$@"
    exit
    ;;
update)
    "$@"
    exit
    ;;
config_update)
    "$@"
    exit
    ;;
clean_up)
    "$@"
    exit
    ;;
check_restart)
    "$@"
    exit
    ;;
get_logs)
    "$@"
    exit
    ;;
get_news)
    "$@"
    exit
    ;;
esac
