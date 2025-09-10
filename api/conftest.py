import pytest

def pytest_addoption(parser):
    parser.addoption('--api-base', action='store', default='https://catfact.ninja', help='Base URL for API tests')

@pytest.fixture(scope='session')
def api_base(pytestconfig):
    return pytestconfig.getoption('--api-base').rstrip('/')