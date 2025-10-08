"""
Base methods for derived pages
"""

import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from tools.logger.logger import Logger


log = Logger(__name__)


class BasePage:
    """
    Base methods for derived pages
    """

    def __init__(self, driver):
        self.driver = driver

    def pause(self, timeout: int = 3, reason: str = "Waiting a bit"):
        """
        Args:
            timeout (int/float): time in seconds to wait
        """
        log.info(f"{reason}; timeout: {timeout}")
        time.sleep(timeout)

    def web_driver_wait(self, timeout: int = 5):
        """
        Setting WebDriverWait
        """
        return WebDriverWait(self.driver, timeout)

    def action_chains(self):
        """
        Get ActionChains instance
        """
        return ActionChains(self.driver)

    def click_and_drag(self, locator, move_by_x: int = 0, move_by_y: int = 300):
        """
        Clicking and dragging an element
        """
        web_element = self.driver.find_element(*locator)
        self.action_chains().click_and_hold(web_element).move_by_offset(move_by_x, move_by_y).release().perform()

    def blur_active_element(self):
        """
        Unfocusing the element being focused
        """
        self.driver.execute_script("document.activeElement && document.activeElement.blur();")

    def is_displayed(self, locator):
        """
        Check if element is displayed
        """
        try:
            result = self.driver.find_element(*locator).is_displayed()
        except Exception:
            result = False
        return result

    def wait_visible(self, locator, timeout: int = 5) -> bool:
        """
        Wait visible
        """
        return self.web_driver_wait(timeout).until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator, timeout: int = 5) -> bool:
        """
        Wait clickable
        """
        return self.web_driver_wait(timeout).until(EC.element_to_be_clickable(locator))

    def click(self, locator) -> None:
        """
        Regular click
        """
        self.wait_clickable(locator).click()

    def js_click(self, locator) -> None:
        """
        JavaScript click
        """
        # JavaScript click
        web_element = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].click();", web_element)

    def type(self, locator, text: str) -> None:
        """
        Type text
        """
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)

    def scroll_by(self, x: int = 0, y: int = 700) -> None:
        """
        Scroll the page
        """
        self.driver.execute_script("window.scrollBy(arguments[0], arguments[1]);", x, y)

    def scroll_by_xy_repeat(self, x=0, y=700, times=1) -> None:
        """
        When you need to scroll particular number of times
        """
        for _ in range(times):
            self.scroll_by(x, y)
            self.pause(1)
        self.blur_active_element()

    def scroll_into_center(self, locator) -> None:
        """
        Scroll into center
        """
        web_element = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", web_element)

    def maybe_click(self, locator) -> None:
        """
        Tries to click, no effect if element is not clickable
        """
        try:
            self.click(locator)
            return True
        except Exception:
            return False

    def tap_empty_space(self) -> None:
        """
        Tapping empty space
        """
        try:
            self.action_chains().move_by_offset(1, 1).click().perform()
        except Exception:
            pass

    def focus_first_visible(self, locator):
        """
        Returns:
            WebElement, focused element
        """
        try:
            web_element = self.find_first_visible_in_viewport(locator)
            # set focus
            self.driver.execute_script("arguments[0].focus();", web_element)
            return web_element
        except Exception as ex:
            log.error(f"Failed to focus visible element: {ex}")
        return None

    def find_first_visible_in_viewport(self,
                                       locator,
                                       min_ratio: float = 0.5,
                                       top_margin: int = 90,
                                       bottom_margin: int = 0):
        """
        Get the 1st visible element which is visible at list by min_ratio in view port and not covered by other elements.

        Returns:
            WebElement
        """
        by, value = locator

        if by == By.CSS_SELECTOR:
            js = """
            const sel = arguments[0], ratio = arguments[1], topM = arguments[2], bottomM = arguments[3];
            const vh = window.innerHeight || document.documentElement.clientHeight;
            const els = Array.from(document.querySelectorAll(sel));
            function visible(el){
              const r = el.getBoundingClientRect();
              const styles = window.getComputedStyle(el);
              if (styles.display === 'none' || styles.visibility === 'hidden' || parseFloat(styles.opacity) === 0) return false;

              const top    = Math.max(r.top, topM);
              const bottom = Math.min(r.bottom, vh - bottomM);
              const visH   = Math.max(0, bottom - top);
              const height = Math.max(1, r.height);

              if (visH/height < ratio) return false;

              // перевірка перекриття: беремо точку в центрі видимої частини
              const x = Math.floor(r.left + r.width/2);
              const y = Math.floor(top + Math.min(visH, height)/2);
              const e = document.elementFromPoint(x, y);
              return e && (el === e || el.contains(e));
            }
            return els.find(visible) || null;
            """
            return self.driver.execute_script(js, value, float(min_ratio), int(top_margin), int(bottom_margin))
        if by == By.XPATH:
            js = """
            const xpath = arguments[0], ratio = arguments[1], topM = arguments[2], bottomM = arguments[3];
            const vh = window.innerHeight || document.documentElement.clientHeight;
            const snap = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            const els = [];
            for (let i = 0; i < snap.snapshotLength; i++) els.push(snap.snapshotItem(i));

            function visible(el){
              const r = el.getBoundingClientRect();
              const styles = window.getComputedStyle(el);
              if (styles.display === 'none' || styles.visibility === 'hidden' || parseFloat(styles.opacity) === 0) return false;

              const top    = Math.max(r.top, topM);
              const bottom = Math.min(r.bottom, vh - bottomM);
              const visH   = Math.max(0, bottom - top);
              const height = Math.max(1, r.height);

              if (visH/height < ratio) return false;

              const x = Math.floor(r.left + r.width/2);
              const y = Math.floor(top + Math.min(visH, height)/2);
              const e = document.elementFromPoint(x, y);
              return e && (el === e || el.contains(e));
            }
            return els.find(visible) || null;
            """
            return self.driver.execute_script(js, value, float(min_ratio), int(top_margin), int(bottom_margin))
        raise ValueError("Use CSS_SELECTOR or XPATH for this helper.")
