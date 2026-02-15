from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config
import time

class DyndnsPage(BasePage):
    """Page Object for the DynDNS Configuration Page."""

    URL_PATH = "#wan/2"

    # Locators
    SERVICE_DROPDOWN = (By.CSS_SELECTOR, "div.dyndns-service span.f-icon_select-down")
    SERVICE_OPTION_CHANGEIP = (By.CSS_SELECTOR, ".basic-select__content-container div:nth-child(65)")
    HOSTNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Hostname']")
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='Password']")
    ADD_BUTTON = (By.CSS_SELECTOR, "div.f-icon_add")

    def navigate(self):
        """Navigates to the DynDNS page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to DynDNS page: {url}")
        
        self.driver.get(url)
        time.sleep(3)
        
        if "wan" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def add_dyndns_client(self, hostname, username, password):
        """Adds a DynDNS client with the provided credentials."""
        self.logger.info(f"Adding DynDNS client: {hostname}")
        try:
            # 1. Open service dropdown
            self.click(self.SERVICE_DROPDOWN)
            time.sleep(1)

            # 2. Select changeip.com (option 65)
            self.click(self.SERVICE_OPTION_CHANGEIP)
            time.sleep(1)

            # 3. Fill Hostname
            self.enter_text(self.HOSTNAME_INPUT, hostname)
            
            # 4. Fill Username
            self.enter_text(self.USERNAME_INPUT, username)
            
            # 5. Fill Password
            self.enter_text(self.PASSWORD_INPUT, password)
            
            # 6. Click Add button
            self.click(self.ADD_BUTTON)
            self.wait_for_page_load()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to add DynDNS client: {e}")
            self.take_screenshot("dyndns_add_failed")
            return False
