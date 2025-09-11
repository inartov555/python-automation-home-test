from selenium.webdriver.common.by import By
from .base_page import BasePage


class HomePage(BasePage):
    # SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label='Search'] , a[aria-label='Search'] , a[href*='search']")
    SEARCH_ICON = (By.XPATH, "//a[@href='/directory']")
    # Accept cookies overlay
    ACCEPT_BUTTON = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept']")

    def open(self, base_url):
        self.driver.get(base_url + "/")

    def open_search(self):
        self.click(self.SEARCH_ICON)

    def confirm_cookies_overlay_if_shown(self):
        """
        Clicking the Accept button on the "Cookies and Advertising Choices" overlay, if it is shown
        """
        self.wait_visible(self.ACCEPT_BUTTON)
        self.click(self.ACCEPT_BUTTON)
