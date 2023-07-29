#!/bin/bash

set -euo pipefail

emerge_install() {
    # Install from GURU repository
    echo "app-admin/gentoo_update ~amd64" >>/etc/portage/package.accept_keywords/gentoo_update
    emerge --quiet-build y app-admin/gentoo_update
}

pip_install() {
    # Install with pip
    cd /root/gentoo_update_source && pip install . --break-system-packages
}

pypi_install() {
    # Install with pip from PyPi
    pip install gentoo_update --break-system-packages
}

sec_update() {
    # Run the gentoo-update in secure mode
    gentoo-update
}

full_update() {
    # Run the gentoo-update in full update mode
    gentoo-update --update-mode full
}

full_update_all_options() {
    # Run the gentoo-update in full update mode and all options enabled
    gentoo-update --update-mode full \
        --config-update-mode merge \
        --daemon-restart \
        --clean \
        --read-logs \
        --read-news
}

"$@"
