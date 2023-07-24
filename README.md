### Gentoo Updater

`gentoo-update` is a tool that automates updates on Gentoo Linux. 
By default it only installs security updates from [GLSA](https://security.gentoo.org/glsa/), 
but it can also be used to update all packages on the system. i.e. `@world`.  

This project 
[originates](https://wiki.gentoo.org/wiki/Google_Summer_of_Code/2023/Ideas/Automated_Gentoo_system_updater) 
from 2023 Google Summer of Code, more about it can be found in the 
[blog post](https://labbrat.net/blog/gsoc2023/gentoo_update_intro/) and 
[Gentoo Forums](https://forums.gentoo.org/viewtopic-p-8793827.html#8793827).  

**TLDR**: `gentoo_update` has 3 main modules - updater, parser and notifier. Updater runs the 
update script and create a log file. Parser reads the log file and composes a post-upgrade 
report which notifier then sends via email or IRC chat.

<br>

#### Features
- updater:
    - [x] detect and patch security updates by default using glsa-check
    - [x] update `@world`
    - [x] insert additional flags to `@world` update 
    - [x] calculate disk usage before and after the update
    - [ ] do not start the update if available disk space is lower than a certain threshold
- parser:
    - [x] Compose a report that informs if the update was successful or not
    - [x] Add package info after successful info, like updated packages, new versions and USE flags
    - [ ] Detect different errors during an update
        - [x] Blocked Packages
        - [ ] USE flag conflicts
        - [ ] Issues with Licenses
        - [ ] Network issues during an update
        - [ ] OOM during an update
    - [x] Add disk usage before/after an update to the report
- notifier:
    - [x] Send update report via IRC bot
    - [ ] Send full report via IRC bot if requested
    - [x] Send update report via email using SendGrid
    - [ ] Send update report via email using local relay
- Other:
    - [x] Add an ebuild to GURU repository
    - [ ] Create a CI/CD pipeline that will run `gentoo_update` on newly published stage3 Docker containers

<br>

#### Usage
`gentoo-update` is in [GURU](https://wiki.gentoo.org/wiki/Project:GURU) 
overlay, and can be installed using `emerge`:
```bash
emerge --ask app-admin/gentoo_update
```

Alternatively, it can be installed with pip in a virtual environment:
```bash
python -m venv gentoo_update
source gentoo_update/bin/activate
python -m pip install gentoo_update
```

The updater creates a subdirectory in Portage's default `PORTAGE_LOGDIR` located at `/var/log/portage/gentoo-update`. 
However, if this variable is set to a different value in `make.conf`, it will use the new location instead of the default.  

Here are some usage examples:
* Basic security update
```bash
gentoo-update
```

* Full system update with extra update parameters
```bash
gentoo-update --update-mode full --args "color=y keep-going"
```

* Full system update, show elogs and news
```bash
gentoo-update --update-mode full --read-logs --read-news
```

* Reading last update report (currently only successful update report):
```bash
gentoo-update --report
```

* Send the last update report via IRC bot
```bash
export IRC_CHANNEL="#<irc_channel_name>"
export IRC_BOT_NICKNAME="<bot_name>"
export IRC_BOT_PASSWORD="<bot_password>"
gentoo-update --send-report irc
```

The detailed explanation of command flags can be found in `--help`.  
Information on testing can be found in tests directory 
[readme](tests/README.md)
