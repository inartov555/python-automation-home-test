"""
conftest.py file
"""

import os
from datetime import datetime

import pytest

from conftest import add_loggers, timestamped_path
from tools.logger.logger import Logger
from api.api.public_api import PublicApi


log = Logger(__name__)


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
