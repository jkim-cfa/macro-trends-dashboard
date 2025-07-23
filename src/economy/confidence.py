import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR", "data")
# Parameters
api_key = os.getenv('ECOS_API_KEY')
base_url = 'https://ecos.bok.or.kr/api/StatisticSearch'
start_date = '201001'
end_date = datetime.now().strftime('%Y%m')
stat_codes = ['513Y001', '521Y001']  # 경제심리지수, 뉴스심리지수
cycle = 'M'

# Function
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

# Run
data = fetch_data(stat_codes)
df = pd.DataFrame(data)

# Rename codes to labels
df['STAT_CODE'] = df['STAT_CODE'].replace({
    '513Y001': '경제심리지수',
    '521Y001': '뉴스심리지수'
})

# Drop unnecessary columns
cols_to_drop = ['ITEM_CODE2', 'ITEM_NAME2', 'ITEM_CODE3', 'ITEM_NAME3',
                'ITEM_CODE4', 'ITEM_NAME4', 'UNIT_NAME', 'WGT']
df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
print(df.head)

# Save to CSV
save_path = os.path.join(data_dir, "economy", "economy_confidence.csv")
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print("Data saved to economy_confidence.csv")
