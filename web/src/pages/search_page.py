from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage


class SearchPage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[aria-label='Search']")
    FIRST_RESULT = (By.CSS_SELECTOR, "a[href*='/videos'] , a[href*='/videos?'] , a[data-a-target='search-result'] , a[href*='/\w+$']")

    def search(self, query):
        self.type(self.SEARCH_INPUT, query + Keys.ENTER)

    def open_first_streamer(self):
        # Heuristic: click the first visible result anchor
        el = self.wait_visible(self.FIRST_RESULT)
        el.click()
