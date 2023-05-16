#!/bin/bash

# Update main Portage tree
emerge --sync

# Update layman overlays if layman is installed
if command -v layman >/dev/null 2>&1 ; then
    layman -S
fi

# Update the eix cache if eix is installed
if command -v eix >/dev/null 2>&1 ; then
    eix-update
fi

