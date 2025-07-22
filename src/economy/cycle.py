import requests
import pandas as pd
from datetime import datetime
import yfinance as yf
import os
from dotenv import load_dotenv

load_dotenv()
# Parameters
api_key = os.getenv('ECOS_API_KEY')
base_url = 'https://ecos.bok.or.kr/api/StatisticSearch'
stat_code = '901Y067'
freq = 'M'
start_period = '200001'
end_period = datetime.today().strftime('%Y%m')

# Fetch ECOS data
url = f"{base_url}/{api_key}/json/kr/1/10000/{stat_code}/{freq}/{start_period}/{end_period}"
response = requests.get(url)
data = response.json()
rows = data.get('StatisticSearch', {}).get('row', [])
df = pd.DataFrame(rows)

# Preprocess ECOS data
df['datetime'] = pd.to_datetime(df['TIME'], format='%Y%m')
df['DATA_VALUE'] = pd.to_numeric(df['DATA_VALUE'], errors='coerce')
df = df[df['ITEM_NAME1'].isin(['동행지수순환변동치', '선행지수순환변동치'])]

# Pivot and calculate difference
pivot_df = df.pivot(index='datetime', columns='ITEM_NAME1', values='DATA_VALUE')
pivot_df['선행-동행'] = pivot_df['선행지수순환변동치'] - pivot_df['동행지수순환변동치']

# Download KOSPI monthly close
yf_start = pd.to_datetime(start_period + '01').strftime('%Y-%m-%d')
yf_end = pd.to_datetime(end_period + '01').strftime('%Y-%m-%d')
kospi = yf.download('^KS11', start=yf_start, end=yf_end, auto_adjust=True, progress=False)

# Resample and prepare for merge
kospi_monthly = kospi['Close'].resample('MS').last()
kospi_monthly.index.name = 'datetime'
kospi_monthly = kospi_monthly.reset_index()

# Merge with ECOS data
pivot_df = pivot_df.reset_index()
pivot_df = pivot_df.merge(kospi_monthly, on='datetime', how='left')

# After the merge line
pivot_df = pivot_df.rename(columns={'^KS11': 'KOSPI'})

# Save
save_path = "C:/Users/va26/Desktop/global event/data/economy/leading_vs_coincident_kospi.csv"
pivot_df.to_csv(save_path, index=False, encoding='utf-8-sig')
print(pivot_df.head())
