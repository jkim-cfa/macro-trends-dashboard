from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re, os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR", "data")

def initialize_browser():
    """Initialize a Chrome WebDriver instance with predefined options."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_hidden_chart_data(driver):
    """Extract data from hidden or visible chart elements using JavaScript."""
    data = {}
    try:
        script = """
        return Array.from(document.querySelectorAll('g.highcharts-data-labels text')).map(el => el.textContent.trim());
        """
        chart_texts = driver.execute_script(script)
        for text in chart_texts:
            match = re.match(r"(.+?)(\d+\.?\d*%)$", text)
            if match:
                resource, percentage = match.groups()
                data[resource.strip()] = percentage.strip()
    except Exception as e:
        print(f"Error scraping chart data: {e}")
    return data

def scrape_year(driver):
    """Extract the year from the page based on specific text patterns."""
    try:
        year_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'a-box-title') and contains(text(), 'Total energy supply')]"))
        )
        year_text = year_element.text
        match = re.search(r"\b(\d{4})\b", year_text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None

def scrape_global_emissions(driver):
    """Extract global emissions percentage from the page."""
    try:
        emissions_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'f-title-2') and contains(text(), '%')]"))
        )
        emissions_text = emissions_element.text
        match = re.match(r"(\d+\.?\d*)%", emissions_text)
        if match:
            return match.group(1) + "%"
    except Exception:
        pass
    return None

def click_electricity_button(driver, timeout=10):
    """Click the 'Electricity' button on the page to reveal additional data."""
    try:
        electricity_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'a-button') and span[contains(text(), 'Electricity')]]"))
        )
        electricity_button.click()
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//g.highcharts-data-labels"))  # Wait for the chart data to load
        )
    except Exception:
        print("Electricity button not found or could not be clicked.")

def scrape_country_data(driver, url):
    """Scrape data for a specific country from its page."""
    driver.get(url)

    country_name = url.split("/")[-1].replace("-", " ").title()
    country_data = {"Country": country_name}

    try:
        year = scrape_year(driver)
        if year:
            country_data["Year"] = year

        global_emissions = scrape_global_emissions(driver)
        if global_emissions:
            country_data["Global Emissions"] = global_emissions

        energy_supplied_data = scrape_hidden_chart_data(driver)
        if energy_supplied_data:
            country_data.update({"Energy Supplied " + k: v for k, v in energy_supplied_data.items()})

        click_electricity_button(driver)
        electricity_data = scrape_hidden_chart_data(driver)
        if electricity_data:
            country_data.update({"Electricity " + k: v for k, v in electricity_data.items()})
    except Exception as e:
        print(f"Error scraping country data for {url}: {e}")

    return country_data

def scrape_continent(driver, continent_url, continent_name):
    """Scrape data for all countries within a continent."""
    driver.get(continent_url)

    country_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'm-country-listing__link')]"))
    )
    country_links = [a.get_attribute("href") for a in country_links]

    continent_data = []
    for country_url in country_links:
        country_data = scrape_country_data(driver, country_url)
        continent_data.append(country_data)

    return continent_data

def main():
    base_url = "https://www.iea.org"
    regions_url = f"{base_url}/countries"
    driver = initialize_browser()

    all_data = []

    try:
        driver.get(regions_url)

        # Extract links and names of continents
        continent_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'm-regions-listing__link')]"))
        )
        continent_links = [
            (a.get_attribute("href"), a.find_element(By.TAG_NAME, "h3").text)
            for a in continent_links
        ]

        print(f"Found {len(continent_links)} continents to scrape.")

        # Scrape each continent
        for continent_url, continent_name in continent_links:
            print(f"Scraping continent: {continent_name}...")
            continent_data = scrape_continent(driver, continent_url, continent_name)
            all_data.extend(continent_data)

    finally:
        driver.quit()
        print("Browser closed.")

    # Save all data to a CSV file relative to the script
    output_file_path = os.path.join(data_dir, "energy", "global_energy_data.csv")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    df = pd.DataFrame(all_data)
    df.to_csv(output_file_path, index=False, encoding="utf-8-sig")
    print(f"Data saved to {output_file_path}.")

if __name__ == "__main__":
    main()