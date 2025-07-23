import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR", "data")

api_key = os.getenv('ECOS_API_KEY')
base_url = 'https://ecos.bok.or.kr/api/StatisticSearch'
stat_codes = ['403Y001', '403Y003']  # Export & Import Price Index
freq = 'M'
start_period = '202201'
end_period = datetime.today().strftime('%Y%m')

all_rows = []

for stat_code in stat_codes:
    url = f"{base_url}/{api_key}/json/kr/1/10000/{stat_code}/{freq}/{start_period}/{end_period}"
    response = requests.get(url)
    data = response.json()
    rows = data.get('StatisticSearch', {}).get('row', [])
    for row in rows:
        row['STAT_CODE'] = stat_code
    all_rows.extend(rows)

# Convert to DataFrame
df = pd.DataFrame(all_rows)
df['datetime'] = pd.to_datetime(df['TIME'].str[:4] + '-' + df['TIME'].str[4:], errors='coerce')
df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'], errors='coerce')
df.drop_duplicates(inplace=True)

# Remove hierarchical duplicates
df = (
    df
    .sort_values('ITEM_CODE1', key=lambda x: x.str.len(), ascending=False)
    .drop_duplicates(subset=['STAT_CODE', 'TIME', 'ITEM_NAME1'], keep='first')
)

# Determine top 5 items in each group
top_export_items = (
    df[df['STAT_CODE'] == '403Y001']
    .groupby('ITEM_NAME1')['DATA_VALUE'].sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top_import_items = (
    df[df['STAT_CODE'] == '403Y003']
    .groupby('ITEM_NAME1')['DATA_VALUE'].sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top_items = set(top_export_items).union(set(top_import_items))

# Filter, compute YoY
df_filtered = df[df['ITEM_NAME1'].isin(top_items)].copy()
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

# Final cleanup
cols_to_drop = ['ITEM_CODE2', 'ITEM_NAME2', 'ITEM_CODE3', 'ITEM_NAME3', 'ITEM_CODE4', 'ITEM_NAME4', 'WGT']
df_filtered.drop(columns=cols_to_drop, inplace=True, errors='ignore')

# Rename STAT_CODE to readable Korean names
stat_code_map = {
    '403Y001': '수출금액지수',
    '403Y003': '수입금액지수'
}
df_filtered['STAT_CODE'] = df_filtered['STAT_CODE'].map(stat_code_map)

# Save to CSV
output_dir = os.path.join(data_dir, "trade")
os.makedirs(os.path.dirname(output_dir), exist_ok=True)
save_path = os.path.join(output_dir, "korea_trade_items_yoy.csv")

df_filtered.to_csv(save_path, index=False, encoding='utf-8-sig')
print(f"✅ Saved to {save_path}")