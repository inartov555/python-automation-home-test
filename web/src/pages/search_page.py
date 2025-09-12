from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage


class SearchPage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[aria-label='Search']")
    FIRST_RESULT = (By.XPATH, "//section//a[starts-with(@href, '/videos/')] | //section//div[class='Layout-sc-1xcs6mc-0 doaFqY']")

    def search(self, query):
        self.type(self.SEARCH_INPUT, query + Keys.ENTER)
        self.blur_active_element()

    def open_first_streamer(self):
        # Heuristic: click the first visible result anchor
        el = self.wait_visible(self.FIRST_RESULT)
        el.click()
