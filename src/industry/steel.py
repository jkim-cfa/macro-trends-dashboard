from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR", "data")


def initialize_browser():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver


def clean_span_text(element: WebElement, driver):
    # Remove all <sup> tags
    driver.execute_script("arguments[0].querySelectorAll('sup').forEach(s => s.remove())", element)
    return element.text.strip()

def region_table(driver):
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//sro-table[@table='3']"))
    )

    rows = container.find_elements(By.CSS_SELECTOR, "div.sdv-ranking-body > div.sdv-ranking-row")

    data = []
    for row in rows:
        cells = [clean_span_text(el, driver) for el in row.find_elements(By.TAG_NAME, "span")]
        if len(cells) >= 3:
            data.append({
                "Region": cells[0],
                "May 2025 YoY (%)": cells[1],
                "Jan–May 2025 YoY (%)": cells[2]
            })
    return data

def country_table(driver):
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//sro-table[@table='4']"))
    )

    rows = container.find_elements(By.CSS_SELECTOR, "div.sdv-ranking-body > div.sdv-ranking-row")

    data = []
    for row in rows:
        cells = [clean_span_text(el, driver) for el in row.find_elements(By.TAG_NAME, "span")]
        if len(cells) >= 3:
            data.append({
                "Country": cells[0],
                "May 2025 YoY (%)": cells[1],
                "Jan–May 2025 YoY (%)": cells[2]
            })
    return data

def main():
    base_url = "https://worldsteel.org/data/steel-data-viewer/?ind=CSP-PERC/"
    driver = initialize_browser()
    driver.get(base_url)

    try:
        region_data = region_table(driver)
        country_data = country_table(driver)

        # Convert both to DataFrames
        region_df = pd.DataFrame(region_data)
        region_df["Scope"] = "Region"

        country_df = pd.DataFrame(country_data)
        country_df = country_df.rename(columns={"Country": "Region"})  # unifies column name
        country_df["Scope"] = "Country"

        # Combine
        combined_df = pd.concat([region_df, country_df], ignore_index=True)

        # Save
        output_path = os.path.join(data_dir, "industry", "steel_combined.csv")
        combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"Data saved to {output_path}.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
