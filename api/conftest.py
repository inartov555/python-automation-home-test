"""
conftest.py file
"""

import os
from datetime import datetime

import pytest

from tools.logger.logger import Logger
from conftest import add_loggers, timestamped_path
from api.api.public_api import PublicApi


log = Logger(__name__)


def pytest_addoption(parser):
    parser.addoption('--api-base', action='store', default='https://catfact.ninja', help='Base URL for API tests')


@pytest.fixture(scope='session')
def api_base(pytestconfig):
    return pytestconfig.getoption('--api-base').rstrip('/')


@pytest.fixture(autouse=True, scope="class")
def setup_api_testing(request):
    request.cls.public_api = PublicApi()
