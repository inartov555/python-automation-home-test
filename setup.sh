#!/bin/bash

# $1: the module name to run tests, e.g. web
# Exported variables: ROOT_VENV

PROJECT_NAME=python-automation-home-test
REPO=/home/oeaohoii/Documents/Moi/GitHub/home_test_aqa/$PROJECT_NAME
# path where workspace will be stored
HOST_WORKSPACE=$HOME/TEST1/workspace
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifact"
WORKSPACE=$HOST_WORKSPACE

mkdir -p "$HOST_ARTIFACTS"
chmod a+rw -R "$HOST_ARTIFACTS"
rm -rf "$HOST_WORKSPACE/$PROJECT_NAME"
rsync -aq --progress "$REPO" "$HOST_WORKSPACE" --exclude .git --exclude *.pyc --exclude .pytest_cache
echo "$PROJECT_NAME will is copied"
cd "$HOST_WORKSPACE/$PROJECT_NAME"
exit 0

echo "Root env set up to: $(pwd)"
export ROOT_VENV=$(pwd)
echo "Entering the '$(pwd)/$1' module"
cd "$1"
./setup.sh
