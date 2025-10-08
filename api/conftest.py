"""
conftest.py file
"""

import pytest

from conftest import add_loggers, timestamped_path
from tools.logger.logger import Logger
from api.api.public_api import PublicApi


log = Logger(__name__)


@pytest.fixture(autouse=True, scope="session")
def add_loggers_to_tests(request) -> None:
    """
    The fixture to configure loggers
    It uses built-in pytest arguments to configure loggigng level and files

    Parameters:
        log_level or --log-level general log level for capturing
        log_file_level or --log-file-level  level of log to be stored to a file. Usually lower than general log
        log_file or --log-file  path where logs will be saved
    """
    add_loggers(request)


def get_timestamped_path(file_name: str, file_ext: str, path_to_file: str = os.getenv("HOST_ARTIFACTS")) -> str:
    """
    Args:
        file_name (str): e.g. screenshot
        file_ext (str): file extention, e.g., png
        path_to_file (str): e.g. /home/user/test_dir/artifacts/

    Returns:
        str, timestamped path
    """
    return timestamped_path(file_name, file_ext, path_to_file)


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
