import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.pages.home_page import HomePage
from src.pages.search_page import SearchPage
from src.pages.streamer_page import StreamerPage


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="https://m.twitch.tv", help="Base URL for the site")
    parser.addoption("--device", action="store", default="Pixel 2", help="Chrome mobile emulation device name")
    parser.addoption("--headless", action="store", default="true", help="Run headless Chrome (true/false)")
    parser.addoption("--screenshot-dir", action="store", default="artifacts", help="Directory for screenshots")


@pytest.fixture(autouse=True, scope="class")
def setup_for_testing(request, driver):
    request.cls.driver = driver
    request.cls.home_page = HomePage(driver)
    request.cls.search_page = SearchPage(driver)
    request.cls.streamer_page = StreamerPage(driver)

    # 1. Open home
    request.cls.home_page.open("https://m.twitch.tv")
    # Getting rid off the cookies overlay
    request.cls.home_page.confirm_cookies_overlay_if_shown()


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def screenshot_dir(pytestconfig):
    path = pytestconfig.getoption("--screenshot-dir")
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def driver(pytestconfig):
    device = pytestconfig.getoption("--device")
    headless = pytestconfig.getoption("--headless").lower() == "true"

    options = Options()
    mobile_emulation = { "deviceName": device }
    '''
    mobile_emulation = {
        "deviceMetrics": {
            "width": 393,    # логічна ширина Pixel 5 (dp)
            "height": 851,   # логічна висота Pixel 5 (dp)
            "pixelRatio": 2.75
        },
        "userAgent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        )
    }
    '''
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=412,915")  # typical Pixel 5 size

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()


@pytest.fixture
def timestamped_path(screenshot_dir):
    def _make(name):
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return os.path.join(screenshot_dir, f"{ts}-{name}")
    return _make
