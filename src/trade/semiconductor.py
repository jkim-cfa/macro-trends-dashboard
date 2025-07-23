import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR", "data")
    
# Set your desired download directory
DOWNLOAD_DIR = os.path.join(data_dir, "trade")
os.makedirs(os.path.dirname(DOWNLOAD_DIR), exist_ok=True)

TARGET_FILENAME = "wsts_billings_latest.xlsx"

def download_latest():
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Auto-download correct ChromeDriver version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("Opening WSTS Historical Billings Report page...")
        driver.get('https://www.wsts.org/67/Historical-Billings-Report')

        # Wait for page to load
        time.sleep(3)

        # Find and click the Excel download link
        excel_link = driver.find_element(By.XPATH, "//a[contains(@href, '.xlsx')]")

        print(f"Downloading: {excel_link.text}")
        excel_link.click()

        # Wait for the file to download (increase if needed)
        time.sleep(8)

        # Find the latest downloaded file
        downloaded_files = sorted(
            [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.xlsx')],
            key=lambda f: os.path.getmtime(os.path.join(DOWNLOAD_DIR, f))
        )

        if downloaded_files:
            latest_file = os.path.join(DOWNLOAD_DIR, downloaded_files[-1])
            new_file_path = os.path.join(DOWNLOAD_DIR, TARGET_FILENAME)

            os.rename(latest_file, new_file_path)
            print(f"✓ Renamed downloaded file to: {TARGET_FILENAME}")
        else:
            print("No downloaded Excel file found.")

    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    download_latest()
