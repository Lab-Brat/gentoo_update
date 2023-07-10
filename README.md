### Gentoo Updater

`gentoo-update` is a tool that automates updates on Gentoo Linux. 
By default it only installs security updates from [GLSA](https://security.gentoo.org/glsa/), 
but it can also be used to update all packages on the system. i.e. `@world`.  

This project 
[originates](https://wiki.gentoo.org/wiki/Google_Summer_of_Code/2023/Ideas/Automated_Gentoo_system_updater) 
from 2023 Google Summer of Code, more about it can be found in the 
[blog post](https://labbrat.net/blog/gsoc2023/gentoo_update_intro/) and 
[Gentoo Forums](https://forums.gentoo.org/viewtopic-p-8793827.html#8793827).  


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
gentoo-update --update-mode full --read-logs y --read-news y
```

* Reading last update report (currently only successful update report):
```bash
gentoo-update --report
```

The detailed explanation of command flags can be found in `--help`.  
Information on testing can be found in tests directory 
[readme](tests/README.md)
