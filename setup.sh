#!/bin/bash

# Input parameters:
#   - $1: the module name to run tests, currently supported (api, web)
#   - $2: the path to the project ( !!! excluding the project folder name !!! ), defaults to $DEFAULT_REPO_PATH
# Exported variables: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

if [ -z $1 ]; then
  echo "ERROR: module name must be set to run the tests"
  return 1
fi

DEFAULT_PROJECT_NAME="python-automation-home-test"
DEFAULT_REPO_PATH="$HOME/$DEFAULT_PROJECT_NAME"

# Repo path defaults to $DEFAULT_REPO_PATH
if [[ -z "$2" ]]; then
  echo "WARNING: no path passed for the project, defaulting to $DEFAULT_REPO_PATH"
  REPO="$DEFAULT_REPO_PATH"
  if [[ ! -d "$REPO" ]]; then
    echo "ERROR: Default path $DEFAULT_REPO_PATH for the repo does not exist"
    return 1
  fi
elif [[ ! -d "$2" ]]; then
  echo "ERROR: Provided path $2 for the repo does not exist"
  return 1
else
  if [[ "${2: -1}" == "/" ]]; then
    REPO="$2$DEFAULT_PROJECT_NAME"
  else
    REPO="$2/$DEFAULT_PROJECT_NAME"
  fi
  echo "Using $REPO path for the repo"
fi

# path where workspace will be stored
HOST_WORKSPACE="$HOME/TEST1/workspace"
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifact"
export HOST_ARTIFACTS="$HOST_ARTIFACTS"
export COPIED_PROJECT_PATH="$HOST_WORKSPACE/$DEFAULT_PROJECT_NAME"

echo "Host workspace directory (copied project + logs, screenshots, etc.):"
echo "  >>> $HOST_WORKSPACE"
echo "Host artifacts directory (logs, screenshots, etc.):"
echo "  >>> $HOST_ARTIFACTS"

mkdir -p "$HOST_ARTIFACTS"
chmod a+rw -R "$HOST_ARTIFACTS"
rm -rf "$COPIED_PROJECT_PATH"
rsync -aq --progress "$REPO" "$HOST_WORKSPACE" --exclude .git --exclude *.pyc --exclude .pytest_cache
if [ $? -ne 0 ]; then
  echo "Cant create workspace $COPIED_PROJECT_PATH, Please configure the path inside of this script"
  ls $HOST_WORKSPACE
fi
echo "$REPO is copied to $COPIED_PROJECT_PATH"
echo "Entering the $COPIED_PROJECT_PATH directory"
cd "$COPIED_PROJECT_PATH"

echo "Root env set up to: $(pwd)"
export ROOT_VENV="$COPIED_PROJECT_PATH"
echo "Entering the '$COPIED_PROJECT_PATH/$1' module"
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
