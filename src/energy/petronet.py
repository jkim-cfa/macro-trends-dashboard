import os
import requests
import pandas as pd

# Settings
download_dir = os.path.dirname(os.path.abspath(__file__))
filename = "petronet_oil_imports_monthly.xls"
filepath = os.path.join(download_dir, filename)

# Time range
start_year = 2024
start_month = 1
end_year = 2025
end_month = 5

# Download Excel
url = (
    "https://www.petronet.co.kr/v4/excel/KDXQ0400_x.jsp"
    "?term=m"
    f"&by={start_year}&bq=1&bm={start_month:02d}"
    f"&ay={end_year}&aq=2&am={end_month:02d}"
    "&PriceCD=3"
    "&CntyCDSList=5,4,3,2,1"
    "&ProdNMList=ALL"
)

response = requests.get(url)
response.raise_for_status()  # raise error if failed

with open(filepath, "wb") as f:
    f.write(response.content)

print(f"✅ Excel downloaded: {filepath}")
