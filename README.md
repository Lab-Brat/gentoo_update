# Gentoo Updater

`gentoo-update` is a tool that automates updates on Gentoo Linux.
By default it only installs security updates from [GLSA](https://security.gentoo.org/glsa/),
but it can also be used to update all packages on the system, i.e. `@world`.

This project
[originates](https://wiki.gentoo.org/wiki/Google_Summer_of_Code/2023/Ideas/Automated_Gentoo_system_updater)
from 2023 Google Summer of Code, more about it can be found in the
[blog post](https://blogs.gentoo.org/gsoc/2023/08/27/final-report-automated-gentoo-system-updater/) and
[Gentoo Forums](https://forums.gentoo.org/viewtopic-p-8793827.html#8793827).

`gentoo-update` has 3 main modules - updater, parser and notifier. Updater runs the
update script and creates a log file. Parser reads the log file and composes a post-upgrade
report which notifier then sends via email, IRC bot or
[mobile app](https://github.com/Lab-Brat/gentoo_update_flutter).

<details>

<summary>Feature List</summary>

- **updater**
  - [x] update security patches from GLSA by default, and optionally update `@world`
  - [x] insert additional flags to `@world` update
  - [x] do not start the update if available disk space is lower than a certain threshold
  - [ ] estimate update time
  - [ ] show package list before the update
  - [ ] control Portage niceness
- **parser**
  - [x] show update status (success/failure) in the report
  - [x] show package info after successful update: ebuilds, blocks, uninstalls etc.
  - [ ] detect different errors during an update
    - [x] blocked packages
    - [ ] USE flag conflicts
    - [ ] issues with Licenses
    - [ ] network issues during an update
    - [ ] OOM during an update
  - [x] show disk usage before/after an update
- **notifier**
  - [x] send update report via IRC bot
  - [x] send update report via email using SendGrid
  - [x] send update report via email using local relay
  - [x] send update report via mobile app
  - [x] send a short report with only the update status instead of a full report
- **general**
  - [x] CLI: add option to choose from which log file to generate a report
  - [ ] CLI: add emoji to console output like in k3s
  - [ ] use configuration file to configure the app (see #28)
  - [ ] export report in machine readible output (JSON, YAML, TOML)
  - [ ] run update on a filesystem snapshot (see #33)
  - [ ] comprehensive set of unit tests (test coverage > 50%)

</details>

## Installation

`gentoo-update` is in [GURU](https://wiki.gentoo.org/wiki/Project:GURU)
overlay, and can be installed using `emerge`. First, enable the overlay:

```bash
emerge --ask app-eselect/eselect-repository
eselect repository enable guru
emerge --sync
```

All packages in GURU overlay must have `~arch` keyword, more on it in
`The Regulations` section in the [documentation](https://wiki.gentoo.org/wiki/Project:GURU).
For example, on amd64 architecture it can be added via:

```bash
echo 'app-admin/gentoo_update ~amd64' > /etc/portage/package.accept_keywords/gentoo_update
```

and then install it:

```bash
emerge --ask app-admin/gentoo_update
```

Alternatively, it can be installed with pip in a virtual environment:

```bash
python -m venv gentoo_update
source gentoo_update/bin/activate
python -m pip install gentoo_update
```

## Usage

The updater creates a subdirectory in Portage's default `PORTAGE_LOGDIR` located at `/var/log/portage/gentoo-update`.
However, if this variable is set to a different value in `make.conf`, it will use the new location instead of the default.

Here are some usage examples:

- Basic security update

```bash
gentoo-update update
```

- Full system update with extra update parameters

```bash
gentoo-update update -m full -a "--color=y --keep-going --exclude=glibc"
```

- Full system update, show elogs and news

```bash
gentoo-update update -m full -l -n
```

- Read last update report:

```bash
gentoo-update report
```

- Show the last 3 logs filenames, and generate a report for one of it:

```shell
# gentoo-update report -o 3
The last 3 log file filenames
log_2023-09-23-09-19
log_2023-10-02-20-19
log_2023-10-07-13-14
# gentoo-update report -r log_2023-10-02-20-19
==========> Gentoo Update Report <==========
update status: SUCCESS
......
```

- Send the last update report to an IRC channel:

```bash
export IRC_CHANNEL="#<irc_channel_name>"
export IRC_BOT_NICKNAME="<bot_name>"
export IRC_BOT_PASSWORD="<bot_password>"
gentoo-update report -s irc
```

- Send the last update report via email (SendGrid API):

```bash
# install Sengrid library
# need to unmask these packages: dev-python/sendgrid, dev-python/python-http-client, dev-python/starkbank-ecdsa
emerge --ask dev-python/sendgrid

# export token and other info via env variables
export SENDGRID_TO='<to_address>'
export SENDGRID_FROM='<from_address>'
export SENDGRID_API_KEY='<api_key>'

# send the latest report, or a specific one
gentoo-update report -s email
gentoo-update report -r <log_name> -s email
```

- Send the last update report via email (local relay):

```bash
echo -e "Subject: Gentoo Update Report\n\n$(gentoo-update report)" | msmtp -a default <target-email>@gmail.com
```

> ℹ️  In this example `msmtp` is used, I wrote a small blog post showing how can it be set up,
> you can find it [here](https://labbrat.net/blog/send_emails_from_terminal/).
> But any other tool can be used, such as `mail`, `mailx`, `sendmail` and even `postfix`.

## Help

The detailed explanation of command flags can be found in CLI's help message:

```bash
gentoo-update --help
```

Information on testing can be found in tests directory [readme](tests/README.md).

To get help or request additional features feel free to create an issue in this GitHub repo.
Or just contact me directly via email at [labbrat_social@pm.me](mailto:labbrat_social@pm.me) or on IRC.
I am in most of the #gentoo IRC groups and my nick there is #LabBrat.
