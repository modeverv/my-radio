from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys

def debug_chrome():
    chrome_options = Options()
    project_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(project_dir, "chrome_profile")
    
    print(f"Profile Path: {user_data_dir}")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # Try with additional flags for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        print("Installing/Checking ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"Driver Path: {driver_path}")
        
        service = Service(driver_path)
        print("Starting Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.google.com")
        print("Successfully opened Google!")
        driver.quit()
    except Exception as e:
        print("\n--- ERROR DETECTED ---")
        print(e)
        print("-----------------------")

if __name__ == "__main__":
    debug_chrome()
