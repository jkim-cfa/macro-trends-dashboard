import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set your desired download directory
DOWNLOAD_DIR = os.path.abspath(r"C:/Users/va26/Desktop/global event/data/energy")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
