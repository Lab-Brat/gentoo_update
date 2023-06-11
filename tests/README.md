### Testing
**Note** Testing will be automated in the future, right now it's a bit hackish.

#### Unit Test
Initialize a virtual environment in the parent directory to run unit tests. 
For example:
```
python -m venv venv
source venv/bin/activate
python tests/test_updater.py
```

#### Docker Test
`compose.yaml` can be used for testing. It builds containers based on stage3 
tarballs and mounts the source code to `/root/gentoo_update_source`.  

Example of a test:
```bash
docker compose up gentoo1 -d
docker exec -it tests-gentoo1-1 /bin/bash

# inside container
cd /root/gentoo_update_source
pip install . --break-system-packages
```
