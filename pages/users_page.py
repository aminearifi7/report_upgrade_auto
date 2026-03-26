from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config

class UsersPage(BasePage):
    """Page Object for the Users Page to manage admin passwords."""
    
    # Locators
    # Using the CSS selectors provided by the user
    ADMIN_PASSWORD_INPUT = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.users-page > div > div > div.page-view__content > div > div > div > div > div > div:nth-child(2) > div > div.label-field__content > div > input")
    ADMIN_PASSWORD_CONFIRM_INPUT = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.users-page > div > div > div.page-view__content > div > div > div > div > div > div:nth-child(3) > div > div.label-field__content > div > input")

    def navigate(self, base_url=None):
        """Navigates to the Users page."""
        target_base = base_url if base_url else Config.BASE_URL
        target_url = f"{target_base}/#users/edit/admin-user"
        self.open_url(target_url)
        self.logger.info(f"Successfully reached Users page: {target_url}")

    def update_admin_password(self, password: str):
        """Updates the admin password using the provided CSS selectors."""
        try:
            self.logger.info(f"Updating admin password to '{password}'...")
            
            # 1. Fill first password field
            self.enter_text(self.ADMIN_PASSWORD_INPUT, password)
            self.logger.info("Entered text into first password field.")
            
            # 2. Fill confirmation password field
            self.enter_text(self.ADMIN_PASSWORD_CONFIRM_INPUT, password)
            self.logger.info("Entered text into second password field.")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update admin password: {e}")
            self.take_screenshot("admin_password_update_failed")
            return False
