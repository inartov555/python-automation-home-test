"""
conftest.py file
"""
# pylint: disable=duplicate-code

import os
from datetime import datetime

import pytest

from tools.logger.logger import Logger
from api.api.public_api import PublicApi


log = Logger(__name__)


@pytest.fixture(autouse=True, scope="session")
def add_loggers() -> None:
    """
    The fixture to configure loggers
    It uses built-in pytest arguments to configure loggigng level and files

    Parameters:
        log_level or --log-level general log level for capturing
        log_file_level or --log-file-level  level of log to be stored to a file. Usually lower than general log
        log_file or --log-file  path where logs will be saved
    """
    artifacts_folder_default = os.getenv("HOST_ARTIFACTS")
    log_level = "DEBUG"
    log_file_level = "DEBUG"
    log_file = os.path.join(timestamped_path("pytest", "log", artifacts_folder_default))
    log.setup_cli_handler(level=log_level)
    log.setup_filehandler(level=log_file_level, file_name=log_file)
    log.info(f"General loglevel: '{log_level}', File: '{log_file_level}'")
    log.info(f"Test's logs will be stored: '{log_file}'")


def timestamped_path(file_name: str, file_ext: str, path_to_file: str = os.getenv("HOST_ARTIFACTS")) -> str:
    """
    Args:
        file_name (str): e.g. screenshot
        file_ext (str): file extention, e.g., png
        path_to_file (str): e.g. /home/user/test_dir/artifacts/

    Returns:
        str, timestamped path
    """
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")
    return os.path.join(path_to_file, f"{file_name}-{ts}.{file_ext}")


def pytest_addoption(parser):
    """
    Supported options
    """
    parser.addoption('--api-base', action='store', default='https://catfact.ninja', help='Base URL for API tests')


@pytest.fixture(scope='session')
def api_base(pytestconfig):
    """
    Get base URL from the fixture
    """
    return pytestconfig.getoption('--api-base').rstrip('/')


@pytest.fixture(autouse=True, scope="class")
def setup_api_testing(request):
    """
    Setting API instance for testing
    """
    request.cls.public_api = PublicApi()
