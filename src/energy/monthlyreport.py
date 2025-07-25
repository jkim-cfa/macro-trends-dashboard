import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR")
    
# Set your desired download directory
DOWNLOAD_DIR = os.path.abspath(os.path.join(data_dir, "energy"))
os.makedirs(os.path.dirname(DOWNLOAD_DIR), exist_ok=True)

def download_latest_momr():
    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options, headless=False)

    try:
        # Step 1: Go to OPEC landing page
        driver.get('https://www.opec.org/monthly-oil-market-report.html')

        # Step 2: Wait for and click the "Download latest MOMR" link
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'momr.opec.org/pdf-download')]"))
        )
        pdf_page_url = link.get_attribute("href")
        print("Navigating to:", pdf_page_url)

        driver.get(pdf_page_url)

        # Step 3: Wait for and click the data policy acceptance button
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Accept OPEC Data Policy Disclaimer')]"))
        )
        accept_btn.click()
        print("Accepted data policy.")

        # Step 4: Wait for download to start (or finish)
        time.sleep(10)  # increase if download is slow
        print(f"Download initiated to: {DOWNLOAD_DIR}")


    finally:
        driver.quit()
        del driver  # prevent __del__ from running later and causing WinError
        print("Browser closed.")

if __name__ == "__main__":
    download_latest_momr()
        
    # Find the newest PDF file in the download directory
    downloaded_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.pdf')]
    downloaded_files.sort(key=lambda f: os.path.getmtime(os.path.join(DOWNLOAD_DIR, f)), reverse=True)

    if downloaded_files:
        original_path = os.path.join(DOWNLOAD_DIR, downloaded_files[0])
        renamed_path = os.path.join(DOWNLOAD_DIR, 'OPEC_MOMR_Latest.pdf')
        os.rename(original_path, renamed_path)
        print(f"Renamed downloaded file to: {renamed_path}")
    else:
        print("No PDF found to rename.")
