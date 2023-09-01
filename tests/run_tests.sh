#!/bin/bash

set -euo pipefail

# ---------------------- VARIABLES ----------------------- #
INSTALL_METHOD="${1}"
UPDATE_MODE="${2}"
SHOW_REPORT="${3:-n}"
SEND_REPORT="${4:-n}"

# --------------------- TEST SCRIPT ---------------------- #
install_gentoo_update() {
    # Install ebuild from GURU repository
    if [[ "${INSTALL_METHOD}" == 'ebuild' ]]; then
        echo "app-admin/gentoo_update ~amd64" >>/etc/portage/package.accept_keywords/gentoo_update
        emerge --quiet-build y app-admin/gentoo_update

    # Install python package from PyPi
    elif [[ "${INSTALL_METHOD}" == 'pip' ]]; then
        pip install gentoo_update --break-system-packages

    # Install python pacakge from source
    elif [[ "${INSTALL_METHOD}" == 'source' ]]; then
        cd /root/gentoo_update_source && pip install . --break-system-packages

    else
        echo "Invalid installation method"
        exit 1

    fi
}

run_gentoo_update() {
    # Update GLSA only
    if [[ "${UPDATE_MODE}" == 'security' ]]; then
        gentoo-update

    # Update @world
    elif [[ "${UPDATE_MODE}" == 'full' ]]; then
        gentoo-update --update-mode full

    # Update @world with all flags
    elif [[ "${UPDATE_MODE}" == 'full_with_all_opts' ]]; then
        gentoo-update --update-mode full \
            --config-update-mode merge \
            --daemon-restart \
            --clean \
            --read-logs \
            --read-news

    else
        echo "Invalid update mode"
        exit 1

    fi
}

show_update_report() {
    # print the update report
    if [[ "${SHOW_REPORT}" == 'y' ]]; then
        gentoo-update --report
    else
        echo "Not printing report"
    fi
}

send_report() {
    # send report via irc, email or mobile
    if [[ "${SEND_REPORT}" != 'n' ]]; then
        gentoo-update --send-report "${SEND_REPORT}"
    else
        echo "Not sending report"
    fi
}

install_gentoo_update
run_gentoo_update
show_update_report
send_report
