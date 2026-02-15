from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class Radio5Page(BasePage):
    """Page Object for the Radio 5GHz Configuration Page."""

    URL_PATH = "#radio/1"

    # Locators
    CHANNEL_DROPDOWN = (By.CSS_SELECTOR, "span.f-icon_select-down")
    CHANNEL_36_OPTION = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.radio-page.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div > div:nth-child(2) > div:nth-child(1) > div > div.label-field__content > div > div > div > div.basic-select__content-container > div > div:nth-child(2)")
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(text(), 'Apply')]")

    def navigate(self):
        """Navigates to the Radio 5GHz page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to Radio 5GHz page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "radio" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def select_channel_36(self):
        """Selects channel 36 and clicks Apply."""
        self.logger.info("Selecting Channel 36 for Radio 5GHz")
        try:
            # 1. Open dropdown
            self.click(self.CHANNEL_DROPDOWN)
            time.sleep(1)

            # 2. Select option 36
            self.click(self.CHANNEL_36_OPTION)
            time.sleep(1)

            # 3. Click Apply
            self.click(self.APPLY_BUTTON)
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Radio 5GHz: {e}")
            self.take_screenshot("radio5_config_failed")
            return False
