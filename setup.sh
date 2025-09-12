#!/bin/bash

# $1: the module name to run tests, e.g. web
# Exported variables: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV

if [ -z $1 ]; then
  echo "ERROR: module path must be set to run the tests"
  return 1
fi

PROJECT_NAME="python-automation-home-test"
REPO="$HOME/$PROJECT_NAME"
# path where workspace will be stored
HOST_WORKSPACE="$HOME/TEST1/workspace"
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifact"
WORKSPACE=$HOST_WORKSPACE
export HOST_ARTIFACTS=$HOST_ARTIFACTS

mkdir -p "$HOST_ARTIFACTS"
chmod a+rw -R "$HOST_ARTIFACTS"
rm -rf "$HOST_WORKSPACE/$PROJECT_NAME"
rsync -aq --progress "$REPO" "$HOST_WORKSPACE" --exclude .git --exclude *.pyc --exclude .pytest_cache
if [ $? -ne 0 ]; then
  echo "Cant create workspace $HOST_WORKSPACE, Please configure the path inside of this script"
  ls $HOST_WORKSPACE
fi
echo "$REPO is copied"
cd "$HOST_WORKSPACE/$PROJECT_NAME"

echo "Root env set up to: $(pwd)"
export ROOT_VENV=$(pwd)
echo "Entering the '$(pwd)/$1' module"
cd "$1"

# Activating venv

MODULE_PATH="$ROOT_VENV/$1"
cd "$MODULE_PATH"

if python3 -m venv --help > /dev/null 2>&1; then
    echo "venv module is available"
else
    python3 -m pip install --user virtualenv
fi
python3 -m venv venv
. venv/bin/activate

BASE_REQ_FILE="$MODULE_PATH/requirements.txt"
echo "Installing module requirements"
python3 -m pip install --upgrade pip
python3 -m pip install -r "$BASE_REQ_FILE"

echo "Virtual env set up to: $(pwd)"
export TEST_VENV=$(pwd)
