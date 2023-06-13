### Testing

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
tarballs and runs a tests script (`tests/run_tests.sh`) on it.  

Before running tests, make sure you have the directory to store logs:
```bash
mkdir ./tests/logs
```
After a test is complete, the update log will be placed there which can be inspected.  
Test Examples:
```bash
# build a systemd base images, install gentoo-update with pip and run full update
cd tests
docker compose up gentoo1_source -d

# build an openrc desktop image, install gentoo-update from GURU repo and run security update
cd tests
dcoker compose up gentoo1 -d
```
