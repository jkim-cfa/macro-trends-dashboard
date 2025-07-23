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
start_date = '200001'
end_date = datetime.now().strftime('%Y%m')
stat_code_main = '731Y004'
stat_code_eur = '731Y005'
cycle = 'M'
measurement_code = '0000100'

# Currencies
currency_codes = {
    '0000001': 'USD',
    '0000002': 'JPY',
    '0000003': 'EUR',
    '0000053': 'CNY'
}
currency_codes2 = {
    '0000003': 'USD/EUR'
}

# Functions
def fetch_fx_data(stat_code, currencies):
    all_data = []
    for code, name in currencies.items():
        url = (
            f"{base_url}/{api_key}/json/kr/1/1000/"
            f"{stat_code}/{cycle}/{start_date}/{end_date}/"
            f"{code}/{measurement_code}"
        )
        response = requests.get(url)
        data = response.json()
        rows = data.get('StatisticSearch', {}).get('row', [])
        for row in rows:
            row['CURRENCY'] = name
            row['EXCHANGE_RATE'] = float(row['DATA_VALUE'])
            all_data.append(row)
    return all_data

# Run
data_main = fetch_fx_data(stat_code_main, currency_codes)
data_eur = fetch_fx_data(stat_code_eur, currency_codes2)
final_data = data_main + data_eur

# DataFrame
df = pd.DataFrame(final_data)
df['DATE'] = pd.to_datetime(df['TIME'], format='%Y%m', errors='coerce')
df = df.dropna(subset=['EXCHANGE_RATE', 'DATE'])
df = df[['DATE', 'CURRENCY', 'EXCHANGE_RATE', 'UNIT_NAME']].sort_values(['CURRENCY', 'DATE'])
df['UNIT_NAME'] = df['UNIT_NAME'].replace('통화당 달러', '달러')

# Print Preview
print(df.head(10))
for currency in df['CURRENCY'].unique():
    latest = df[df['CURRENCY'] == currency].iloc[-1]
    print(f"{currency}: {latest['EXCHANGE_RATE']:.2f} ({latest['DATE'].strftime('%Y-%m')})")

# Save
save_path = os.path.join(data_dir, "economy", "fx_rates.csv")
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print("Data saved to monthly_fx_rates.csv")
