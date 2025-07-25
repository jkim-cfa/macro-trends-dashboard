import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShippingIndexScraper:
    def __init__(self):
        self.urls = {
            'CCFI': 'https://www.kcla.kr/web/inc/html/4-1_2.asp',
            'SCFI': 'https://www.kcla.kr/web/inc/html/4-1_3.asp',
            'HRCI': 'https://www.kcla.kr/web/inc/html/4-1_4.asp',
            'BDI': 'https://www.kcla.kr/web/inc/html/4-1_5.asp'
        }
        self.session = requests.Session()
        # Add headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def scrape_index_data(self, url, index_name):
        """Scrape data from a single index page"""
        try:
            logger.info(f"Scraping {index_name} from {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table with the specific structure
            table = soup.find('table', {'summary': index_name})
            if not table:
                # Alternative search - look for table within Guide_Table01 class
                guide_table = soup.find('li', class_='Guide_Table01')
                if guide_table:
                    table = guide_table.find('table')

            if not table:
                logger.error(f"Could not find table for {index_name}")
                return None

            # Extract table data
            rows = table.find('tbody').find_all('tr')
            if len(rows) < 2:
                logger.error(f"Insufficient data rows for {index_name}")
                return None

            # First row contains dates (skip first cell which is "지수")
            date_row = rows[0]
            dates = [td.get_text().strip() for td in date_row.find_all('td')[1:]]

            # Second row contains values
            value_row = rows[1]
            values = [td.get_text().strip() for td in value_row.find_all('td')]

            # Create DataFrame
            if len(dates) == len(values):
                df = pd.DataFrame({
                    'Date': dates,
                    f'{index_name}_Value': values
                })
                df['Index'] = index_name
                logger.info(f"Successfully scraped {len(df)} records for {index_name}")
                return df
            else:
                logger.error(
                    f"Date and value count mismatch for {index_name}: {len(dates)} dates, {len(values)} values")
                return None

        except requests.RequestException as e:
            logger.error(f"Request error for {index_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Parsing error for {index_name}: {e}")
            return None

    def scrape_all_indices(self):
        """Scrape all shipping indices"""
        all_data = []

        for index_name, url in self.urls.items():
            df = self.scrape_index_data(url, index_name)
            if df is not None:
                all_data.append(df)

            # Be polite - add delay between requests
            time.sleep(2)

        return all_data

    def merge_and_save_data(self, data_frames, output_file='shipping_indices.csv'):
        """Merge all data frames and save to CSV"""
        if not data_frames:
            logger.error("No data to save")
            return False

        try:
            # Start with the first dataframe
            merged_df = data_frames[0][['Date', f'{data_frames[0]["Index"].iloc[0]}_Value']].copy()

            # Merge with other dataframes on Date
            for df in data_frames[1:]:
                index_name = df['Index'].iloc[0]
                temp_df = df[['Date', f'{index_name}_Value']].copy()
                merged_df = merged_df.merge(temp_df, on='Date', how='outer')

            # Sort by date
            merged_df['Date'] = pd.to_datetime(merged_df['Date'])
            merged_df = merged_df.sort_values('Date')
            merged_df['Date'] = merged_df['Date'].dt.strftime('%Y.%m.%d')

            # Save to CSV
            merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"Data saved to {output_file}")
            logger.info(f"Total records: {len(merged_df)}")

            # Display summary
            print(f"\n=== SCRAPING SUMMARY ===")
            print(f"Total records saved: {len(merged_df)}")
            print(f"Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
            print(f"Columns: {list(merged_df.columns)}")
            print(f"Output file: {output_file}")

            # Show first few rows
            print(f"\n=== FIRST 5 RECORDS ===")
            print(merged_df.head().to_string(index=False))

            return True

        except Exception as e:
            logger.error(f"Error merging and saving data: {e}")
            return False


def main():
    """Main function to run the scraper"""
    scraper = ShippingIndexScraper()

    print("Starting Korean Shipping Index Scraper...")
    print("Scraping indices: CCFI, SCFI, HRCI, BDI")
    print("-" * 50)

    # Scrape all indices
    data_frames = scraper.scrape_all_indices()

    if data_frames:
        # Merge and save data
        output_dir = os.path.join(data_dir, "trade")
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        output_path = os.path.join(output_dir, "shipping_indices.csv")
        success = scraper.merge_and_save_data(data_frames, output_file=output_path)

        if success:
            print("\n✅ Scraping completed successfully!")
        else:
            print("\n❌ Error occurred while saving data")
    else:
        print("\n❌ No data was scraped")


if __name__ == "__main__":
    main()