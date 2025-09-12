import pytest
import time

from tools.logger.logger import Logger

@pytest.mark.mobile
class TestTwitchMobile(object):
    log = Logger(__name__)

    def test_search_and_open_streamer(self, driver, base_url, timestamped_path):
        # 1. Open home
        self.home_page.open(base_url)
        # 2. Tap search icon
        self.home_page.open_search()
        # 3. Type query
        self.search_page.search("StarCraft II")
        # 4. Scroll down twice (small delays to simulate user)
        self.search_page.scroll_by_xy_repeat(times=2)
        # 5. Open a streamer
        self.search_page.open_first_streamer()
        # 6. Wait for streamer page to load; take screenshot
        self.streamer_page.ensure_loaded()
        screenshot_path = timestamped_path("streamer.png")
        self.driver.save_screenshot(screenshot_path)
        self.log.debug(f"Saved screenshot: {screenshot_path}")
