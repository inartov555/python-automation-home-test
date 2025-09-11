import time

import pytest

from web.conftest import setup_for_testing


@pytest.mark.mobile
@pytest.mark.usefixtures("setup_apps_and_games")
def test_search_and_open_streamer(driver, base_url, timestamped_path):
    # 1. Open home
    self.home_page.open(base_url)
    # 2. Tap search icon
    self.home_page.open_search()
    # 3. Type query
    self.search_page.search("StarCraft II")
    # 4. Scroll down twice (small delays to simulate user)
    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(0.5)
    # 5. Open a streamer
    self.search_page.open_first_streamer()
    # 6. Wait for streamer page to load; take screenshot
    self.streamer_page.ensure_loaded()
    screenshot_path = timestamped_path("streamer.png")
    driver.save_screenshot(screenshot_path)
    print(f"Saved screenshot: {screenshot_path}")
