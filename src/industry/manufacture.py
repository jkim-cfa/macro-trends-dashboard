import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- Parameters ---
api_key = os.getenv('ECOS_API_KEY')
base_url = 'https://ecos.bok.or.kr/api/StatisticSearch'
start_date = '202001'
end_date = datetime.now().strftime('%Y%m')
stat_codes = ['901Y026', '901Y066']  # 제조업재고율, 설비투자지수
cycle = 'M'

# --- Function ---
def fetch_data(stat_codes):
    all_data = []
    for code in stat_codes:
        url = f"{base_url}/{api_key}/json/kr/1/10000/{code}/{cycle}/{start_date}/{end_date}/"
        response = requests.get(url)

        data = response.json()
        rows = data.get('StatisticSearch', {}).get('row', [])
        for row in rows:
            row['STAT_CODE'] = code
            all_data.append(row)
        time.sleep(0.3)
    return all_data

# --- Run ---
data = fetch_data(stat_codes)
df = pd.DataFrame(data)
print(df.head())

# Drop unnecessary columns
cols_to_drop = ['ITEM_CODE2', 'ITEM_NAME2', 'ITEM_CODE3', 'ITEM_NAME3',
                'ITEM_CODE4', 'ITEM_NAME4', 'WGT']

df = df[df['ITEM_NAME1'] != '원지수']

df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

# Save to CSV
save_path = "C:/Users/va26/Desktop/global event/data/industry/manufacture_inventory.csv"
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print("Data saved to manufacture_inventory.csv")

