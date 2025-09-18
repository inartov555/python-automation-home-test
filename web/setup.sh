#!/bin/bash

REPO=/home/oeaohoii/Documents/Moi/GitHub/home_test_aqa/python-automation-home-test
HOME=/home/oeaohoii
# path where workspace will be stored
HOST_WORKSPACE=$HOME/TEST1/workspace
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifact"
WORKSPACE=$HOST_WORKSPACE

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_FILE=$DIR/venv/version.txt
PROJECT=$1
cd ${DIR}

echo "Copied instance of python-automation-home-test will be used. You can continue working with your local instance"
mkdir -p $HOST_ARTIFACTS
chmod a+rw -R $HOST_ARTIFACTS
export REPO_PATH="$WORKSPACE/python-automation-home-test"
rm -rf $HOST_WORKSPACE/python-automation-home-test
rsync -aq --progress $REPO $HOST_WORKSPACE --exclude .git --exclude *.pyc --exclude .pytest_cache
echo "$DIR"
exit 0

if python3 -m venv --help > /dev/null 2>&1; then
    echo "venv module is available"
else
    python3 -m pip install --user virtualenv
fi
python3 -m venv venv
. venv/bin/activate

BASE_REQ_FILE="${DIR}/requirements.txt"

if [[ -n ${PROJECT} ]]; then
  if [[ -f "${PROJECT_REQ_FILE}" ]]; then
    req_file="${PROJECT_REQ_FILE}"
    echo "Using project base requirements: ${PROJECT} @ ${req_file}"
    venv1_ver=$( md5sum "${PROJECT_REQ_FILE}" | cut -d' ' -f1 )
    venv2_ver=$( md5sum "${BASE_REQ_FILE}" | cut -d' ' -f1 )
    required_venv_version="${venv1_ver},${venv2_ver}"
  else
    req_file=${ONE_ENV_REQ_FILE}
    echo "Project ${PROJECT} uses OneENV requirements: ${req_file}"
    required_venv_version=$( md5sum $req_file | cut -d' ' -f1 )
  fi
else
  req_file=${ONE_ENV_REQ_FILE}
  echo "Using OneENV requirements: ${req_file}"
  required_venv_version=$( md5sum $req_file | cut -d' ' -f1 )
fi

if [[ -f ${VERSION_FILE} ]]; then
  installed_venv_version=$( cat ${VERSION_FILE} )
else
  installed_venv_version="None"
fi
if [[ ${installed_venv_version} == ${required_venv_version} ]]; then
  echo "Actual version of VENV is ok to go. VERSION: ${installed_venv_version}"
else
  echo "Installing VENV. Ver: ${required_venv_version}"
  python3 -m pip install --upgrade pip
  python3 -m pip install wheel setuptools
  python3 -m pip install -r "$req_file"
  echo ${required_venv_version} > ${VERSION_FILE}
fi

echo "Virtual env set up to: $(pwd)"
export TEST_VENV=$(pwd)
