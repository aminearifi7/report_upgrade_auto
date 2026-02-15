from selenium import webdriver
from utils.config import Config

def get_driver():
    """Initializes and returns a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    if Config.HEADLESS:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
    # Selenium 4.10+ handles driver management automatically
    driver = webdriver.Chrome(options=options)
    return driver
