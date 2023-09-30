# Testing

## Unit Test

There is a simple unit test that can be run by installing
`gentoo_update` in a virtual environment and running:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install .
python tests/test_updater.py
```

## Docker Test

`compose.yaml` can be used for testing. It builds containers based on stage3
tarballs and runs a tests script (`tests/run_tests.sh`) on it.  

Before running tests, make sure you have the directory to store logs:
**NOTE** All commands below are run from `tests` directory

```bash
mkdir logs
```

After a test is complete, the update log will be placed there which can be inspected.
Test Examples:

```bash
# build an openrc base image 
# install gentoo_update with pip from source and run full update
docker compose up gentoo_update_world_source

# build an old (08-05-2023) openrc desktop image,
# install gentoo_update from source and install only security updates
docker compose up gentoo_update_glsa_source
```
