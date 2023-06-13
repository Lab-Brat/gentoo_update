#!/bin/bash

emerge_install() {
    # Install from GURU repository
    echo "app-admin/gentoo_update ~amd64" >> /etc/portage/package.accept_keywords/gentoo_update
    emerge --quiet-build y app-admin/gentoo_update
}

pip_install() {
    # Install with pip
    cd /root/gentoo_update_source && pip install . --break-system-packages
}

sec_update() {
    # Run the gentoo-update in secure mode
    gentoo-update
}

full_update() {
    # Run the gentoo-update in full update mode
    gentoo-update -m full
}

"$@"

