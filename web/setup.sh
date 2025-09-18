#!/bin/bash

# NOTE: there's ROOT_VENV, it's defined in setup.sh located in the main project directory
MODULE_PATH=$ROOT_VENV/web
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
