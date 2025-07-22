import requests
import json
import pandas as pd
import os

# Fetch data
url = "https://www.kotra.or.kr/bigdata/visualization/global/search"
params = {
    "baseYr": "2024", # Change this as needed
    "expIsoWd2NatCd": "ALL",
    "impIsoWd2NatCd": "ALL",
    "hscd": "ALL"
}

r = requests.get(url, params=params)
data = r.json()

# Save raw JSON
with open("kotra_global_trade.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Saved KOTRA data to kotra_global_data.json")

# CSV output directory
output_dir = "C:/Users/va26/Desktop/global event/data/trade"
os.makedirs(output_dir, exist_ok=True)

# Extract main content
kotra_data = data  # JSON is already flat at top level

# Export CSVs
export_map = {
    "mapList": "global_trade.csv",
    "itemDecrsTop5List": "global_export_decrease_items_top5.csv",
    "countryVaritnTop5List": "global_trade_variation_top5.csv",
    "itemIncrsTop5List": "global_export_increase_items_top5.csv",
}

exported_files = []
for key, filename in export_map.items():
    if key in kotra_data and isinstance(kotra_data[key], list) and kotra_data[key]:
        df = pd.DataFrame(kotra_data[key])

        # Drop fully empty columns from second to last
        if df.shape[1] > 1:
            cols_to_check = df.columns[1:]
            df = df.drop(columns=[col for col in cols_to_check if df[col].isna().all() or df[col].eq("").all()])

        save_path = os.path.join(output_dir, filename)
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        exported_files.append(save_path)

print("✅ Exported CSV files:")
for f in exported_files:
    print(f" - {f}")
