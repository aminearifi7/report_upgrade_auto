from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class NtpPage(BasePage):
    """Page Object for the NTP (Network Time Protocol) Configuration Page."""

    URL_PATH = "#wan/3"

    # Locators
    TIMEZONE_DROPDOWN = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.page-wan.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div > div:nth-child(3) > div > div.label-select-input > div > div.label-field__content > div > div.label-select__select > div > div > div > span.select-placeholder__icon.f-icon.f-icon_select-down")
    TIMEZONE_UTC_MINUS4 = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.page-wan.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div > div:nth-child(3) > div > div.label-select-input > div > div.label-field__content > div > div.label-select__select > div > div.basic-select__content-container > div > div:nth-child(27)")
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(text(), 'Apply')]")

    def navigate(self):
        """Navigates to the NTP page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to NTP page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "wan" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def select_timezone_utc_minus4(self):
        """Selects UTC-4 (America: Campo Grande, Cuiaba) timezone and clicks Apply."""
        self.logger.info("Selecting timezone UTC-4 (America: Campo Grande, Cuiaba)")
        try:
            # 1. Open timezone dropdown
            self.click(self.TIMEZONE_DROPDOWN)
            time.sleep(1)

            # 2. Select UTC-4 option (nth-child 27)
            self.click(self.TIMEZONE_UTC_MINUS4)
            time.sleep(1)

            # 3. Click Apply
            self.click(self.APPLY_BUTTON)
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure NTP timezone: {e}")
            self.take_screenshot("ntp_config_failed")
            return False
