from selenium.webdriver.common.by import By
from pages.base_page import BasePage
import time

class LanPage(BasePage):
    """Page Object for the LAN Settings Page."""
    
    # Locators
    URL = "http://192.168.1.1/#lan/"
    
    # Using the specific selectors provided by the user
    IP_INPUT_1 = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.page-lan.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div:nth-child(2) > div > div:nth-child(1) > div > div.label-field__content > div > input")
    IP_INPUT_2 = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.page-lan.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div:nth-child(2) > div > div:nth-child(3) > div > div.label-field__content > div > input")
    IP_INPUT_3 = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.page-view-container.page-lan.page-view-container_large-page > div > div > div > div > div.page-section__content > div > div:nth-child(2) > div > div:nth-child(4) > div > div.label-field__content > div > input")
    
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(normalize-space(), 'Apply')]")
    OK_BUTTON = (By.ID, "popup-ok")

    def navigate(self):
        """Navigates to the LAN page."""
        self.logger.info(f"Navigating to LAN page: {self.URL}")
        self.driver.get(self.URL)
        self.wait_for_page_load()
        time.sleep(3) # Ensure dynamic elements are truly ready

    def configure_ips(self, ip1, ip2, ip3):
        """Clears and sets the three IP input fields."""
        self.logger.info(f"Configuring IPs: {ip1}, {ip2}, {ip3}")
        
        # IP 1
        self.enter_text(self.IP_INPUT_1, ip1)
        
        # IP 2
        self.enter_text(self.IP_INPUT_2, ip2)
        
        # IP 3
        self.enter_text(self.IP_INPUT_3, ip3)

    def apply_changes(self):
        """Clicks Apply and confirms with Ok button, then waits 10s."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self.logger.info("Applying LAN changes...")
        
        try:
            # 1. Click Apply directly (or use BasePage logic if preferred, but user wanted speed before)
            # Reverting slightly to be more robust but keeping it direct enough
            apply_btn = self.find_element(self.APPLY_BUTTON)
            apply_btn.click()
            self.logger.info("Clicked Apply button.")
            
            # 2. Wait for Ok button to appear and click it
            self.logger.info("Waiting for Ok confirmation popup...")
            ok_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(self.OK_BUTTON)
            )
            ok_btn.click()
            self.logger.info("Clicked Ok button.")
            
            # 3. Wait until the page reloads or settles
            self.logger.info("Waiting for page to reload after apply...")
            # Small buffer to allow browser to register the click/unload start
            time.sleep(1) 
            self.wait_for_page_load()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply LAN changes: {e}")
            self.take_screenshot("lan_apply_failed")
            return False
