### Gentoo Updater

`gentoo-update` is a tool that automates installing updates on Gentoo Linux. 
By default it only installs security updates from [GLSA](https://security.gentoo.org/glsa/), 
but it also provides support to update `@world`.  

This project 
[originates](https://wiki.gentoo.org/wiki/Google_Summer_of_Code/2023/Ideas/Automated_Gentoo_system_updater) 
from 2023 Google Summer of Code.


#### Usage
`gentoo-update` can be easily installed with pip (ebuild coming soon):
```bash
pip install gentoo_update
```

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
[readme](gentoo_update/blob/main/tests/README.md)
