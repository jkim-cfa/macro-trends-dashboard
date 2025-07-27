import os
import warnings
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR")
eda_path = os.path.join(EDA_DIR, "outputs", "global_trade")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Top 5 Year-over-Year (YoY) Decreased Export Items
def load_top5_decreased_export_items_data(engine):
    query = """
    SELECT * 
    FROM trade_global_export_decrease_items_top5_processed
    ORDER BY full_label, indicator, value
    """
    return pd.read_sql(query, engine)

# Top 5 Year-over-Year (YoY) Increased ExportItems
def load_top5_increased_export_items_data(engine):
    query = """
    SELECT * 
    FROM trade_global_export_increase_items_top5_processed
    ORDER BY full_label, indicator, value
    """
    return pd.read_sql(query, engine)

# Top 5 Year-over-Year Trade Increased Countries
def load_top5_increased_export_countries_data(engine):
    query = """
    SELECT * 
    FROM trade_global_trade_variation_top5_processed
    ORDER BY country,indicator, value
    """
    return pd.read_sql(query, engine)

# Top 5 Trading Partners
def load_top5_trading_partners_data(engine):
    query = """
    SELECT * 
    FROM trade_global_trade_processed
    ORDER BY rank, country, indicator, value
    """
    return pd.read_sql(query, engine)

# Shipping Index
def load_shipping_index_data(engine):
    query = """
    SELECT date, indicator, value, unit 
    FROM trade_shipping_indices_processed
    WHERE value IS NOT NULL
    ORDER BY date, indicator 
    """
    return pd.read_sql(query, engine)

# English translation dictionary
eng_commodity_name = {
    '천연가스': "Natural Gas",
    '유연탄' : 'Bituminous Coal',
    '석유와 역청유(瀝靑油)(원유로 한정한다)': 'Crude Oil',
    '경질유(輕質油)와 조제품': 'Light Oil and Preparations',
    '전기에너지': 'Electrical Energy',
    '그 밖의 석탄': 'Other Coal',
    '메모리': 'Memory Modules (Electronic Components)',
    '응결시키지 않은 것': 'Unagglomerated Iron Ores and Concentrates',
    '기억장치': 'Data Storage Devices',
    '휴대용 자동자료처리기계': 'Portable Data Processing Machines (<10kg)',
    '음극과 음극의 형재': 'Refined Copper Cathodes and Sections',
    '처리장치(소호 제8471.41호나 제8471.49호 외의 것으로서 기억장치ㆍ입력장치ㆍ출력장치 중 한 가지나 두 가지 장치를 동일 하우징 속에 내장한 것인지에 상관없다)': 'Processing Units (non-8471.41/49)',
    '면역물품(일정한 투여량으로 한 것, 소매용 모양이나 포장을 한 것에 한정한다)': 'Immunological Products (Dosage/Retail)',
    '그 밖의 차량(불꽃점화식 피스톤 내연기관과 추진용 모터로서의 전동기를 둘 다 갖춘 것으로서, 외부 전원에 플러그를 꽂아 충전할 수 있는 방식의 것은 제외한다)': 'Other Hybrid Vehicles (non-Plug-in)',
    '면역혈청과 그 밖의 혈액 분획물': 'Immunological Serum & Blood Fractions',
    '제8471호에 해당하는 기계의 부분품과 부속품': 'Parts for HS8471 Machines',
    '그 밖의 차량(추진용 전동기만을 갖춘 것)': 'Electric Vehicles (Motor Only)',
    '광전지(모듈에 조립되었거나 패널로 구성된 것으로 한정한다)': 'Photovoltaic Cells (Modules/Panels)',
    '리튬이온 축전지': 'Lithium-Ion Batteries',
    '터보제트나 터보프로펠러의 것': 'Parts for Turbojets/Turboprops',
    '비행기ㆍ헬리콥터ㆍ무인기의 그 밖의 부분품': 'Aircraft & UAV Parts'
}

# Top 5 Year-over-Year (YoY) Decreased Export Items
def process_top5_export_decrease_items(df):

    # Map English names with fallback
    df['eng_commodity_name'] = df['commodity_name'].map(eng_commodity_name).fillna(df['commodity_name'])

    # Extract HS code
    df['hs_code'] = df['full_label'].str[:6]

    # Combine for full label
    df['commodity_full_name'] = df['eng_commodity_name'] + df['hs_code']

    # Pivot to combine amount and YoY into one row
    export_decreased_items_pivoted = df.pivot_table(
        index=["date", "country", "commodity_full_name", "change_type"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()

    # Rename columns
    export_decreased_items_pivoted = export_decreased_items_pivoted.rename(columns={
        "export_amount": "export_value_thousand_usd",
        "export_yoy": "yoy_change_percent"
    })

    return export_decreased_items_pivoted

# Top 5 Year-over-Year (YoY) Increased Export Items
def process_top5_export_increase_items(df):

    # Map English names with fallback
    df['eng_commodity_name'] = df['commodity_name'].map(eng_commodity_name).fillna(df['commodity_name'])

    # Extract HS code
    df['hs_code'] = df['full_label'].str[:6]

    # Combine for full label
    df['commodity_full_name'] = df['eng_commodity_name'] + df['hs_code']

    # Pivot to combine amount and YoY into one row
    export_increased_items_pivoted = df.pivot_table(
        index=["date", "country", "commodity_full_name", "change_type"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()

    # Rename columns
    export_increased_items_pivoted = export_increased_items_pivoted.rename(columns={
        "export_amount": "export_value_thousand_usd",
        "export_yoy": "yoy_change_percent"
    })

    return export_increased_items_pivoted

# Top 5 Year-over-Year Trade Increasesd Countries
def process_top5_export_increase_countries(df):

    export_increased_countries_pivoted  = df.pivot_table(
        index=["date", "country", "partner"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()

    export_increased_countries_pivoted = export_increased_countries_pivoted.rename(columns={
        "export_amount": "export_value_thousand_usd",
        "export_yoy": "yoy_change_percent",
        "export_share": "export_share_percent",
        "import_share": "import_share_percent"
    })

    return export_increased_countries_pivoted

# Top 5 Trading Partners
def process_top5_trade_partners(df):
    top5_trade_partners_pivoted = df.pivot_table(
        index=["date", "country", "partner", "rank"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()

    top5_trade_partners_pivoted = top5_trade_partners_pivoted.rename(columns={
        "export_amount": "export_value_thousand_usd",
        "export_yoy": "yoy_change_percent",
        "export_share": "export_share_percent",
        "import_share": "import_share_percent"
    })

    return top5_trade_partners_pivoted

# Shipping Index
def process_shipping_index(df):
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Drop rows with missing values
    df = df.dropna(subset=["value", "indicator"])

    # Pivot
    shipping_index_pivoted = df.pivot_table(
        index="date",
        columns="indicator",
        values="value",
        aggfunc="mean"
    ).sort_index()

    return shipping_index_pivoted

# Correlation Analysis
def correlation_analysis(shipping_index_pivoted):
    combined_filled = shipping_index_pivoted.fillna(method='ffill').fillna(method='bfill')
    correlation_matrix = combined_filled.corr()

    return correlation_matrix

# Volitility Analysis
def three_month_volatility_analysis(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Fill missing values
    df_filled = df.fillna(method='ffill').fillna(method='bfill')

    # Set 'date' as the index and sort it
    df_filled = df_filled.set_index('date').sort_index()

    # Resample the data to a monthly frequency and calculate the mean for each month
    monthly_mean = df_filled.resample('M')['value'].mean().to_frame()

    # Apply a rolling 3-month standard deviation (volatility) calculation
    rolling_3m_volatility = monthly_mean.rolling(window=3).std()

    return rolling_3m_volatility

# Save
def save_trade_eda_outputs(
    df_decrease_items,
    df_increase_items,
    df_increase_countries,
    df_top5_partners,
    df_shipping_index,
    output_dir
):
    os.makedirs(output_dir, exist_ok=True)

    # Export Decrease Items
    processed_decrease = process_top5_export_decrease_items(df_decrease_items)
    processed_decrease.to_csv(os.path.join(output_dir, "export_decrease_items_top5.csv"), index=False)

    # Export Increase Items
    processed_increase = process_top5_export_increase_items(df_increase_items)
    processed_increase.to_csv(os.path.join(output_dir, "export_increase_items_top5.csv"), index=False)

    # Export Increase Countries
    processed_increase_countries = process_top5_export_increase_countries(df_increase_countries)
    processed_increase_countries.to_csv(os.path.join(output_dir, "export_increase_countries_top5.csv"), index=False)

    # Top 5 Trade Partners
    processed_partners = process_top5_trade_partners(df_top5_partners)
    processed_partners.to_csv(os.path.join(output_dir, "trade_partners_top5.csv"), index=False)

    # Shipping Index: Pivoted
    shipping_index_pivoted = process_shipping_index(df_shipping_index)
    shipping_index_pivoted.to_csv(os.path.join(output_dir, "shipping_index_pivoted.csv"))

    # Correlation Matrix
    corr_matrix = correlation_analysis(shipping_index_pivoted)
    corr_matrix.to_csv(os.path.join(output_dir, "shipping_index_correlation.csv"))

    # Rolling 3-Month Volatility
    rolling_volatility = three_month_volatility_analysis(df_shipping_index)
    rolling_volatility.to_csv(os.path.join(output_dir, "shipping_index_3m_volatility.csv"))

    print(f"✅ Trade EDA outputs saved to: {output_dir}")

    # Key insights for AI analysis
    key_insights = {
        "summary_statistics": {
            "Top 5 YoY Decrease Items": processed_decrease[["commodity_full_name", "export_value_thousand_usd", "yoy_change_percent"]]
                .sort_values("yoy_change_percent")
                .head(5)
                .to_dict(orient="records"),

            "Top 5 YoY Increase Items": processed_increase[["commodity_full_name", "export_value_thousand_usd", "yoy_change_percent"]]
                .sort_values("yoy_change_percent", ascending=False)
                .head(5)
                .to_dict(orient="records"),

            "Top 5 Export Increase Countries": processed_increase_countries[["country", "partner", "export_value_thousand_usd", "yoy_change_percent"]]
                .sort_values("yoy_change_percent", ascending=False)
                .head(5)
                .to_dict(orient="records"),

            "Top Trade Partners by Export Value": processed_partners[["country", "partner", "export_value_thousand_usd"]]
                .sort_values("export_value_thousand_usd", ascending=False)
                .head(5)
                .to_dict(orient="records")
        },

        "shipping_index": {
            "correlation_matrix": corr_matrix.round(2).to_dict(),
            "volatility_3m_std": rolling_volatility.round(2).dropna(how='all').tail(1).to_dict(orient="records")[0]
        }
    }

    # Save JSON
    with open(os.path.join(output_dir, "key_insights.json"), "w", encoding='utf-8') as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False)

    return key_insights

# Gemini Insight
def generate_insights(key_insights, output_dir):
    try:
        summary_stats = key_insights.get("summary_statistics", {})
        shipping_metrics = key_insights.get("shipping_index", {})

        prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects. Extract non-obvious implications from the data below.

**Data Inputs**:
1. Summary Statistics:
{json.dumps(summary_stats, indent=2)}

2. Key Metrics:
{json.dumps(shipping_metrics, indent=2)}

### **Required Output Format**  
```markdown
## Global Trade Second-Order Analysis

### Core Trend  
• Global Trade: [TREND SUMMARY IN 5-10 WORDS]  
• **Direct Impact**: [IMMEDIATE OUTCOME IN 1 SENTENCE]  

### Hidden Effects  
1. **[EFFECT 1 NAME]**  
   - *Catalyst*: [PRIMARY DRIVER]  
   - *Transmission*: [HOW IT SPREADS THROUGH SYSTEM]  
   - *Evidence*: [DATA POINT OR HISTORICAL PRECEDENT]  

2. **[EFFECT 2 NAME]**  
   - *Catalyst*: [PRIMARY DRIVER]  
   - *Transmission*: [HOW IT SPREADS THROUGH SYSTEM]  
   - *Evidence*: [DATA POINT OR HISTORICAL PRECEDENT]  

### Cross-Domain Impacts  
→ **[SECTOR A]**: [IMPACT DESCRIPTION] (Delay: [X MONTHS/YEARS])  
→ **[SECTOR B]**: [IMPACT DESCRIPTION] (Delay: [X MONTHS/YEARS])  

### System Dynamics  
⚠️ *Threshold Effect*: "[QUANTITATIVE TRIGGER IF KNOWN]"  
♻️ *Feedback Mechanism*: "[SELF-REINFORCING OR DAMPENING CYCLE]"  

### Actionable Intelligence  
🛠 **Policy Lever**: [CONCRETE INTERVENTION]  
📊 **Leading Indicator**: [METRIC] (Update: [FREQUENCY])  
"""
        response = MODEL.generate_content(prompt)
        gemini_insight = response.text.strip()

        with open(f"{output_dir}/gemini_insight.txt", "w", encoding="utf-8") as f:
            f.write(gemini_insight)

        print("✅ Gemini insights generated and saved.")

    except Exception as e:
        print(f"❌ Gemini insight generation failed: {e}")

# Main
def main():
    # Load data from database
    df_decrease_items = load_top5_decreased_export_items_data(engine)
    df_increase_items = load_top5_increased_export_items_data(engine)
    df_increase_countries = load_top5_increased_export_countries_data(engine)
    df_top5_partners = load_top5_trading_partners_data(engine)
    df_shipping_index = load_shipping_index_data(engine)

    # Save all processed outputs and generate key insights
    key_insights = save_trade_eda_outputs(
        df_decrease_items,
        df_increase_items,
        df_increase_countries,
        df_top5_partners,
        df_shipping_index,
        eda_path
    )

    # Basic console overview
    df_decrease_items['date'] = pd.to_datetime(df_decrease_items['date'], errors='coerce')

    print("\n=== Data Overview ===")
    print(f"Time Range: {df_decrease_items['date'].min().year} to {df_decrease_items['date'].max().year}")
    print(f"Commodities: {df_decrease_items['commodity_name'].nunique()}")
    print(f"Indicators: {df_decrease_items['indicator'].nunique()}")


    print("\n=== Summary Stats ===")
    print(df_decrease_items.groupby('commodity_name')['value'].describe().round(2))

    # Generate Gemini insight text based on key stats
    generate_insights(key_insights, eda_path)

    print(f"\n✅ All data saved to: {eda_path}")
    print("Files created:")
    print("- export_decrease_items_top5.csv")
    print("- export_increase_items_top5.csv")
    print("- export_increase_countries_top5.csv")
    print("- trade_partners_top5.csv")
    print("- shipping_index_pivoted.csv")
    print("- shipping_index_correlation.csv")
    print("- shipping_index_3m_volatility.csv")
    print("- gemini_insight.txt")

if __name__ == "__main__":
    main()
