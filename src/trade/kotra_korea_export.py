import requests
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os

# Constants
BASE_URL = "https://www.kotra.or.kr/bigdata/visualization/korea/search"
EXPORT_PARAMS = {
    "impIsoWd2NatCd": "ALL",
    "isContinent": "N",
    "hscd": "ALL",
    "period": "M",
    "korExpImp": "exp"
}
IMPORT_PARAMS = EXPORT_PARAMS.copy()
IMPORT_PARAMS["korExpImp"] = "imp"

# Find latest available month
def fetch_data(baseYr, baseMn, params):
    params["baseYr"] = str(baseYr)
    params["baseMn"] = str(baseMn)
    try:
        r = requests.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and any(isinstance(v, list) and v for v in data.values()):
            return data
        return None
    except Exception:
        return None

def get_latest_valid_data():
    current = datetime.today().replace(day=1)
    for _ in range(12):  # look back up to 12 months
        baseYr = current.year
        baseMn = current.month
        test_params = EXPORT_PARAMS.copy()
        data = fetch_data(baseYr, baseMn, test_params)
        if data:
            return baseYr, baseMn
        current -= relativedelta(months=1)
        time.sleep(0.5)  # be polite to the server
    raise Exception("❌ No valid data found for the past 12 months.")

# Save JSON
def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Save CSV
def save_selected_lists_to_csv(data, export_map, output_dir):
    saved = []
    for key, filename in export_map.items():
        if key in data and isinstance(data[key], list) and data[key]:
            df = pd.DataFrame(data[key])
            if df.shape[1] > 1:
                cols_to_check = df.columns[1:]
                df = df.drop(columns=[col for col in cols_to_check if df[col].isna().all() or df[col].eq("").all()])
            save_path = os.path.join(output_dir, filename)
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            saved.append(save_path)
    return saved

# Main run
if __name__ == "__main__":
    year, month = get_latest_valid_data()
    print(f"📦 Fetching latest available data: {year}-{month:02d}")

    EXPORT_PARAMS.update({"baseYr": year, "baseMn": month})
    IMPORT_PARAMS.update({"baseYr": year, "baseMn": month})

    export_data = fetch_data(year, month, EXPORT_PARAMS)
    import_data = fetch_data(year, month, IMPORT_PARAMS)

    save_json(export_data, "kotra_korea_export.json")
    save_json(import_data, "kotra_korea_import.json")

    print("✅ Saved both export and import JSON files.")

    # Output directory
    output_dir = "C:/Users/va26/Desktop/global event/data/trade"
    os.makedirs(output_dir, exist_ok=True)

    # CSV mappings
    export_map = {
        "itemIncrsTrendList": "korea_export_increase_items.csv",
        "countryVaritnTrendList": "korea_export_country_variation.csv",
    }

    import_map = {
        "itemIncrsTrendList": "korea_import_increase_items.csv",
        "countryVaritnTrendList": "korea_import_country_variation.csv",
    }

    export_files = save_selected_lists_to_csv(export_data, export_map, output_dir)
    import_files = save_selected_lists_to_csv(import_data, import_map, output_dir)

    print("✅ Exported CSV files:")
    for f in export_files + import_files:
        print(f" - {f}")
