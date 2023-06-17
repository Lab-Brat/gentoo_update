### Gentoo Updater

`gentoo-update` is a tool that automates updates on Gentoo Linux. 
By default it only installs security updates from [GLSA](https://security.gentoo.org/glsa/), 
but it can also be used to update all packages on the system. i.e. `@world`.  

This project 
[originates](https://wiki.gentoo.org/wiki/Google_Summer_of_Code/2023/Ideas/Automated_Gentoo_system_updater) 
from 2023 Google Summer of Code.


#### Usage
`gentoo-update` is in [GURU](https://wiki.gentoo.org/wiki/Project:GURU) 
overlay, and can be installed using `emerge`. But because the project is 
in early stage of development it's not considered stable and is masked by 
`~amd64`. To unmask and install it, run:
```bash
echo 'app-admin/gentoo_update ~amd64' >> /etc/portage/package.accept_keywords/gentoo_update
emerge --ask app-admin/gentoo_update
```

Alternatively, updater can be installed with pip:
```
pip install gentoo_update --break-system-packages
```

The updater will not display build logs by default, so it's recommended to 
define `PORTAGE_LOGDIR` in `/etc/portage/make.conf`. If this option is defined, 
updater will use it to store it's own logs as well.  


Here are some usage examples:
* Basic security update
```bash
gentoo-update
```

* Full system update with extra update parameters
```bash
gentoo-update --update-mode full --args color=n
```

* Full system update, show elogs and news
```bash
gentoo-update --update-mode full --read-logs y --read-news y
```

The detailed explanation of command flags can be found in `--help`.  
Information on testing can be found in tests directory 
[readme](tests/README.md)
