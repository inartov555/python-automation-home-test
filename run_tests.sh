#!/bin/bash

# Input parameters:
#   - $1: the module name to run tests, currently supported (api, web)
#   - $2: the path to the project ( !!! excluding the project folder name !!! ), defaults to $DEFAULT_REPO_PATH
# Exported variables in the setup.sh file: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh "$1" "$2"
if [[ $? -ne 0 ]]; then
  return 1
fi

python3 -m pytest --reruns 3 --reruns-delay 2 -v --tb=short -s --html=$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html
# Now, let's deactivate venv
deactivate
# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
