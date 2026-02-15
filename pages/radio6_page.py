from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class Radio6Page(BasePage):
    """Page Object for the Radio 6GHz Configuration Page."""

    URL_PATH = "#radio/2"

    # Locators
    CHANNEL_DROPDOWN = (By.CSS_SELECTOR, "span.select-placeholder__icon.f-icon.f-icon_select-down")
    # Using the specific nth-child(11) provided by user for channel 37
    CHANNEL_37_OPTION = (By.CSS_SELECTOR, ".basic-select__content-container div:nth-child(11)")
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(text(), 'Apply')]")

    def navigate(self):
        """Navigates to the Radio 6GHz page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to Radio 6GHz page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "radio" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def select_channel_37(self):
        """Selects channel 37 and clicks Apply."""
        self.logger.info("Selecting Channel 37 for Radio 6GHz")
        try:
            # 1. Open dropdown
            self.click(self.CHANNEL_DROPDOWN)
            time.sleep(1)

            # 2. Select option 37
            self.click(self.CHANNEL_37_OPTION)
            time.sleep(1)

            # 3. Click Apply
            self.click(self.APPLY_BUTTON)
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Radio 6GHz: {e}")
            self.take_screenshot("radio6_config_failed")
            return False
