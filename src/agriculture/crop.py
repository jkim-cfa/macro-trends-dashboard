import requests
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR")    

# Parameters
api_key = os.getenv('CROP_API_KEY')
base_url = 'https://api.fas.usda.gov/api/psd/commodity'
start_year = 2000
end_year = int(datetime.now().year)

# Commodities
commodity_code = [
    {'commodityCode': '0410000', 'commodityName': 'Wheat'},
    {'commodityCode': '0440000', 'commodityName': 'Corn'},
    {'commodityCode': '2222000', 'commodityName': 'Soybean'},
    {'commodityCode': '0011000', 'commodityName': 'Cattle'},
    {'commodityCode': '0422110', 'commodityName': 'Rice'},
    {'commodityCode': '0612000', 'commodityName': 'Sugar'}
]

headers = {
    'accept': 'application/json',
    'X-Api-Key': api_key
}

# Function
def fetch_commodity_data(commodity_code, start_year, end_year):
    all_data = []
    for item in commodity_code:
        code = item["commodityCode"]
        name = item["commodityName"]
        for year in range(start_year, end_year + 1):
            url = f"{base_url}/{code}/world/year/{year}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            rows = response.json()
            for row in rows:
                row["commodityCode"] = code
                row["commodityName"] = name
                all_data.append(row)
            time.sleep(0.3)
    return all_data

# Run & Display
data = fetch_commodity_data(commodity_code, start_year, end_year)
df = pd.DataFrame(data)

attribute_id = 28  # Production only
df = df[df['attributeId'].isin([attribute_id])]
df['attributeId'] = df['attributeId'].replace(28, 'Production')
# Replace unitId values
df['unitId'] = df['unitId'].replace({
    8: '1000 Metric Ton',
    5: '1000 Head'
})
df = df.drop(columns=['calendarYear'])
df = df.rename(columns={'month': 'report_month'})
df['countryCode'] = 'World'
print(df.head())

save_path = os.path.join(data_dir, "agriculture", "crop_production.csv")
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print("Data saved to crop_production.csv")
