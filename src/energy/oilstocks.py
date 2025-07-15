import requests
import pandas as pd

year = "2025"  # Change this as needed
all_data = []

for month in range(1, 13):
    month_str = f"{month:02d}"
    url = f"https://api.iea.org/netimports/monthly?year={year}&month={month_str}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.iea.org/data-and-statistics/data-tools/oil-stocks-of-iea-countries",
        "Origin": "https://www.iea.org"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data:
            print(f"No data for {year}-{month_str}")
            continue
        for row in data:
            row["Year"] = year
            row["Month"] = month_str
            all_data.append(row)
    else:
        print(f"Failed to fetch {year}-{month_str}: Status {response.status_code}")

# Convert to DataFrame
df = pd.DataFrame(all_data)


# Reorder columns
desired_order = ['Year', 'Month', 'countryName', 'total', 'industry', 'publicData', 'abroadIndustry', 'abroadPublic']
df = df[desired_order]

df["Month"] = pd.to_datetime(df["Year"] + "-" + df["Month"] + "-01").dt.strftime("%B")

# Save or show
save_path = "C:/Users/va26/Desktop/global event/data/energy/iea_oil_stocks.csv"
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print("Data saved to iea_oil_stocks.csv")