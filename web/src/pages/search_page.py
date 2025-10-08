"""
Search page
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tools.logger.logger import Logger
from web.src.pages.base_page import BasePage


log = Logger(__name__)


class SearchPage(BasePage):
    """
    Search page
    """
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[aria-label='Search']")
    FIRST_RESULT = (
        By.XPATH,
        "//section//a[starts-with(@href, '/videos/')] | "
        "//section//button[@class='ScCoreLink-sc-16kq0mq-0 cZfgmJ InjectLayout-sc-1i43xsx-0 ggvZjN tw-link']")

    def search(self, query):
        """
        Typing search text, starting search and the unfocusing active element
        """
        self.type(self.SEARCH_INPUT, query + Keys.ENTER)
        self.blur_active_element()

    def open_first_streamer(self):
        """
        Heuristic: click the first visible result anchor
        """
        self.wait_visible(self.FIRST_RESULT)
        el = self.focus_first_visible(self.FIRST_RESULT)
        el.click()
