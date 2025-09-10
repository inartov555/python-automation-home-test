import time
import pytest
from src.pages.home_page import HomePage
from src.pages.search_page import SearchPage
from src.pages.streamer_page import StreamerPage

@pytest.mark.mobile
def test_search_and_open_streamer(driver, base_url, timestamped_path):
    home = HomePage(driver)
    search = SearchPage(driver)
    streamer = StreamerPage(driver)

    # 1. Open home
    home.open(base_url)

    # 2. Tap search icon
    home.open_search()

    # 3. Type query
    search.search("StarCraft II")

    # 4. Scroll down twice (small delays to simulate user)
    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(0.5)

    # 5. Open a streamer
    search.open_first_streamer()

    # 6. Wait for streamer page to load; take screenshot
    streamer.ensure_loaded()
    screenshot_path = timestamped_path("streamer.png")
    driver.save_screenshot(screenshot_path)
    print(f"Saved screenshot: {screenshot_path}")