from selenium.webdriver.common.by import By
from pages.base_page import BasePage, RecoveryHandledException
from utils.config import Config
import time

class Wifi5Page(BasePage):
    """Page Object for the WiFi 5GHz Details Page."""

    # URL
    URL_PATH = "#wifi/details/private:5"

    # Locators (Assuming identical structure to 2.4GHz)
    SSID_INPUT = (By.CSS_SELECTOR, "input.basic-input[type='text']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input.basic-input[type='password']")
    SECURITY_DROPDOWN_ICON = (By.XPATH, "//div[contains(@class, 'select-placeholder')]//span[contains(@class, 'f-icon_select')]")
    WPA3_PERSONAL_OPTION = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(1) > div > div > div > div > div:nth-child(4) > div > div.label-field__content > div > div > div > div.basic-select__content-container > div > div:nth-child(2) > span")
    
    DEVICE_INPUT = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(2) > div > div > div:nth-child(2) > div.wifi-mac-filtering-form > div > div.field-placeholder.wifi-mac-filtering-form__devices > div.label-select-input > div > div > div > div.label-select__select > div > div.focus-item.basic-select__selection > div.label-field.label-input.label-select-input__input.label-field_no-label.label-field_no-status > div > div > input")
    DEVICE_LIST_ITEM = (By.CSS_SELECTOR, "div.select-option, div.basic-select__item, div.basic-select__content-container div span")
    ADD_BUTTON = (By.CSS_SELECTOR, "div.f-icon_add")
    
    RADIO_CHECKBOX_OFF = (By.CSS_SELECTOR, "div.f-icon_radio-checkbox-off")
    RADIO_CHECKBOX_ON = (By.CSS_SELECTOR, "div.f-icon_radio-checkbox-on")
    RADIO_TOGGLE = (By.CSS_SELECTOR, "div.label-radio-checkbox__icon")
    
    # MAC Filtering specific
    MAC_FILTER_ALLOW_RADIO = (By.XPATH, "//*[@id='app-app-hgw']/div/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div/div[1]/div[1]")
    MAC_FILTER_DISABLE_RADIO = (By.CSS_SELECTOR, "#app-app-hgw > div > div.page__container > div.main-content.page__main-content > div.wifi-page > div > div > div.page-view__content > div:nth-child(2) > div > div > div.group-item.mac-filtering-mode > div.group-row.group-row_default > div > div:nth-child(3) > div.focus-item.label-radio-checkbox__icon.f-icon.f-icon_radio-checkbox-off")
    
    APPLY_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and contains(text(), 'Apply')]")
    SAVE_BUTTON = (By.XPATH, "//div[contains(@class, 'button-basic') and (contains(text(), 'Save') or contains(text(), 'SAVE'))]")

    def navigate(self):
        """Navigates to the WiFi 5GHz details page."""
        url = f"{Config.BASE_URL}/{self.URL_PATH}"
        self.logger.info(f"Navigating to WiFi 5GHz details page: {url}")
        
        # Robust navigation with retry if redirected to dashboard
        self.driver.get(url)
        time.sleep(3)
        
        if "details" not in self.driver.current_url.lower():
             self.logger.warning("Redirected? Attempting direct navigation again...")
             self.driver.get(url)
             time.sleep(3)
             
        self.wait_for_page_load()

    def update_ssid_and_password(self, ssid, password):
        """Changes the SSID and Password with clearing."""
        self.logger.info(f"Changing SSID to {ssid} and Password to {password}")
        try:
            # SSID
            ssid_elem = self.find_element(self.SSID_INPUT)
            ssid_elem.clear()
            ssid_elem.send_keys(ssid)
            
            # Password
            pass_elem = self.find_element(self.PASSWORD_INPUT)
            pass_elem.clear()
            pass_elem.send_keys(password)
            return True
        except RecoveryHandledException:
            self.logger.warning("Recovery happened during WiFi 5GHz SSID/Password update.")
            return False

    def select_security_wpa3(self):
        """Selects WPA3 Personal security mode and clicks Save."""
        self.logger.info("Selecting WPA3 Personal security mode for WiFi 5GHz")
        try:
            # 1. Open menu
            self.click(self.SECURITY_DROPDOWN_ICON)
            time.sleep(1) # Wait for menu
            
            # 2. Click WPA3 Personal option
            self.click(self.WPA3_PERSONAL_OPTION)
            time.sleep(1) 
            
            # 3. Click Save
            time.sleep(1.5) # Stability wait
            self.click(self.SAVE_BUTTON)
            
            # 4. Wait for redirect
            self.logger.info("Waiting 10 seconds for automatic redirect/processing...")
            time.sleep(10)
            
            # 5. Re-navigate
            self.logger.info("Re-navigating to WiFi 5GHz details page...")
            self.navigate()
            
            return True
        except RecoveryHandledException:
            self.logger.warning("Recovery happened during WiFi 5GHz security mode selection/save.")
            return False

    def select_first_device_and_apply(self):
        """Clicks device input, chooses the first device if any, clicks Add, then Apply."""
        self.logger.info("Attempting to select the first available device for WiFi 5GHz, add it, and apply")
        try:
            # 1. Click the input to open the list
            self.click(self.DEVICE_INPUT)
            time.sleep(2) # Wait for dynamic list to populate
            
            # 2. Find options
            options = self.driver.find_elements(*self.DEVICE_LIST_ITEM)
            if options:
                self.logger.info(f"Found {len(options)} device options. Selecting the first one.")
                target_option = options[0]
                self.driver.execute_script("arguments[0].scrollIntoView(true);", target_option)
                time.sleep(1)
                
                target_option.click() 
                time.sleep(1)
                
                # 3. Click Add Button
                self.logger.info("Clicking Add button...")
                self.click(self.ADD_BUTTON)
                time.sleep(1)
                
                # 4. Click Apply
                self.logger.info("Clicking Apply button...")
                self.click(self.APPLY_BUTTON)
                self.wait_for_page_load()
                time.sleep(2)
                return True
            else:
                self.logger.info("No device entries found in the list. Skipping selection for WiFi 5GHz.")
                return True
        except RecoveryHandledException:
            self.logger.warning("Recovery happened during WiFi 5GHz device selection/addition.")
            return False
        except Exception as e:
            self.logger.error(f"Failed to select/add device for WiFi 5GHz: {e}")
            return False

    def toggle_radio_and_apply(self, index=0, locator=None):
        """Clicks the radio/checkbox toggle and then Apply."""
        target_loc = locator if locator else self.RADIO_TOGGLE
        self.logger.info(f"Toggling radio/checkbox (locator: {target_loc}, index: {index}) for WiFi 5GHz and applying")
        
        try:
            if locator:
                self.click(locator)
            else:
                toggles = self.driver.find_elements(*self.RADIO_TOGGLE)
                if len(toggles) > index:
                    toggles[index].click()
                else:
                    self.logger.warning(f"No radio/checkbox found at index {index} for WiFi 5GHz")
                    return False
                
            time.sleep(1.5) # Increased stability wait
            self.click(self.APPLY_BUTTON)
            self.wait_for_page_load()
            return True
        except RecoveryHandledException:
            self.logger.warning(f"Recovery happened during WiFi 5GHz radio toggle at index {index}.")
            return False
        except Exception as e:
            self.logger.error(f"Failed to toggle radio for WiFi 5GHz: {e}")
            return False
