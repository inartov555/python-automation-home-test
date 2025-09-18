#!/bin/bash

# $1: the module name to run tests, e.g. api
# Exported variables in the setup.sh file: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV

ORIGINAL_PROJECT_PATH="$(pwd)"
source ./setup.sh "$1"
python3 -m pytest --reruns 3 --reruns-delay 2 -v --tb=short -s --html=$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html
# Now, let's deactivate venv
deactivate
# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
