from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.wait_clickable(locator).click()

    def type(self, locator, text):
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)

    def scroll_by(self, x=0, y=600):
        self.driver.execute_script("window.scrollBy(arguments[0], arguments[1]);", x, y)

    def maybe_click(self, locator):
        try:
            self.click(locator)
            return True
        except Exception:
            return False
