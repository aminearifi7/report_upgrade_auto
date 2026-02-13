from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage, RecoveryHandledException
import time

class WifiPage(BasePage):
    """Page Object for the WiFi Page."""

    # URL
    URL_PATH = "#wifi/"

    # Locators
    WIFI_TOGGLE = (By.CSS_SELECTOR, "div.label-toggle__indicator")
    POPUP_OK = (By.XPATH, "//*[@id='popup-ok' or contains(text(), 'Yes, continue')]")
    WPS_BUTTON = (By.CSS_SELECTOR, "div.button-with-icon__label")
    # UPDATED: Use broader selector to match base_page logic and catch ALL overlays
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(text(), 'Apply')]")
    SPLIT_STATE_INDICATOR = (By.XPATH, "//div[contains(text(), 'Split')]")
    SPLIT_ICON = (By.CSS_SELECTOR, "div.f-icon_split")

    def navigate(self, base_url=None):
        """Navigates to the WiFi page."""
        url = f"{base_url if base_url else 'http://192.168.1.1'}/{self.URL_PATH}"
        self.logger.info(f"Navigating to {url}")
        
        # Robust navigation
        self.driver.get(url)
        time.sleep(2)
        if "wifi" not in self.driver.current_url.lower():
             self.driver.get(url)
             time.sleep(2)
             
        self.wait_for_page_load()
        
        # Verify content
        try:
            self.find_element(self.WIFI_TOGGLE, timeout=10)
            self.logger.info("WiFi page verified (Toggle found).")
        except:
            self.logger.warning("WiFi toggle not found. Page might not have loaded correctly. Refreshing...")
            self.driver.refresh()
            self.wait_for_page_load()

    def wait_until_wifi_state(self, target_enabled: bool, timeout=45):
        """
        Waits until the WiFi toggle reflects the target state.
        target_enabled=True  => waits for 'f-icon_check' class.
        target_enabled=False => waits for 'f-icon_check' class to DISAPPEAR.
        Includes proactive error popup detection.
        """
        self.logger.info(f"Waiting until WiFi state is: {'Enabled' if target_enabled else 'Disabled'}...")
        
        try:
            if target_enabled:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: ("f-icon_check" in d.find_element(*self.WIFI_TOGGLE).get_attribute("class")) or 
                               self.check_for_unexpected_popups()
                )
            else:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: ("f-icon_check" not in d.find_element(*self.WIFI_TOGGLE).get_attribute("class")) or 
                               self.check_for_unexpected_popups()
                )
            self.logger.info(f"WiFi state reached: {'Enabled' if target_enabled else 'Disabled'}")
            return True
        except RecoveryHandledException:
            raise # Bubble up to toggle_wifi
        except TimeoutException:
            self.logger.error(f"Timeout waiting for WiFi to become {'Enabled' if target_enabled else 'Disabled'}")
            self.take_screenshot("wifi_state_timeout")
            return False

    def toggle_wifi(self, target_state=None):
        """
        Disables or enables WiFi and optionally waits for a specific target state.
        target_state: True for Enabled, False for Disabled, None for 'just toggle'.
        """
        self.logger.info(f"Attempting to toggle Global WiFi... (Target state: {target_state})")
        
        try:
            # 1. Click the toggle
            # BasePage.find_element (via click) will now handle error recovery automatically
            self.wait_for_page_load() 
            self.click(self.WIFI_TOGGLE)
            self.logger.info("WiFi toggle clicked.")

            # 2. Wait for any loading/popup
            self.logger.info("Waiting for secondary UI state (popup or spinner)...")
            time.sleep(1.5) 
            
            # 3. Custom Poll Loop: "Yes" Button vs. Error Popup/Blocker
            # Adjusted strategy: Wait longer (30s) but check specifically for ERRORS.
            self.logger.info("Polling for confirmation or error (Concurrent Check)...")
            confirmation_clicked = False
            
            end_time = time.time() + 30 # Increased to 30s to allow slow loading
            while time.time() < end_time:
                # A. Check for 'Yes, continue'
                yes_btns = self.driver.find_elements(*self.POPUP_OK)
                if yes_btns and yes_btns[0].is_displayed() and yes_btns[0].is_enabled():
                    self.logger.info("'Yes, continue' button found. Clicking...")
                    try:
                        yes_btns[0].click()
                        confirmation_clicked = True
                        self.logger.info("Confirmation clicked.")
                        self.wait_until_invisible(self.POPUP_BACKGROUND)
                        break 
                    except Exception as e:
                        self.logger.warning(f"Failed to click valid 'Yes' button: {e}")
                
                # B. Active Error Check
                # Using the base page logic which looks for specific "Error" text/titles
                if self.check_for_unexpected_popups():
                    return False

                # C. Check specifically for the broad 'popup-background' but ONLY trigger if it's NOT the Yes button logic
                # (handled by check_for_unexpected_popups mainly). 
                # If check_for_unexpected_popups didn't trigger, it means it's not a KNOWN error.
                # Could be a spinner. We just wait.
                
                time.sleep(0.2)
            
            if not confirmation_clicked:
                 self.logger.warning("Loop finished (30s). No confirmation clicked.")
                 # We do NOT force refresh here blindly anymore.
                 # Proceeding to wait_for_page_load to ensure stability.


            # 4. Wait for the toggle action to process (UI sync)
            self.wait_for_page_load(timeout=60)
            
            # 5. Functional Verification: Wait until the state is reached
            if target_state is not None:
                return self.wait_until_wifi_state(target_state)
            
            return True

        except RecoveryHandledException as e:
            self.logger.warning(f"WiFi Action interrupted by Global Recovery: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to toggle WiFi: {e}")
            self.take_screenshot("wifi_toggle_failed")
            return False

    def is_wifi_enabled(self):
        """Checks if the WiFi is currently enabled."""
        try:
            element = self.find_element(self.WIFI_TOGGLE)
            return "f-icon_check" in element.get_attribute("class")
        except:
            return None

    def launch_wps(self):
        """
        Clicks Launch WPS and waits 10 seconds.
        Returns the button label text after the wait.
        """
        self.logger.info("Attempting to launch WPS...")
        try:
            # 1. Locate and click WPS button
            # We look for the div containing 'Launch WPS'
            wps_btn = self.find_element(self.WPS_BUTTON)
            if "LAUNCH WPS" not in wps_btn.text.upper():
                self.logger.warning(f"WPS button text is '{wps_btn.text}', expected something like 'Launch WPS'.")
            
            self.click(self.WPS_BUTTON)
            self.logger.info("WPS Launch clicked. Waiting 10 seconds...")
            
            # 2. Wait 10 seconds as requested
            time.sleep(10)
            
            # 3. Check for unexpected popups after the wait (proactive)
            # This will raise RecoveryHandledException if a popup appeared
            self.check_for_unexpected_popups()
            
            # 4. Get new label
            new_label = self.find_element(self.WPS_BUTTON).text
            self.logger.info(f"WPS Label after 10s: '{new_label}'")
            return new_label

        except RecoveryHandledException as e:
            self.logger.warning(f"WPS Launch interrupted by Global Recovery: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to launch WPS: {e}")
            self.take_screenshot("wps_launch_failed")
            return None

    def is_already_split(self):
        """Checks if VAPs are already split based on UI indicator."""
        try:
            return len(self.driver.find_elements(*self.SPLIT_STATE_INDICATOR)) > 0
        except:
            return False

    def click_help_icon(self):
        """Clicks the help icon on the WiFi page via JavaScript to avoid interception."""
        self.logger.info("Clicking the Help icon (JS)...")
        try:
            element = self.find_element(self.HELP_ICON_BUTTON)
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info("Help icon clicked.")
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to click Help icon: {e}")
            self.take_screenshot("help_icon_click_failed")
            return False

    def apply_changes(self):
        """Clicks the Apply button via JS and handles the confirmation popup."""
        self.logger.info("Attempting to Apply changes (JS)...")
        try:
            # 1. Click Apply via JS to avoid interception
            element = self.find_element(self.APPLY_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info("Apply button clicked (JS).")
            
            # 2. Handle 'Yes, continue' popup
            time.sleep(2) # Give popup a moment to appear
            self.logger.info("Confirming with 'Yes, continue'...")
            self.click(self.POPUP_OK)
            self.logger.info("Confirmation 'Yes, continue' clicked.")
            
            # 3. Wait for popup to disappear
            self.wait_until_invisible(self.POPUP_BACKGROUND)
            self.wait_for_page_load(timeout=60)
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply changes: {e}")
            self.take_screenshot("apply_changes_failed")
            return False

    def split_vaps(self):
        """Performs the WiFi VAP splitting sequence: Split Icon -> Apply -> Yes, continue."""
        self.logger.info("Starting WiFi VAP split sequence...")
        try:
            # 1. Click Split Icon
            self.logger.info("Clicking Split icon...")
            self.click(self.SPLIT_ICON)
            
            # 2. Click Apply
            self.logger.info("Clicking Apply button...")
            self.click(self.APPLY_BUTTON)
            
            # 3. Confirm with 'Yes, continue'
            self.logger.info("Confirming VAP split with 'Yes, continue'...")
            # Using the existing POPUP_OK locator which matches the provided HTML id="popup-ok"
            self.click(self.POPUP_OK)
            
            self.logger.info("Waiting for VAP split to be processed...")
            self.wait_for_page_load(timeout=60)
            self.logger.info("VAP split completed successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to split VAPs: {e}")
            self.take_screenshot("split_vaps_failed")
            return False
