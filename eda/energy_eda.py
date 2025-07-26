import os
import warnings
import pandas as pd
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv
import google.generativeai as genai
from pandas.tseries.offsets import DateOffset

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR")
eda_path = os.path.join(EDA_DIR, "outputs", "energy")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Load energy datasets
def load_oil_import_with_continents_data():
    query = """
    SELECT date, region, country, value, unit, sector, source
    FROM energy_oil_imports_with_continents_processed
    ORDER BY date, region, country, unit
    """
    df_oil_import_with_continents = pd.read_sql(query, engine)
    df_oil_import_with_continents['date'] = pd.to_datetime(df_oil_import_with_continents['date'])
    return df_oil_import_with_continents

def load_iea_oil_stocks_data():
    query = """
    SELECT date, country, value, unit, source
    FROM energy_iea_oil_stocks_processed
    ORDER BY date, country
    """
    df_iea_oil_stocks = pd.read_sql(query, engine)
    df_iea_oil_stocks['date'] = pd.to_datetime(df_iea_oil_stocks['date'])
    return df_iea_oil_stocks

def load_opec_summary_data():
    query = """
    SELECT topic, insight
    FROM energy_opec_insights
    """
    df_opec_summary = pd.read_sql(query, engine)
    return df_opec_summary

# Oil Stock Analysis
def stock_time_series_analysis(df_iea_oil_stocks):

    aggregates = ['Total IEA', 'Total IEA Asia Pacific', 'Total IEA net importers', 'Total IEA Europe']
    
    # 1. Country stock ranking (latest values)
    latest_date = df_iea_oil_stocks['date'].max()

    country_ranking = (
        df_iea_oil_stocks[
            (df_iea_oil_stocks['date'] == latest_date) &
            (~df_iea_oil_stocks['country'].isin(aggregates))  # Excluding aggregates
        ]
        .sort_values('value', ascending=False)
        .reset_index(drop=True)
    )
    
    # 3. Volatility by country (standard deviation)
    volatility_by_country = (
        df_iea_oil_stocks[~df_iea_oil_stocks['country'].isin(aggregates)]  # Excluding aggregates
        .groupby("country")["value"]
        .agg(['std', 'mean', 'count'])
        .reset_index()
        .rename(columns={'std': 'volatility', 'mean': 'avg_stock', 'count': 'data_points'})
        .sort_values(by="volatility", ascending=False)
    )
    
    # 4. Seasonality patterns
    df_copy = df_iea_oil_stocks[~df_iea_oil_stocks['country'].isin(aggregates)].copy()  # Excluding aggregates
    df_copy['month'] = df_copy['date'].dt.month
    seasonality_by_country = (
        df_copy.groupby(['month', 'country'])['value']
        .mean()
        .reset_index()
    )
    
    # 5. Top stockpilers stats
    stockpile_stats = (
        df_iea_oil_stocks[~df_iea_oil_stocks['country'].isin(aggregates)]  # Excluding aggregates
        .groupby("country")
        .agg(
            avg_stock=("value", "mean"),
            latest_stock=("value", "last"),
            min_stock=("value", "min"),
            max_stock=("value", "max")
        )
        .sort_values(by="latest_stock", ascending=False)
        .reset_index()
    )
    
    return {
        'country_ranking': country_ranking,
        'volatility_analysis': volatility_by_country,
        'seasonality_patterns': seasonality_by_country,
        'stockpile_statistics': stockpile_stats
    }

# Oil Import Analysis
def oil_import_analysis(df_oil_import_with_continents):

    # Map units to readable metric names
    metric_unit_map = {
        'thousand USD': 'Value',
        'thousand bbl': 'Volume',
        'percentage': 'Share',
        'USD/bbl': 'Price'
    }
    
    df_oil_import_with_continents['metric_type'] = df_oil_import_with_continents['unit'].map(metric_unit_map)
    
    # 1. Regional share analysis (percentage data)
    continent_share = df_oil_import_with_continents[
        df_oil_import_with_continents['unit'] == 'percentage'
    ].copy()
    
    continent_share_summary = (
        continent_share
        .sort_values(['date', 'value'], ascending=[True, False])
        .reset_index(drop=True)
    )
    
    # 2. Volume analysis (thousand bbl)
    volume_data = df_oil_import_with_continents[
        df_oil_import_with_continents['unit'] == 'thousand bbl'
    ].copy()
    
    volume_by_region = (
        volume_data.groupby(['date', 'region'])['value']
        .sum()
        .reset_index()
        .sort_values(['date', 'value'], ascending=[True, False])
    )
    
    # 3. Value analysis (thousand USD)
    value_data = df_oil_import_with_continents[
        df_oil_import_with_continents['unit'] == 'thousand USD'
    ].copy()
    
    value_by_region = (
        value_data.groupby(['date', 'region'])['value']
        .sum()
        .reset_index()
        .sort_values(['date', 'value'], ascending=[True, False])
    )
    
    # 4. Price analysis (USD/bbl)
    price_data = df_oil_import_with_continents[
        df_oil_import_with_continents['unit'] == 'USD/bbl'
    ].copy()
    
    price_by_region = (
        price_data.groupby(['date', 'region'])['value']
        .mean()  # Average price per region per date
        .reset_index()
        .sort_values(['date', 'value'], ascending=[True, False])
    )
    
    # 5. Import dependency analysis
    latest_date = df_oil_import_with_continents['date'].max()
    latest_shares = continent_share[continent_share['date'] == latest_date]
    
    dependency_risk = {
        'dominant_supplier': latest_shares.loc[latest_shares['value'].idxmax(), 'region'],
        'max_dependency': float(latest_shares['value'].max()),
        'supplier_count': int(latest_shares['region'].nunique()),
    }
    
    # 6. Dominant Supplier Trend
    dominant_region_trend = dependency_risk.get('dominant_supplier')
    n_months = 12
    start_date = latest_date - DateOffset(months=n_months)

    # Filter only for that region and recent months
    trend_df = (
        continent_share[
            (continent_share['region'] == dominant_region_trend) &
            (continent_share['date'] >= start_date)
        ]
        .sort_values('date')
        .loc[:, ['date', 'value']]
        .rename(columns={'value': 'dominant_region_share'})
    )
    
    # Add the dominant_region_name column
    trend_df['dominant_region_name'] = dominant_region_trend

    return {
        'regional_share_trends': continent_share_summary,
        'volume_by_region': volume_by_region,
        'value_by_region': value_by_region,
        'price_by_region': price_by_region,
        'dependency_analysis': dependency_risk,
        'dominant_supplier_trend': trend_df,
        'metric_breakdown': df_oil_import_with_continents.groupby('metric_type')['value'].describe()
    }

# OPEC insights integration
def integrate_opec_insights(df_opec_summary):

    opec_analysis = {}
    for _, row in df_opec_summary.iterrows():
        topic = row['topic']
        insight = row['insight']
        
        if topic not in opec_analysis:
            opec_analysis[topic] = []
        opec_analysis[topic].append(insight)
    
    # Create summary metrics
    opec_summary_stats = {
        'total_insights': int(len(df_opec_summary)),
        'unique_topics': int(df_opec_summary['topic'].nunique()),
        'topics_covered': list(df_opec_summary['topic'].unique()),
        'insights_by_topic': opec_analysis
    }
    
    return opec_summary_stats

# Main analysis function
def save_eda_data(df_iea_oil_stocks, df_oil_import_with_continents, df_opec_summary, output_dir=eda_path):

    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw data
    df_iea_oil_stocks.to_csv(f'{output_dir}/iea_stocks_raw.csv', index=False, encoding='utf-8-sig')
    df_oil_import_with_continents.to_csv(f'{output_dir}/oil_imports_raw.csv', index=False, encoding='utf-8-sig')
    df_opec_summary.to_csv(f'{output_dir}/opec_summary_raw.csv', index=False, encoding='utf-8-sig')
    
    # Run analyses
    stock_analysis_results = stock_time_series_analysis(df_iea_oil_stocks)
    import_analysis_results = oil_import_analysis(df_oil_import_with_continents)
    opec_insights = integrate_opec_insights(df_opec_summary)
    
    # Save individual analysis components
    for key, df in stock_analysis_results.items():
        if isinstance(df, pd.DataFrame):
            df.to_csv(f'{output_dir}/stock_{key}.csv', index=False, encoding='utf-8-sig')
    
    for key, df in import_analysis_results.items():
        if isinstance(df, pd.DataFrame):
            df.to_csv(f'{output_dir}/import_{key}.csv', index=False, encoding='utf-8-sig')

    # Build comprehensive key insights
    key_insights = {
        # Stock Analysis
        "stock_analysis": {
            "total_countries": int(df_iea_oil_stocks['country'].nunique()),
            "date_range": {
                "earliest": df_iea_oil_stocks['date'].min().strftime('%Y-%m-%d'),
                "latest": df_iea_oil_stocks['date'].max().strftime('%Y-%m-%d')
            },
            "top_stockpilers": stock_analysis_results.get('stockpile_statistics', pd.DataFrame()).head(5).to_dict('records'),
            "volatility_leaders": stock_analysis_results.get('volatility_analysis', pd.DataFrame()).head(5).to_dict('records')
        },
        
        # Import Analysis  
        "import_analysis": {
            "total_records": len(df_oil_import_with_continents),
            "regions_covered": int(df_oil_import_with_continents['region'].nunique()),
            "metric_types": list(df_oil_import_with_continents['unit'].unique()),
            "dependency_risk": import_analysis_results.get('dependency_analysis', {})
        },

        # Data Quality
        "data_quality": {
            "stocks_data_completeness": float((df_iea_oil_stocks.notna().sum() / len(df_iea_oil_stocks)).mean()),
            "imports_data_completeness": float((df_oil_import_with_continents.notna().sum() / len(df_oil_import_with_continents)).mean()),
            "has_complete_dataset": bool(all([not df_iea_oil_stocks.empty, not df_oil_import_with_continents.empty, not df_opec_summary.empty]))
        },
        
        "summary_statistics": {
            "total_iea_stocks_latest_value": float(stock_analysis_results['stockpile_statistics'].iloc[0]['latest_stock']),
            "top_import_region_volume": import_analysis_results['volume_by_region'].iloc[0]['region'],
            "top_import_volume_value": float(import_analysis_results['volume_by_region'].iloc[0]['value']),
            "avg_import_price_latest": float(import_analysis_results['price_by_region'].loc[lambda df: df['date'] == df['date'].max(), 'value'].mean()
            ),
        },
        "value_analysis": {
            "stock_value_distribution": {
                "min": float(df_iea_oil_stocks['value'].min()),
                "max": float(df_iea_oil_stocks['value'].max()),
                "mean": float(df_iea_oil_stocks['value'].mean()),
                "std": float(df_iea_oil_stocks['value'].std()),
            },
            "import_value_distribution": {
                "min": float(df_oil_import_with_continents[df_oil_import_with_continents['unit'] == 'thousand USD']['value'].min()),
                "max": float(df_oil_import_with_continents[df_oil_import_with_continents['unit'] == 'thousand USD']['value'].max()),
                "mean": float(df_oil_import_with_continents[df_oil_import_with_continents['unit'] == 'thousand USD']['value'].mean()),
                "std": float(df_oil_import_with_continents[df_oil_import_with_continents['unit'] == 'thousand USD']['value'].std()),
            }
        },
        "temporal_analysis": {
            "stock_dates": {
                "earliest": df_iea_oil_stocks['date'].min().strftime('%Y-%m-%d'),
                "latest": df_iea_oil_stocks['date'].max().strftime('%Y-%m-%d')
            },
            "import_dates": {
                "earliest": df_oil_import_with_continents['date'].min().strftime('%Y-%m-%d'),
                "latest": df_oil_import_with_continents['date'].max().strftime('%Y-%m-%d')
            }
        },
    }
    
    # Save key insights
    with open(f"{output_dir}/key_insights.json", "w", encoding='utf-8') as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False, default=str)
    
    return key_insights

# Gemini Insight
def generate_insights(key_insights, df_opec_summary_df, output_dir):
    try:
        # Prepare the OPEC summary text from the DataFrame
        opec_insight_text = "\n".join([f"Topic: {row['topic']} - Insight: {row['insight']}" for _, row in df_opec_summary_df.iterrows()])

        prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects in the energy market. Extract non-obvious implications and strategic insights from the provided data.

**Data Inputs**:
1. OPEC Monthly Report Summary:
\"\"\"
{opec_insight_text}
\"\"\"

2. Summary Statistics:
{json.dumps(key_insights.get("summary_statistics", {}), indent=2, ensure_ascii=False)}

3. Stock Analysis Results:
{json.dumps(key_insights.get("stock_analysis", {}), indent=2, ensure_ascii=False)}

4. Import Dependency Analysis:
{json.dumps(key_insights.get("import_analysis", {}).get("dependency_risk", {}), indent=2, ensure_ascii=False)}

5. Value Distribution Analysis:
{json.dumps(key_insights.get("value_analysis", {}), indent=2, ensure_ascii=False)}

6. Timeline: {key_insights.get('temporal_analysis', {}).get('stock_dates', {}).get('earliest', 'N/A')} to {key_insights.get('temporal_analysis', {}).get('stock_dates', {}).get('latest', 'N/A')}

---

### **Required Output Format**
```markdown
## Energy Second-Order Analysis

### Core Trend
• Energy: [TREND SUMMARY IN 5-10 WORDS]
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
        print(f"Error details: {e}")

# Main execution
def main():
    print("🛢️ Starting Energy Market Analysis...")
    
    # Load all datasets
    df_iea_oil_stocks = load_iea_oil_stocks_data()
    df_oil_import_with_continents = load_oil_import_with_continents_data()
    df_opec_summary = load_opec_summary_data()

    print("📊 Data Loading Summary:")
    print(f"- IEA Oil Stocks: {len(df_iea_oil_stocks)} records")
    print(f"- Oil Imports by Region: {len(df_oil_import_with_continents)} records")
    print(f"- OPEC Summary Insights: {len(df_opec_summary)} records")
    
    # Run comprehensive analysis
    insights = save_eda_data(df_iea_oil_stocks, df_oil_import_with_continents, df_opec_summary)
    
    # Generate AI insights
    generate_insights(insights, df_opec_summary, eda_path)

    print(f"\n✅ Energy market analysis completed successfully!")
    print(f"📁 Results saved to: {eda_path}")
    print("📊 Files created:")
    print("- *_raw.csv (original datasets)")
    print("- stock_*.csv (stock analysis results)")
    print("- import_*.csv (import analysis results)")
    print("- key_insights.json (comprehensive metrics)")
    print("- gemini_insight.txt (AI strategic analysis)")
    
    return insights

if __name__ == "__main__":
    main()