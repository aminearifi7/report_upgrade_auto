import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL", "http://192.168.1.1")
    USERNAME = os.getenv("USERNAME", "root")
    PASSWORD = os.getenv("PASSWORD", "sah")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
