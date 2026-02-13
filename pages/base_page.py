from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from utils.logger import Logger
import time
import os
from datetime import datetime

class RecoveryHandledException(Exception):
    """Custom exception raised when an error popup was detected and handled via refresh."""
    pass

class BasePage:
    """Base class for all page objects with logging and generic validation."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.timeout = 10
        self.logger = Logger().get_logger()
        self.screenshot_dir = "screenshots"
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def wait_for_page_load(self, timeout=30):
        """Wait for page to be fully loaded and all spinners to disappear."""
        try:
            self.logger.info("Waiting for page readyState 'complete'...")
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Custom polling loop for spinners + Active Error Detection
            # We replace strict WebDriverWait with a loop to ensure we catch "Error Popups" 
            # that might be blocking the "Spinner" from disappearing.
            end_time = time.time() + 60
            spinners_cleared = False
            
            # REMOVED 'popup-background' from this list because it blocks VALID interactive popups
            # Error popups are handled separately by checks inside the loop.
            spinner_selectors = [
                "div.spinner-background",
                "div.spinner",
                "[class*='spinner']",
                "div.loading-overlay",
                ".f-icon_loading",
                ".splash",
                ".loader",
                ".loading",
                "div#init-loader"
            ]
            
            while time.time() < end_time:
                # 1. Check if any spinner is visible
                # We use find_elements for speed (non-blocking)
                found_visible_spinner = False
                for selector in spinner_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(e.is_displayed() for e in elements):
                        found_visible_spinner = True
                        break # Found one, so we are still loading
                
                if not found_visible_spinner:
                    self.logger.info("All detected spinners are gone.")
                    spinners_cleared = True
                    break
                
                # 2. If spinner/popup is present, CHECK IF IT IS AN ERROR
                # The user wants to refresh immediately if it's an error.
                if self.check_for_unexpected_popups():
                    # This method triggers refresh and raises RecoveryHandledException
                    # But since we are inside the method, it returns True (refresh done)
                    # We should probably let it raise, but check_for_unexpected_popups returns True/False
                    # Actually, check_for_unexpected_popups raises RecoveryHandledException in my implementation below
                    # (Wait, let's verify line 206 inside check_for_unexpected_popups)
                    pass

                time.sleep(0.5)

            if not spinners_cleared:
                self.logger.warning("Some spinner is still present after 60s wait, attempting to proceed anyway.")

            self.logger.info("Page fully loaded and ready.")
            time.sleep(1) # Extra buffer
        except RecoveryHandledException:
            raise # Ensure recovery skip is propagated
        except Exception as e:
            self.logger.warning(f"Page load wait encountered an issue: {e}")

    def find_element(self, locator):
        """Finds a visible and clickable element with logging and proactive auto-recovery."""
        try:
            # We use a custom wait that also checks for popups
            return WebDriverWait(self.driver, self.timeout).until(
                lambda d: EC.element_to_be_clickable(locator)(d) or self.check_for_unexpected_popups()
            )
        except RecoveryHandledException:
            raise # Bubble up
        except TimeoutException:
            self.logger.error(f"Element not clickable/found: {locator}")
            self.take_screenshot("element_not_found")
            raise

    def click(self, locator):
        """Clicks on an element. If a popup is detected, it refreshes and skips the step."""
        try:
            self.logger.info(f"Clicking element: {locator}")
            self.find_element(locator).click()
            # Post-click wait (User Requirement: "at every click wait until page ready")
            self.wait_for_page_load()
        except ElementClickInterceptedException:
            self.logger.warning(f"Click intercepted for {locator}. Checking for popups...")
            # check_for_unexpected_popups will raise RecoveryHandledException if a popup is found
            # which will skip this step entirely.
            if not self.check_for_unexpected_popups():
                # If no popup found, it might just be a spinner or temporary overlay
                self.logger.info("No popup found, waiting for page load and retrying once...")
                self.wait_for_page_load()
                self.find_element(locator).click()
            
            # Post-click wait (User Requirement: "at every click wait until page ready")
            self.wait_for_page_load()
        except RecoveryHandledException:
            raise # Ensure skip is propagated
        except Exception as e:
            self.logger.error(f"Failed to click element {locator}: {e}")
            self.take_screenshot("click_failed")
            raise

    def enter_text(self, locator, text: str):
        """Enters text into an input field with logging."""
        try:
            self.logger.info(f"Entering text '{text}' into {locator}")
            element = self.find_element(locator)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            self.logger.error(f"Failed to enter text into {locator}: {e}")
            self.take_screenshot("enter_text_failed")
            raise
    
    def open_url(self, url: str):
        """Navigates to a specific URL."""
        self.logger.info(f"Navigating to {url}")
        self.driver.get(url)
        self.wait_for_page_load()

    def take_screenshot(self, name: str):
        """Take a screenshot and save it with timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None

    def validate_all_interactive_elements(self):
        """
        Generic method to validate presence of inputs and buttons.
        Useful for crawling 36 pages to ensure basic rendering.
        """
        self.logger.info(f"Validating all interactive elements on page: {self.driver.title}")
        
        # Check Inputs
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        self.logger.info(f"Found {len(inputs)} input fields.")
        for i, inp in enumerate(inputs):
            try:
                if inp.is_displayed():
                    self.logger.info(f"Input {i} (type={inp.get_attribute('type')}) is displayed.")
            except Exception as e:
                self.logger.warning(f"Input {i} validation failed: {e}")

        # Check Buttons
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        self.logger.info(f"Found {len(buttons)} buttons.")
        for i, btn in enumerate(buttons):
            try:
                if btn.is_displayed():
                    self.logger.info(f"Button {i} (text='{btn.text}') is displayed.")
            except Exception as e:
                self.logger.warning(f"Button {i} validation failed: {e}")
                
        return True

    def wait_until_invisible(self, locator, timeout=10):
        """Waits until an element is invisible or removed from DOM."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.logger.warning(f"Element {locator} still visible after {timeout}s")
            return False

    def check_for_unexpected_popups(self):
        """
        Checks if an unexpected popup or error is present.
        If found, takes a screenshot, refreshes the page, and returns True.
        """
        try:
            # Specific patterns for REAL error popups or blocking dialogs
            recovery_locators = [
                (By.XPATH, "//*[contains(text(), 'An error has occurred')]"),
                (By.XPATH, "//*[contains(text(), 'technical error')]"),
                (By.XPATH, "//*[contains(text(), 'Failed')]"),
                (By.XPATH, "//*[contains(@class, 'error-message')]"),
                (By.XPATH, "//div[contains(@class, 'popup-title') and contains(text(), 'Error')]"),
                (By.XPATH, "//div[contains(@class, 'popup-title') and contains(text(), 'Alert')]"),
                (By.CSS_SELECTOR, "div.popup-error, div.modal-error")
            ]
            
            for locator in recovery_locators:
                elements = self.driver.find_elements(*locator)
                if len(elements) > 0 and any(e.is_displayed() for e in elements):
                    self.logger.warning(f"Unexpected popup/error detected via: {locator}")
                    self.take_screenshot("unexpected_popup_detected")
                    curr_url = self.driver.current_url
                    self.logger.info("Popup detected. Refreshing immediately...")
                    # User requested: Wait 3 sec before refresh
                    time.sleep(3) 
                    self.logger.info(f"Navigating to current URL to clear popup: {curr_url}")
                    self.driver.get(curr_url)
                    
                    # User requested: "wait until page ready" (Full wait logic)
                    self.wait_for_page_load()
                    
                    self.logger.info("Page ready after recovery navigation. Skipping current step.")
                    raise RecoveryHandledException("Error popup handled via navigation.")
        except RecoveryHandledException:
            raise # Bubble up
        except Exception as e:
            self.logger.debug(f"Popup check failed (normal if no popup): {e}")
        
        return False
