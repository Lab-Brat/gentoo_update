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


#### Testing
**Note** Testing will be automated in the future, right now it's a bit hackish
In `gentoo_update/tests` there is a Docker Compose file that 
can be used for testing. It builds containers based on stage3 
tarballs and mounts the source code to `/root/gentoo_update_source`.  

Example of a test:
```bash
cd tests
docker compose up gentoo1 -d
docker exec -it tests-gentoo1-1 /bin/bash

# inside container
cd /root/gentoo_update_source
python gentoo_update.python
```

