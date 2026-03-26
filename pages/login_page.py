from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            wait = WebDriverWait(self.driver, 20)

            # Wait for Vue.js to finish mounting before interacting
            time.sleep(2)

            # 1. Wait until username input is clickable (overlay dismissed)
            username_element = wait.until(
                EC.element_to_be_clickable(self.USERNAME_INPUT)
            )

            # Use JS click to bypass any residual overlay
            self.driver.execute_script("arguments[0].click();", username_element)
            username_element.send_keys(Keys.CONTROL, "a")
            username_element.send_keys(Keys.DELETE)
            username_element.clear()
            
            # 2. Enter 'root'
            self.logger.info("Entering 'root' into username")
            username_element.send_keys("root")
            
            # 3. Enter password
            self.logger.info("Entering 'sah' into password")
            password_element = wait.until(
                EC.element_to_be_clickable(self.PASSWORD_INPUT)
            )
            self.driver.execute_script("arguments[0].click();", password_element)
            password_element.clear()
            password_element.send_keys("sah")
            
            # 4. Click Login
            login_btn = wait.until(
                EC.element_to_be_clickable(self.LOGIN_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", login_btn)
            self.logger.info("Login submitted.")
            
            # 5. Wait until next page is fully loaded
            self.logger.info("Waiting for next page to load...")
            time.sleep(10) 
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise