from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver

    def web_driver_wait(self, timeout=5):
        return WebDriverWait(self.driver, timeout)

    def action_chains(self):
        return ActionChains(self.driver)

    def click_and_drag(self, locator, move_by_x=0, move_by_y=300):
        web_element = self.driver.find_element(*locator)
        self.action_chains().click_and_hold(web_element).move_by_offset(move_by_x, move_by_y).release().perform()

    def blur_active_element(self):
        # Unfocusing the element being focused
        self.driver.execute_script("document.activeElement && document.activeElement.blur();")

    def is_displayed(self, locator):
        try:
            result = self.driver.find_element(*locator).is_displayed()
        except Exception:
            result = False
        return result

    def wait_visible(self, locator, timeout=5):
        return self.web_driver_wait(timeout).until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator, timeout=5):
        return self.web_driver_wait(timeout).until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.wait_clickable(locator).click()

    def js_click(self, locator):
        # JavaScript click
        web_element = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].click();", web_element)

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
