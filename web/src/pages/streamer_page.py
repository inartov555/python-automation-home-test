"""
Streamer page
"""

from selenium.webdriver.common.by import By

from tools.logger.logger import Logger
from web.src.pages.base_page import BasePage


log = Logger(__name__)


class StreamerPage(BasePage):
    """
    Streamer page
    """
    # Possible popups (consent, mature content, cookie, login prompts, etc.)
    DISMISS_SELECTORS = [
        (By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Dismiss']"),
        (By.CSS_SELECTOR, "button:has(svg[aria-label='Close'])"),
        (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept'], button[aria-label*='Accept']"),
        (By.CSS_SELECTOR, "button:contains('Continue'), a:contains('Continue')")
    ]

    VIDEO_PLAYER = (By.CSS_SELECTOR, "video, div[data-a-target='video-player'], div[class*='player']")
    CHANNEL_HEADER = (By.CSS_SELECTOR, "header, h1, h2")

    def ensure_loaded(self):
        """
        Make sure the video/player is visible
        """
        # Try to close any modal/popups if they appear
        for loc in self.DISMISS_SELECTORS:
            self.maybe_click(loc)
        # Wait for either a video/player container or channel header to be visible
        try:
            return self.wait_visible(self.VIDEO_PLAYER)
        except Exception:
            return self.wait_visible(self.CHANNEL_HEADER)
