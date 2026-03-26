from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from utils.config import Config

def get_driver():
    """Initializes and returns a Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if Config.HEADLESS:
        options.add_argument("--headless=new")  # nouveau flag headless Chrome 112+
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    # Force fresh download matching installed Chrome version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver