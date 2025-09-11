from selenium.webdriver.common.by import By
from .base_page import BasePage


class HomePage(BasePage):
    SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label='Search'] , a[aria-label='Search'] , a[href*='search']")
    # Accept cookies overlay
    ACCEPT_BUTTON = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept']")

    def open(self, base_url):
        self.driver.get(base_url + "/")

    def open_search(self):
        self.click(self.SEARCH_ICON)

    def confirm_accept_cookies_overlay_if_shown(self):
        self.click(self.SEARCH_ICON)
