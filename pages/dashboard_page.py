from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
import time

class DashboardPage(BasePage):
    """Page Object for the Dashboard Page."""
    
    # Locators
    # The element showing the current mode (Basic or Advanced)
    MODE_MENU_VALUE = (By.CSS_SELECTOR, "div.mode-ui-menu__value")
    
    # The option in the dropdown to select Advanced
    ADVANCED_OPTION = (By.XPATH, "//div[contains(@class, 'header-menu-popup__menu-item') and contains(text(), 'Advanced')]")

    def ensure_advanced_mode(self):
        """
        Checks the current mode. If 'Basic', switches to 'Advanced'.
        """
        from selenium.webdriver.common.action_chains import ActionChains  # Import locally to avoid circular deps if any
        
        self.logger.info("Checking Dashboard Mode (Basic/Advanced)...")
        
        try:
            # 1. Wait for Mode Menu Value to appear
            self.logger.info("Waiting for Mode Menu Value to appear...")
            mode_element = self.find_element(self.MODE_MENU_VALUE)
            
            # 2. Get current mode text
            current_mode = mode_element.text.strip()
            self.logger.info(f"Current mode is: '{current_mode}'")
            
            # 3. If already in Advanced mode, return
            if "Advanced" in current_mode:
                self.logger.info("Already in Advanced mode.")
                return True
            
            # 4. If in Basic mode, click to open the menu
            if "Basic" in current_mode:
                self.logger.info("Currently in Basic mode. Clicking on 'Basic' to open menu...")
                mode_element.click()
                
                # 5. Wait for the Advanced option to be visible and clickable
                self.logger.info("Waiting for 'Advanced' option in menu...")
                wait = WebDriverWait(self.driver, 10)
                advanced_option = wait.until(
                    EC.element_to_be_clickable(self.ADVANCED_OPTION)
                )
                
                # Debug: Log all menu items
                try:
                    menu_items = self.driver.find_elements(By.CSS_SELECTOR, "div.header-menu-popup__menu-item")
                    self.logger.info(f"Found {len(menu_items)} menu items")
                    for idx, item in enumerate(menu_items):
                        self.logger.info(f"  Menu item {idx}: '{item.text}'")
                except Exception as debug_e:
                    self.logger.warning(f"Debug logging failed: {debug_e}")
                
                # 6. Click on Advanced option (Using ActionChains for robust interaction)
                self.logger.info("Clicking on 'Advanced' option via ActionChains...")
                ActionChains(self.driver).move_to_element(advanced_option).click().perform()
                
                # 7. Wait for the mode to change
                self.logger.info("Waiting for mode switch to complete...")
                time.sleep(2)
                
                # 8. Verify the switch was successful
                mode_element = self.find_element(self.MODE_MENU_VALUE)
                new_mode = mode_element.text.strip()
                
                if "Advanced" in new_mode:
                    self.logger.info("Successfully switched to Advanced mode.")
                    return True
                else:
                    self.logger.warning(f"Mode switch verification failed. Current text: '{new_mode}'")
                    return False
            else:
                self.logger.warning(f"Unexpected mode value: '{current_mode}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to switch mode: {e}")
            raise