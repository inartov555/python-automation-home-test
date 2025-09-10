from selenium.webdriver.common.by import By
from .base_page import BasePage

class HomePage(BasePage):
    SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label='Search'] , a[aria-label='Search'] , a[href*='search']")

    def open(self, base_url):
        self.driver.get(base_url + "/")

    def open_search(self):
        self.click(self.SEARCH_ICON)