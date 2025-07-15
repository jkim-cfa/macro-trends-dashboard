import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ECOS_API_KEY')
base_url = 'https://ecos.bok.or.kr/api/StatisticSearch'
stat_codes = ['901Y011', '901Y012']
freq = 'M'
start_period = '202001'
end_period = datetime.today().strftime('%Y%m')

all_rows = []

for stat_code in stat_codes:
    # 1. First call to get total count
    url = f"{base_url}/{api_key}/json/kr/1/100/{stat_code}/{freq}/{start_period}/{end_period}"
    response = requests.get(url)
    result = response.json()

    total_count = int(result['StatisticSearch']['list_total_count'])
    page_count = (total_count // 100) + 1

    # 2. Loop over pages
    for i in range(page_count):
        start = str(i * 100 + 1)
        end = str((i + 1) * 100)
        page_url = f"{base_url}/{api_key}/json/kr/{start}/{end}/{stat_code}/{freq}/{start_period}/{end_period}"
        page_response = requests.get(page_url)
        page_data = page_response.json()

        rows = page_data.get('StatisticSearch', {}).get('row', [])
        for row in rows:
            row['STAT_CODE'] = stat_code
        all_rows.extend(rows)

# 3. Convert to DataFrame
df = pd.DataFrame(all_rows)
df['datetime'] = pd.to_datetime(df['TIME'].str[:4] + '-' + df['TIME'].str[4:], errors='coerce')
df.drop_duplicates(inplace=True)

# Get top countries by cumulative export/import value
top_exporters = (
    df[df['STAT_CODE'] == '901Y011']
    .groupby('ITEM_NAME1')['DATA_VALUE'].sum()
    .sort_values(ascending=False)
    .head(10)
    .index
)

top_importers = (
    df[df['STAT_CODE'] == '901Y012']
    .groupby('ITEM_NAME1')['DATA_VALUE'].sum()
    .sort_values(ascending=False)
    .head(10)
    .index
)

top_countries = set(top_exporters).union(set(top_importers))

df_filtered = df[df['ITEM_NAME1'].isin(top_countries)].copy()

df_filtered['DATA_VALUE'] = pd.to_numeric(df_filtered['DATA_VALUE'], errors='coerce')

df_filtered.sort_values(['STAT_CODE', 'ITEM_NAME1', 'datetime'], inplace=True)
df_filtered['yoy'] = (
    df_filtered
    .groupby(['STAT_CODE', 'ITEM_NAME1'])['DATA_VALUE']
    .pct_change(periods=12)
    .mul(100)
    .round(2)
    .astype(str)
    .add('%')
)

# Drop unused columns in filtered version only
cols_to_drop = ['ITEM_CODE2', 'ITEM_NAME2', 'ITEM_CODE3', 'ITEM_NAME3', 'ITEM_CODE4', 'ITEM_NAME4', 'WGT']
df_filtered.drop(columns=cols_to_drop, inplace=True, errors='ignore')

# Save
output_dir = "C:/Users/va26/Desktop/global event/data/trade"
os.makedirs(output_dir, exist_ok=True)
save_path = os.path.join(output_dir, "korea_trade_yoy.csv")
df_filtered.to_csv(save_path, index=False, encoding='utf-8-sig')

