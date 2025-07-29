import os
import warnings
import pandas as pd
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv
import google.generativeai as genai

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

# Stockpile Analysis
def stock_time_series_analysis(df_iea_oil_stocks):
    """Analyze IEA oil stock data over time, excluding aggregates."""
    if df_iea_oil_stocks.empty:
        return {}

    # Define aggregate entries to exclude
    aggregates = ['Total IEA', 'Total IEA Asia Pacific', 'Total IEA net importers', 'Total IEA Europe']

    # Filter out aggregates once
    df_filtered = df_iea_oil_stocks[~df_iea_oil_stocks['country'].isin(aggregates)].copy()
    df_filtered['month'] = df_filtered['date'].dt.month
    latest_date = df_filtered['date'].max()

    # 1. Country stock ranking (latest values)
    country_ranking = (
        df_filtered[df_filtered['date'] == latest_date]
        .sort_values('value', ascending=False)
        .reset_index(drop=True)
    )

    # 2. Volatility by country
    volatility_by_country = (
        df_filtered.groupby("country")["value"]
        .agg(volatility='std', avg_stock='mean', data_points='count')
        .reset_index()
        .sort_values(by="volatility", ascending=False)
    )

    # 3. Seasonality patterns
    seasonality_by_country = (
        df_filtered.groupby(['month', 'country'])['value']
        .mean()
        .reset_index()
        .rename(columns={'value': 'monthly_avg_stock'})
    )

    # 4. Top stockpilers statistics
    stockpile_stats = (
        df_filtered.groupby("country")
        .agg(
            avg_stock=('value', 'mean'),
            latest_stock=('value', 'last'),
            min_stock=('value', 'min'),
            max_stock=('value', 'max')
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
# Oil Import Analysis - Fixed Version
def oil_import_analysis(df_oil_import_with_continents):
    # Map units to readable metric names
    metric_unit_map = {
        'thousand USD': 'Value',
        'thousand bbl': 'Volume',
        'percentage': 'Share',
        'USD/bbl': 'Price'
    }
    
    # Create metric_type column on a copy to avoid modifying original
    df_oil_import_with_continents = df_oil_import_with_continents.copy()
    df_oil_import_with_continents['metric_type'] = df_oil_import_with_continents['unit'].map(metric_unit_map)
    
    # Data validation: Check for potential aggregates/totals
    def identify_aggregates(df, country_col='country'):
        """Identify rows that might be regional/total aggregates"""
        aggregate_keywords = ['total', 'all', 'aggregate', 'sum', 'world', 'global']
        mask = df[country_col].str.lower().str.contains('|'.join(aggregate_keywords), na=False)
        return mask
    
    # Remove potential country-level aggregates to avoid double counting
    aggregate_mask = identify_aggregates(df_oil_import_with_continents, 'country')
    df_clean = df_oil_import_with_continents[~aggregate_mask].copy()
    
    print(f"Removed {aggregate_mask.sum()} potential aggregate rows from {len(df_oil_import_with_continents)} total rows")
    
    # 1. Regional share analysis (percentage data) - No aggregation needed
    continent_share = df_clean[df_clean['unit'] == 'percentage'].copy()
    
    continent_share_summary = (
        continent_share
        .sort_values(['date', 'value'], ascending=[True, False])
        .reset_index(drop=True)
    )
    
    # 2. Volume analysis (thousand bbl) - Check if aggregation is appropriate
    volume_data = df_clean[df_clean['unit'] == 'thousand bbl'].copy()
    
    # Check if we have individual country data that should be aggregated
    country_count_by_region = volume_data.groupby(['date', 'region'])['country'].nunique()
    regions_with_multiple_countries = country_count_by_region[country_count_by_region > 1]
    
    if len(regions_with_multiple_countries) > 0:
        print(f"Found regions with multiple countries - aggregating volume data")
        volume_by_region = (
            volume_data.groupby(['date', 'region'])
            .agg({
                'value': 'sum',
                'metric_type': 'first',
                'country': 'count'  # Track how many countries were aggregated
            })
            .reset_index()
            .rename(columns={'country': 'country_count'})
            .sort_values(['date', 'value'], ascending=[True, False])
        )
    else:
        print("No aggregation needed for volume data - using as-is")
        volume_by_region = volume_data.copy()
        volume_by_region['country_count'] = 1
    
    # 3. Value analysis (thousand USD) - Same logic as volume
    value_data = df_clean[df_clean['unit'] == 'thousand USD'].copy()
    
    country_count_by_region_value = value_data.groupby(['date', 'region'])['country'].nunique()
    regions_with_multiple_countries_value = country_count_by_region_value[country_count_by_region_value > 1]
    
    if len(regions_with_multiple_countries_value) > 0:
        print(f"Found regions with multiple countries - aggregating value data")
        value_by_region = (
            value_data.groupby(['date', 'region'])
            .agg({
                'value': 'sum',
                'metric_type': 'first',
                'country': 'count'
            })
            .reset_index()
            .rename(columns={'country': 'country_count'})
            .sort_values(['date', 'value'], ascending=[True, False])
        )
    else:
        print("No aggregation needed for value data - using as-is")
        value_by_region = value_data.copy()
        value_by_region['country_count'] = 1
    
    # 4. Price analysis (USD/bbl) - Always use mean for prices
    price_data = df_clean[df_clean['unit'] == 'USD/bbl'].copy()
    
    price_by_region = (
        price_data.groupby(['date', 'region'])
        .agg({
            'value': 'mean',  # Always average for prices
            'metric_type': 'first',
            'country': 'count'
        })
        .reset_index()
        .rename(columns={'country': 'country_count'})
        .sort_values(['date', 'value'], ascending=[True, False])
    )
    
    # 5. Import dependency analysis - Use cleaned percentage data
    latest_date = continent_share['date'].max() if not continent_share.empty else None
    
    if latest_date is not None:
        latest_shares = continent_share[continent_share['date'] == latest_date]
        
        if not latest_shares.empty:
            max_idx = latest_shares['value'].idxmax()
            dependency_risk = {
                'dominant_supplier': latest_shares.loc[max_idx, 'region'],
                'max_dependency': float(latest_shares['value'].max()),
                'supplier_count': int(latest_shares['region'].nunique()),
                'data_date': latest_date.strftime('%Y-%m-%d')
            }
        else:
            dependency_risk = {
                'dominant_supplier': 'Unknown',
                'max_dependency': 0.0,
                'supplier_count': 0,
                'data_date': 'Unknown'
            }
    else:
        dependency_risk = {
            'dominant_supplier': 'Unknown',
            'max_dependency': 0.0,
            'supplier_count': 0,
            'data_date': 'Unknown'
        }
    
    # 6. Dominant Supplier Trend - Enhanced validation
    dominant_region_trend = dependency_risk.get('dominant_supplier')
    n_months = 12
    
    if latest_date is not None and dominant_region_trend != 'Unknown':
        start_date = latest_date - pd.DateOffset(months=n_months)
        
        trend_df = (
            continent_share[
                (continent_share['region'] == dominant_region_trend) &
                (continent_share['date'] >= start_date)
            ]
            .sort_values('date')
            .loc[:, ['date', 'value']]
            .rename(columns={'value': 'dominant_region_share'})
        )
        
        trend_df['dominant_region_name'] = dominant_region_trend
    else:
        trend_df = pd.DataFrame(columns=['date', 'dominant_region_share', 'dominant_region_name'])
    
    # 7. Data quality metrics
    data_quality = {
        'original_rows': len(df_oil_import_with_continents),
        'cleaned_rows': len(df_clean),
        'removed_aggregates': aggregate_mask.sum(),
        'unique_regions': df_clean['region'].nunique(),
        'unique_countries': df_clean['country'].nunique(),
        'date_range': {
            'start': df_clean['date'].min().strftime('%Y-%m-%d') if not df_clean.empty else 'Unknown',
            'end': df_clean['date'].max().strftime('%Y-%m-%d') if not df_clean.empty else 'Unknown'
        }
    }
    
    return {
        'regional_share_trends': continent_share_summary,
        'volume_by_region': volume_by_region,
        'value_by_region': value_by_region,
        'price_by_region': price_by_region,
        'dependency_analysis': dependency_risk,
        'dominant_supplier_trend': trend_df,
        'metric_breakdown': df_clean.groupby('metric_type')['value'].describe() if not df_clean.empty else pd.DataFrame(),
        'data_quality': data_quality
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

    # Safe summary statistics extraction
    stockpile_stats = stock_analysis_results.get('stockpile_statistics', pd.DataFrame())
    volume_data = import_analysis_results.get('volume_by_region', pd.DataFrame())
    price_data = import_analysis_results.get('price_by_region', pd.DataFrame())
    
    # Debug information
    print(f"Volume data shape: {volume_data.shape}")
    print(f"Price data shape: {price_data.shape}")
    if not volume_data.empty:
        print(f"Volume data columns: {volume_data.columns.tolist()}")
        print(f"Volume data sample: {volume_data.head()}")
    
    # Build comprehensive key insights
    key_insights = {
        # Stock Analysis
        "stock_analysis": {
            "total_countries": int(df_iea_oil_stocks['country'].nunique()),
            "date_range": {
                "earliest": df_iea_oil_stocks['date'].min().strftime('%Y-%m-%d'),
                "latest": df_iea_oil_stocks['date'].max().strftime('%Y-%m-%d')
            },
            "top_stockpilers": stockpile_stats.head(5).to_dict('records') if not stockpile_stats.empty else [],
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
            "total_iea_stocks_latest_value": float(stockpile_stats.iloc[0]['latest_stock']) if not stockpile_stats.empty else 0.0,
            "top_import_region_volume": volume_data.loc[volume_data['value'].idxmax(), 'region'] if not volume_data.empty and not volume_data['value'].isna().all() else 'Unknown',
            "top_import_volume_value": float(volume_data['value'].max()) if not volume_data.empty and not volume_data['value'].isna().all() else 0.0,
            "avg_import_price_latest": float(
                price_data.loc[price_data['date'] == price_data['date'].max(), 'value'].mean()
            ) if not price_data.empty and not price_data['date'].isna().all() else 0.0,
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
## Energy Sector Second-Order Effect Analysis

### Core Trend
• Energy: [TREND SUMMARY IN 5–10 WORDS]  
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

### Strategic Recommendations
🛠 **Immediate Actions**: [CONCRETE STEPS]
📊 **Monitoring Metrics**: [KEY INDICATORS]
🎯 **Long-term Strategy**: [STRATEGIC DIRECTION]

### Risk Assessment
⚠️ **High Risk**: [CRITICAL CONCERN]
⚠️ **Medium Risk**: [MODERATE CONCERN]
⚠️ **Low Risk**: [MINOR CONCERN]

### Market Intelligence
📈 **Bullish Signals**: [POSITIVE INDICATORS]
📉 **Bearish Signals**: [NEGATIVE INDICATORS]
🔄 **Neutral Factors**: [BALANCED ELEMENTS]

**Analysis Guidelines**:
- Focus on actionable intelligence
- Consider global geopolitical dynamics
- Assess Korea's competitive positioning
- Identify emerging trends and risks
- Provide specific, measurable recommendations
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
    # Load all datasets
    df_iea_oil_stocks = load_iea_oil_stocks_data()
    df_oil_import_with_continents = load_oil_import_with_continents_data()
    df_opec_summary = load_opec_summary_data()
    
    # Run comprehensive analysis
    insights = save_eda_data(df_iea_oil_stocks, df_oil_import_with_continents, df_opec_summary)
    
    # Generate AI insights
    generate_insights(insights, df_opec_summary, eda_path)

    print(f"\n✅ All data saved to: {eda_path}")
    print("="*50)

if __name__ == "__main__":
    main()