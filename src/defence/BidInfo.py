import requests
import pandas as pd
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BID_API_KEY')
list_url = 'http://openapi.d2b.go.kr/openapi/service/PrcurePlanInfoService/getDmstcPrcurePlanList'

params = {
    'serviceKey': api_key,
    'orderPrearngeMtBegin': '20100101',
    'numOfRows': '10000',
}

response = requests.get(list_url, params=params)
response.encoding = 'utf-8'
root = ET.fromstring(response.content)

items = root.findall('.//item')
data = []
for item in items:
    row = {}
    for child in item:
        row[child.tag] = child.text
    data.append(row)

df = pd.DataFrame(data)

# Drop unnecessary columns if desired
columns_to_drop = ['beffatStndrdOthbcAt', 'bidMth', 'cntrctMth', 'dcsNo', 'orntCode', 'progrsSttusCode', 'spcifyPrcureAt']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

print(df.head())

save_path = "C:/Users/va26/Desktop/global event/data/defence/bid_info.csv"  # Use your desired full path
df.to_csv(save_path, index=False, encoding="utf-8-sig")
