from bs4 import BeautifulSoup
import pandas as pd
from collections import OrderedDict
import re
import os
from dotenv import load_dotenv

load_dotenv()
data_dir = os.getenv("DATA_DIR")

# Continent mapping
CONTINENT_MAPPING = {
    'Asia': ['필리핀', '말레이시아', '인도네시아', '호주', '뉴질랜드', '파푸아뉴기니', '카자흐스탄'],
    'Africa': ['알제리', '콩고', '나이지리아', '적도기니', '모잠비크'],
    'America': ['캐나다', '미국', '멕시코', '브라질', '에콰도르'],
    'MiddleEast': ['이라크', '쿠웨이트', '카타르', '아랍에미레이트', '사우디아라비아', '오만', '중립지대'],
    'Europe': ['노르웨이', '영국']
}

# Load disguised .xls (actually HTML)
with open(os.path.join(data_dir, "energy", "petronet_oil_imports_monthly.xls"), "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
all_tables = soup.find_all('table')
wide_data = OrderedDict()
current_year = None

# Parse each data table
for table in all_tables:
    if table.get('border') != '1':
        continue

    rows = table.find_all('tr')
    if len(rows) < 3:
        continue

    country_cells = rows[0].find_all('td')[2:]
    countries = [td.get_text(strip=True) for td in country_cells]

    for row in rows[2:]:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        raw_cell = cells[0].get_text(strip=True).replace('\xa0', '')

        if '년' in raw_cell:
            match = re.match(r'(\d+)년\s*(\d+)월', raw_cell)
            if match:
                current_year = f"20{match.group(1)}"
                current_month = match.group(2).zfill(2)
            else:
                continue
        elif '월' in raw_cell and current_year:
            match = re.match(r'(\d+)월', raw_cell)
            if match:
                current_month = match.group(1).zfill(2)
            else:
                continue
        else:
            continue

        try:
            month_name = pd.to_datetime(f"{current_year}-{current_month}-01").strftime('%b %Y')
        except:
            continue

        values = [cell.get_text(strip=True).replace(',', '') for cell in cells[1:]]
        if month_name not in wide_data:
            wide_data[month_name] = {}

        for i, country in enumerate(countries):
            idx = i * 3
            if idx + 2 >= len(values):
                continue

            vol = float(values[idx]) if values[idx] != '-' else 0
            val = float(values[idx + 1]) if values[idx + 1] != '-' else 0
            price = float(values[idx + 2]) if values[idx + 2] != '-' else 0

            if country:
                wide_data[month_name][f"{country} (Vol)"] = vol
                wide_data[month_name][f"{country} (Value)"] = val
                wide_data[month_name][f"{country} (Price)"] = price

# Convert to DataFrame
df_wide = pd.DataFrame.from_dict(wide_data, orient='index')
df_wide.index.name = 'Month'
df_wide.reset_index(inplace=True)

# Add Total row
float_cols = df_wide.select_dtypes(include=['float64'])
sum_cols = [col for col in float_cols.columns if 'Price' not in col]
mean_cols = [col for col in float_cols.columns if 'Price' in col]

total_data = {}
for col in sum_cols:
    total_data[col] = df_wide[col].sum()
for col in mean_cols:
    total_data[col] = df_wide[col].mean()
total_data['Month'] = 'Total'

df_wide = pd.concat([df_wide, pd.DataFrame([total_data])], ignore_index=True)

# ---- Optimized continent aggregation ----
continent_df_parts = []

for continent, countries in CONTINENT_MAPPING.items():
    value_cols = [f"{country} (Value)" for country in countries if f"{country} (Value)" in df_wide.columns]
    vol_cols = [f"{country} (Vol)" for country in countries if f"{country} (Vol)" in df_wide.columns]
    price_cols = [f"{country} (Price)" for country in countries if f"{country} (Price)" in df_wide.columns]

    value_sum = df_wide[value_cols].sum(axis=1)
    vol_sum = df_wide[vol_cols].sum(axis=1)
    price_avg = df_wide[price_cols].mean(axis=1)

    if '합 계 (Value)' in df_wide.columns:
        total_values = df_wide['합 계 (Value)']
    else:
        total_values = df_wide[[col for col in df_wide.columns
                                if '(Value)' in col and not any(c in col for c in CONTINENT_MAPPING.keys())]].sum(axis=1)

    pct = (value_sum / total_values) * 100
    pct_formatted = pct.round(2).astype(str) + '%'

    continent_df = pd.DataFrame({
        f"{continent} (Value)": value_sum,
        f"{continent} (Vol)": vol_sum,
        f"{continent} (Price)": price_avg,
        f"{continent} (%)": pct_formatted
    })

    continent_df_parts.append(continent_df)

# Combine all continent data and reorder
continent_all = pd.concat(continent_df_parts, axis=1)

# Reorder columns: Month → Continent → Country-level
df_wide = pd.concat([
    df_wide[['Month']].reset_index(drop=True),
    continent_all.reset_index(drop=True),
    df_wide.drop(columns=['Month']).reset_index(drop=True)
], axis=1)

filename = "oil_imports_with_continents.csv"
save_path = os.path.join(data_dir, "energy", filename)
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save final result
df_wide.to_csv(save_path, index=False, encoding="utf-8-sig")
print(f"Saved to: {save_path}")