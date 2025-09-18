import pytest

from api.api.public_api import PublicApi


def pytest_addoption(parser):
    parser.addoption('--api-base', action='store', default='https://catfact.ninja', help='Base URL for API tests')


@pytest.fixture(scope='session')
def api_base(pytestconfig):
    return pytestconfig.getoption('--api-base').rstrip('/')


@pytest.fixture(autouse=True, scope="class")
def driver(request):
    request.cls.public_api = PublicApi()
