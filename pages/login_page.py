from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from pages.base_page import BasePage
from utils.config import Config

class LoginPage(BasePage):
    """Page Object for the Login Page."""
    
    # Locators
    USERNAME_INPUT = (By.CSS_SELECTOR, "input.basic-input[placeholder='Username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']") 
    LOGIN_BUTTON = (By.CSS_SELECTOR, "div.login__button")

    def login(self, url=None):
        """Performs the login action at the specified URL or the default BASE_URL."""
        target_url = url if url else Config.BASE_URL
        self.open_url(target_url)
        self.logger.info(f"Attempting login at {target_url}...")
        
        try:
            # 1. Supprimer le contenu par defaut (Delete default content)
            # Using Ctrl+A + Delete to be robust against pre-filled text
            username_element = self.find_element(self.USERNAME_INPUT)
            username_element.click()
            # Windows/Linux uses CONTROL, Mac uses COMMAND. Assuming Windows based on context.
            username_element.send_keys(Keys.CONTROL, "a")
            username_element.send_keys(Keys.DELETE)
            # Ensure it's empty
            username_element.clear()
            
            # 2. Ecrire 'root'
            self.logger.info("Entering 'root' into username")
            username_element.send_keys("root")
            
            # 3. Ecrire 'sah' (Password)
            self.logger.info("Entering 'sah' into password")
            self.enter_text(self.PASSWORD_INPUT, "sah")
            
            # 4. Click Login
            self.click(self.LOGIN_BUTTON)
            self.logger.info("Login submitted.")
            
            # 5. Wait until next page is fully charged
            self.logger.info("Waiting for next page to load...")
            time.sleep(10) 
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise
