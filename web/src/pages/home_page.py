from selenium.webdriver.common.by import By
from .base_page import BasePage


class HomePage(BasePage):
    # SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label='Search'] , a[aria-label='Search'] , a[href*='search']")
    SEARCH_ICON = (By.XPATH, "//a[@href='/directory']/div/div")
    # Accept cookies overlay
    ACCEPT_BUTTON = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept']")
    # Sometimes, transition to app overlay is shown when selecting, e.g., the search button,
    # this overlay consists of 2 parts
    TRANSITION_TO_APP_OVERLAY = (By.XPATH,
        "//div[@class='ScReactModalBase-sc-26ijes-0 foAhuv tw-modal-layer']//div[@class='Layout-sc-1xcs6mc-0 cBrePX']")
    CLOSE_OVERLAY = (By.XPATH,
        "//div[@class='ScReactModalBase-sc-26ijes-0 foAhuv tw-modal-layer']//button[@class='InjectLayout-sc-1i43xsx-0 ccdBQN']"
    )

    def open(self, base_url):
        self.driver.get(base_url + "/")

    def open_search(self):
        self.click(self.SEARCH_ICON)
        self.get_out_of_transition_to_app_overlay()

    def confirm_cookies_overlay_if_shown(self):
        """
        Clicking the Accept button on the "Cookies and Advertising Choices" overlay, if it is shown
        """
        self.wait_visible(self.ACCEPT_BUTTON)
        self.click(self.ACCEPT_BUTTON)

    def get_out_of_transition_to_app_overlay(self):
        """
        Clicking the Accept button on the "Cookies and Advertising Choices" overlay, if it is shown
        """
        try:
            if self.wait_visible(self.TRANSITION_TO_APP_OVERLAY, 2):
                self.js_click(self.CLOSE_OVERLAY)
        except Exception:
            pass
