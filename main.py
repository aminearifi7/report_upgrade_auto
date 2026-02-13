"""
Main entry point for Home Gateway Upgrade Report automation.
Orchestrates: Login -> Switch to Advanced Mode.
"""
from utils.driver_factory import get_driver
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.lan_page import LanPage
from pages.wifi_page import WifiPage
from pages.wifi24_page import Wifi24Page
from pages.wifi5_page import Wifi5Page
from pages.wifi6_page import Wifi6Page
from pages.base_page import RecoveryHandledException
from utils.logger import Logger
from utils.config import Config
import time

def main():
    """Main orchestration function."""
    logger = Logger().get_logger()
    driver = None
    
    try:
        logger.info("=" * 60)
        logger.info("Starting Home Gateway Upgrade Report Automation")
        logger.info("Target URL: " + Config.BASE_URL)
        logger.info("=" * 60)
        
        # Initialize driver
        logger.info("Initializing WebDriver...")
        driver = get_driver()
        
        # 1. LOGIN PHASE
        logger.info("\n--- STEP 1: LOGIN ---")
        login_page = LoginPage(driver)
        
        # Perform login (internally navigates to Config.BASE_URL)
        login_page.login()
        
        # 2. DASHBOARD MODE SWITCH
        logger.info("\n--- STEP 2: SWITCH TO ADVANCED MODE ---")
        dashboard_page = DashboardPage(driver)
        
        # Wait for dashboard to load after login
        dashboard_page.wait_for_page_load()
        
        # Perform mode switch if necessary
        if dashboard_page.ensure_advanced_mode():
            logger.info("Successfully reached Advanced Mode.")
        else:
            logger.warning("Could not verify Advanced Mode switch.")
            
        # 3. LAN PAGE CONFIGURATION
        logger.info("\n--- STEP 3: LAN PAGE CONFIGURATION ---")
        lan_page = LanPage(driver)
        
        # Navigate to LAN page
        lan_page.navigate()
        
        # Configure IPs
        lan_page.configure_ips("192.168.3.5", "192.168.3.6", "192.168.3.250")
        
        # Apply changes
        if lan_page.apply_changes():
            logger.info("LAN configuration applied and confirmed.")
        else:
            logger.error("LAN configuration failed.")
            
        # 4. RE-LOGIN AT NEW IP
        logger.info("\n--- STEP 4: RE-LOGIN AT NEW IP ---")
        new_ip = "192.168.3.5"
        new_url = f"http://{new_ip}"
        
        logger.info(f"Waiting 30 seconds for gateway to stabilize at {new_ip}...")
        time.sleep(30)
        
        logger.info(f"Attempting re-login at {new_url}...")
        login_page.login(url=new_url)
        
        # 5. NAVIGATE TO NEW IP WIFI PAGE
        logger.info("\n--- STEP 5: NAVIGATE TO NEW IP WIFI PAGE ---")
        new_ip_wifi_url = f"{new_url}/#wifi/"
        logger.info(f"Navigating to new IP WiFi page: {new_ip_wifi_url}")
        driver.get(new_ip_wifi_url)
        
        # Instantiate WifiPage
        wifi_page = WifiPage(driver)
        wifi_page.wait_for_page_load()
        logger.info(f"Successfully reached WiFi page at new IP: {new_ip_wifi_url}")
        
        # 6. SPLIT WIFI VAPS
        logger.info("\n--- STEP 6: SPLIT WIFI VAPS ---")
        if wifi_page.split_vaps():
            logger.info("WiFi VAPs split successfully.")
        else:
            logger.error("Failed to split WiFi VAPs.")
        
        # 7. WIFI 2.4GHz DETAILS PHASE
        logger.info("\n--- WIFI 2.4GHz DETAILS PHASE ---")
        wifi24_page = Wifi24Page(driver)
        
        try:
            # 1. Navigate to WiFi 2.4GHz details URL
            wifi24_page.navigate()
            wifi24_page.take_screenshot("11_wifi24_details_loaded")
            
            # 2. Update SSID to amine_prpl_24 and 3. Password to amine123
            if wifi24_page.update_ssid_and_password("amine_prpl_24", "amine123"):
                wifi24_page.take_screenshot("12_ssid_password_updated")
            
            # 4 & 5 & 6 & 7. Select WPA3, Save, and Re-navigate
            if wifi24_page.select_security_wpa3():
                wifi24_page.take_screenshot("13_security_saved_and_re-navigated")
            
        except RecoveryHandledException:
            logger.warning("Main WiFi 2.4GHz configuration interrupted by popup. Skipping to MAC filtering.")

        # 8 & 9. MAC Filtering Radios
        try:
            logger.info("Setting MAC Filtering to 'Allow'...")
            if wifi24_page.toggle_radio_and_apply(locator=wifi24_page.MAC_FILTER_ALLOW_RADIO):
                wifi24_page.take_screenshot("14_mac_filter_allow_applied")

            logger.info("Setting MAC Filtering to 'Disable'...")
            if wifi24_page.toggle_radio_and_apply(locator=wifi24_page.MAC_FILTER_DISABLE_RADIO):
                wifi24_page.take_screenshot("15_mac_filter_disable_applied")
        except RecoveryHandledException:
            logger.warning("MAC Filter toggle interrupted by popup. skipping to device selection.")
            
        # 10. Select first device from dynamic list and Apply
        try:
            logger.info("Selecting first device from dynamic list and applying...")
            if wifi24_page.select_first_device_and_apply():
                wifi24_page.take_screenshot("16_device_selected_and_applied")
        except RecoveryHandledException:
            logger.warning("Device selection interrupted by popup. Finishing automation.")

        # Intermediate stability step: Navigate to main WiFi page
        logger.info("Stability step: Navigating to main WiFi page before next band...")
        wifi_page.navigate(base_url=new_url)

        # 8. WIFI 5GHz DETAILS PHASE
        logger.info("\n--- WIFI 5GHz DETAILS PHASE ---")
        wifi5_page = Wifi5Page(driver)
        
        try:
            # 1. Navigate to WiFi 5GHz details URL
            wifi5_page.navigate()
            wifi5_page.take_screenshot("17_wifi5_details_loaded")
            
            # 2. Update SSID to amine_prpl_5ghz and 3. Password to amine123
            if wifi5_page.update_ssid_and_password("amine_prpl_5ghz", "amine123"):
                wifi5_page.take_screenshot("18_wifi5_ssid_password_updated")
            
            # 4 & 5 & 6 & 7. Select WPA3, Save, and Re-navigate
            if wifi5_page.select_security_wpa3():
                wifi5_page.take_screenshot("19_wifi5_security_saved_and_re-navigated")
            
            # 8 & 9. MAC Filtering Radios (Allow -> Disable)
            try:
                logger.info("Setting WiFi 5GHz MAC Filtering to 'Allow'...")
                if wifi5_page.toggle_radio_and_apply(locator=wifi5_page.MAC_FILTER_ALLOW_RADIO):
                    wifi5_page.take_screenshot("20_wifi5_mac_filter_allow_applied")

                logger.info("Setting WiFi 5GHz MAC Filtering to 'Disable'...")
                if wifi5_page.toggle_radio_and_apply(locator=wifi5_page.MAC_FILTER_DISABLE_RADIO):
                    wifi5_page.take_screenshot("21_wifi5_mac_filter_disable_applied")
            except RecoveryHandledException:
                logger.warning("WiFi 5GHz MAC Filter toggle interrupted by popup. Skipping to device selection.")

            # 10. Select first device from dynamic list and Apply
            try:
                logger.info("Selecting first device from WiFi 5GHz dynamic list and applying...")
                if wifi5_page.select_first_device_and_apply():
                    wifi5_page.take_screenshot("22_wifi5_device_selected_and_applied")
            except RecoveryHandledException:
                logger.warning("WiFi 5GHz device selection interrupted by popup.")

        except RecoveryHandledException:
            logger.warning("WiFi 5GHz configuration interrupted by popup. Skipping to final steps.")

        # Intermediate stability step: Navigate to main WiFi page
        logger.info("Stability step: Navigating to main WiFi page and wait 5s...")
        wifi_page.navigate(base_url=new_url)
        time.sleep(5)

        # 9. WIFI 6GHz DETAILS PHASE
        logger.info("\n--- WIFI 6GHz DETAILS PHASE ---")
        wifi6_page = Wifi6Page(driver)
        
        try:
            # 1. Navigate to WiFi 6GHz details URL
            wifi6_page.navigate()
            wifi6_page.take_screenshot("23_wifi6_details_loaded")
            
            # 2. Update SSID to amine_prpl_6ghz and 3. Password to amine123
            if wifi6_page.update_ssid_and_password("amine_prpl_6ghz", "amine123"):
                wifi6_page.take_screenshot("24_wifi6_ssid_password_updated")
            
            # 4 & 5 & 6 & 7. Select WPA3, Save, and Re-navigate
            if wifi6_page.select_security_wpa3():
                wifi6_page.take_screenshot("25_wifi6_security_saved_and_re-navigated")
            
            # 8 & 9. MAC Filtering Radios (Allow -> Disable)
            try:
                logger.info("Setting WiFi 6GHz MAC Filtering to 'Allow'...")
                if wifi6_page.toggle_radio_and_apply(locator=wifi6_page.MAC_FILTER_ALLOW_RADIO):
                    wifi6_page.take_screenshot("26_wifi6_mac_filter_allow_applied")

                logger.info("Setting WiFi 6GHz MAC Filtering to 'Disable'...")
                if wifi6_page.toggle_radio_and_apply(locator=wifi6_page.MAC_FILTER_DISABLE_RADIO):
                    wifi6_page.take_screenshot("27_wifi6_mac_filter_disable_applied")
            except RecoveryHandledException:
                logger.warning("WiFi 6GHz MAC Filter toggle interrupted by popup. Skipping to device selection.")

            # 10. Select first device from dynamic list and Apply
            try:
                logger.info("Selecting first device from WiFi 6GHz dynamic list and applying...")
                if wifi6_page.select_first_device_and_apply():
                    wifi6_page.take_screenshot("28_wifi6_device_selected_and_applied")
            except RecoveryHandledException:
                logger.warning("WiFi 6GHz device selection interrupted by popup.")

        except RecoveryHandledException:
            logger.warning("WiFi 6GHz configuration interrupted by popup. Finishing automation.")

        # Final stability step
        logger.info("Final stability step: Navigating to main WiFi page and wait 5s...")
        wifi_page.navigate(base_url=new_url)
        time.sleep(5)

        logger.info("\n" + "=" * 60)
        logger.info("All automation steps completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Automation failed during initial steps: {e}")
        if driver:
            try:
                driver.save_screenshot("screenshots/main_error.png")
                logger.info("Error screenshot saved to screenshots/main_error.png")
            except:
                pass
        raise
        
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()
            logger.info("Browser closed.")

if __name__ == "__main__":
    main()
