from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class WifiGuestPage(BasePage):
    """Page Object for the WiFi Guest Configuration Page."""

    URL_PATH = "#wifi/details/guest:5:2"

    # Locators
    SSID_INPUT = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(1) > div > div > div > div > div:nth-child(1) > div > div.label-field__content > div > input")
    SECURITY_DROPDOWN = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(1) > div > div > div > div > div:nth-child(4) > div > div.label-field__content > div > div > div > div > div > span.select-placeholder__icon.f-icon.f-icon_select-down")
    SECURITY_NONE_OPTION = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(1) > div > div > div > div > div:nth-child(4) > div > div.label-field__content > div > div > div > div.basic-select__content-container > div > div:nth-child(7)")
    SAVE_BUTTON = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(1) > div > div > div > div > div.group-row.group-row_buttons > div > div:nth-child(2)")

    def navigate(self):
        """Navigates to the WiFi Guest page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to WiFi Guest page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "wifi" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def configure_guest(self, ssid):
        """Changes the SSID and sets security to None, then saves."""
        self.logger.info(f"Configuring WiFi Guest: SSID={ssid}, Security=None")
        try:
            # 1. Clear existing SSID and enter new one
            self.enter_text(self.SSID_INPUT, ssid)
            time.sleep(1)

            # 2. Open security dropdown
            self.click(self.SECURITY_DROPDOWN)
            time.sleep(1)

            # 3. Select None
            self.click(self.SECURITY_NONE_OPTION)
            time.sleep(1)

            # 4. Click Save
            self.click(self.SAVE_BUTTON)
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure WiFi Guest: {e}")
            self.take_screenshot("wifi_guest_config_failed")
            return False
