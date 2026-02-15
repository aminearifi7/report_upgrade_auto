from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class FirewallPage(BasePage):
    """Page Object for the Firewall (Network Security) Configuration Page."""

    URL_PATH = "#networkSecurity/"

    # Locators
    CUSTOM_RADIO = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.network-security-page > div > div > div > div > div > div.page-section__content > div > div.group-item.firewall-levels > div.group-row.group-row_info > div > div:nth-child(4) > div.focus-item.label-radio-checkbox__icon.f-icon.f-icon_radio-checkbox-off")
    APPLY_BUTTON = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.network-security-page > div > div > div > div > div > div.page-section__content > div > div.group-item.firewall-levels > div.group-row.firewall-levels__button.group-row_buttons > div > div:nth-child(2)")

    def navigate(self):
        """Navigates to the Firewall page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to Firewall page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "networksecurity" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def select_custom_mode(self):
        """Selects Custom firewall mode and clicks Apply."""
        self.logger.info("Selecting Custom firewall mode")
        try:
            # 1. Click Custom radio button
            self.click(self.CUSTOM_RADIO)
            time.sleep(1)

            # 2. Click Apply
            self.click(self.APPLY_BUTTON)
            self.wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure Firewall: {e}")
            self.take_screenshot("firewall_config_failed")
            return False
