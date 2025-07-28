import os
import warnings
import pandas as pd
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv
import numpy as np
import google.generativeai as genai
from scipy.stats import pearsonr

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR")
eda_path = os.path.join(EDA_DIR, "outputs", "economy")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Example mapping dictionary
indicator_rename_map = {
    '선행지수순환변동치': 'Leading Index',
    '동행지수순환변동치': 'Coincident Index',
    '선행-동행': 'Leading–Coincident Spread',
}

sentiment_rename_map = {
    '경제심리지수(순환변동치)': 'Economic Sentiment Index (Adjusted)',
    '경제심리지수(원계열)': 'Economic Sentiment Index (Raw)',
    '뉴스심리지수': 'News Sentiment Index'
}

# Load economic sentiment datasets
def load_economy_sentiment_data():
    query = """
    SELECT date, category, indicator, value, unit, source
    FROM economy_economy_confidence_processed
    ORDER BY date
    """
    df_sentiment = pd.read_sql(query, engine)
    df_sentiment['date'] = pd.to_datetime(df_sentiment['date'])
    df_sentiment['indicator'] = df_sentiment['indicator'].replace(sentiment_rename_map)
    return df_sentiment

# Load FX datasets
def load_fx_data():
    query = """
    SELECT date, currency, quote, exchange_rate, unit, source
    FROM economy_fx_rates_processed
    ORDER BY date
    """
    df_fx = pd.read_sql(query, engine)
    df_fx['date'] = pd.to_datetime(df_fx['date'])
    df_fx['pair'] = df_fx['currency'] + '/' + df_fx['quote']
    return df_fx

# Load economic indicators datasets
def load_economic_indicators_data():
    query = """
    SELECT date, indicator, value, unit, source
    FROM economy_leading_vs_coincident_kospi_processed
    ORDER BY date
    """
    df_economic_indicators = pd.read_sql(query, engine)
    df_economic_indicators['date'] = pd.to_datetime(df_economic_indicators['date'])
    df_economic_indicators['indicator'] = df_economic_indicators['indicator'].replace(indicator_rename_map)
    return df_economic_indicators

# Helper functions for key insights
def get_latest_value(df, indicator_name, value_col='value'):
    if df.empty:
        return None
    
    if 'indicator' in df.columns:
        filtered = df[df['indicator'] == indicator_name]
    elif 'currency' in df.columns:
        filtered = df[df['currency'] == indicator_name]
    elif 'pair' in df.columns:
        filtered = df[df['pair'] == indicator_name]
    else:
        return None
    
    return float(filtered[value_col].iloc[-1]) if not filtered.empty else None

def get_trend(df, indicator_name, value_col='value'):
    if df.empty:
        return None
    if 'indicator' in df.columns:
        filtered = df[df['indicator'] == indicator_name].sort_values('date')
    elif 'currency' in df.columns:
        filtered = df[df['currency'] == indicator_name].sort_values('date')
    elif 'pair' in df.columns:
        filtered = df[df['pair'] == indicator_name].sort_values('date')
    else:
        return None
    
    if len(filtered) >= 3:
        recent_values = filtered[value_col].tail(3)
        return float(recent_values.pct_change().mean() * 100)  # % change
    return None

# Sentiment indicators analysis
def sentiment_indicators_analysis(sentiment_df):
    if sentiment_df.empty:
        return sentiment_df

    sentiment_processed = sentiment_df.copy()
    sentiment_processed = sentiment_processed.sort_values(['indicator', 'date'])

    # Momentum (MoM % change)
    sentiment_processed['momentum'] = sentiment_processed.groupby('indicator')['value'].pct_change()

    # Absolute difference
    sentiment_processed['value_lag1'] = sentiment_processed.groupby('indicator')['value'].shift(1)
    sentiment_processed['value_change'] = sentiment_processed['value'] - sentiment_processed['value_lag1']

    # Rolling Averages
    sentiment_processed['ma_3m'] = sentiment_processed.groupby('indicator')['value'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    sentiment_processed['ma_6m'] = sentiment_processed.groupby('indicator')['value'].transform(
        lambda x: x.rolling(window=6, min_periods=1).mean()
    )

    # Business-rule categorisation
    def categorize_sentiment(value):
        if pd.isna(value):
            return 'Unknown'
        if value > 110:
            return 'Very Positive'
        elif value > 105:
            return 'Positive'
        elif value >= 95:
            return 'Neutral'
        elif value >= 90:
            return 'Negative'
        else:
            return 'Very Negative'

    sentiment_processed['sentiment_strength'] = sentiment_processed['value'].apply(categorize_sentiment)

    return sentiment_processed

# FX analysis
def fx_analysis(fx_df):
    if fx_df.empty:
        return fx_df, []

    df_fx = fx_df.copy()
    volatility_data = []

    latest_date = df_fx['date'].max()
    three_months_ago = latest_date - pd.DateOffset(months=3)
    twelve_months_ago = latest_date - pd.DateOffset(months=12)

    for pair in df_fx['pair'].unique():
        pair_data = df_fx[df_fx['pair'] == pair].sort_values('date').copy()

        # Full returns column
        pair_data['returns'] = pair_data['exchange_rate'].pct_change()

        # --- 3-month volatility ---
        recent_3m = pair_data[pair_data['date'] >= three_months_ago]
        if len(recent_3m) > 1:
            vol_3m = recent_3m['returns'].std() * 100
            volatility_data.append({
                'date': recent_3m['date'].iloc[-1].strftime('%Y-%m-%d'),
                'indicator': f"{pair} Volatility (3M)",
                'value': vol_3m,
                'category': 'FX Volatility',
                'pair': pair,
                'current_rate': recent_3m['exchange_rate'].iloc[-1],
                'rate_range': recent_3m['exchange_rate'].max() - recent_3m['exchange_rate'].min(),
                'data_points': len(recent_3m)
            })

        # --- 12-month volatility ---
        recent_12m = pair_data[pair_data['date'] >= twelve_months_ago]
        if len(recent_12m) > 1:
            vol_12m = recent_12m['returns'].std() * 100
            volatility_data.append({
                'date': recent_12m['date'].iloc[-1].strftime('%Y-%m-%d'),
                'indicator': f"{pair} Volatility (12M)",
                'value': vol_12m,
                'category': 'FX Volatility',
                'pair': pair,
                'current_rate': recent_12m['exchange_rate'].iloc[-1],
                'rate_range': recent_12m['exchange_rate'].max() - recent_12m['exchange_rate'].min(),
                'data_points': len(recent_12m)
            })

    return df_fx, volatility_data

# Key economic indicators analysis
def key_indicators_analysis(df_economic_indicators):
    if df_economic_indicators.empty:
        return df_economic_indicators
        
    df_processed = df_economic_indicators.copy()
    
    # Add trend analysis
    for indicator in df_processed['indicator'].unique():
        mask = df_processed['indicator'] == indicator
        indicator_data = df_processed[mask].sort_values('date').copy()

        # Calculate rolling trend using trailing 3 values (pct_change between them)
        indicator_data['trend_3m'] = indicator_data['value'].pct_change().rolling(2).mean()
        
        # Assign back
        df_processed.loc[mask, 'trend_3m'] = indicator_data['trend_3m'].values
    
    return df_processed

# Cross-correlation analysis
def cross_correlation_analysis(df_economic_indicators, df_fx):
    correlation_results = []

    if df_economic_indicators.empty:
        return pd.DataFrame(correlation_results)

    # KOSPI vs USD/KRW correlation
    kospi_data = df_economic_indicators[df_economic_indicators['indicator'] == 'KOSPI'][['date', 'value']].rename(columns={'value': 'KOSPI'})
    
    # Look for USD/KRW pair (should already have pair column from load_fx_data)
    if not df_fx.empty and 'USD/KRW' in df_fx['pair'].values:
        usd_krw_data = df_fx[df_fx['pair'] == 'USD/KRW'][['date', 'exchange_rate']].rename(columns={'exchange_rate': 'USD_KRW'})
        
        if not kospi_data.empty and not usd_krw_data.empty:
            merged_data = pd.merge(kospi_data, usd_krw_data, on='date', how='inner')
            if len(merged_data) > 1:
                correlation, p_value = pearsonr(merged_data['KOSPI'], merged_data['USD_KRW'])
                correlation_results.append({
                    'indicator_1': 'KOSPI',
                    'indicator_2': 'USD/KRW',
                    'correlation': correlation,
                    'p_value': p_value,
                    'significance': 'Significant' if p_value < 0.05 else 'Not Significant',
                    'data_points': len(merged_data),
                    'category': 'Cross-Asset Correlation'
                })

    # Leading vs Coincident indicators correlation
    leading_data = df_economic_indicators[df_economic_indicators['indicator'] == 'Leading Index'][['date', 'value']].rename(columns={'value': 'leading'})
    coincident_data = df_economic_indicators[df_economic_indicators['indicator'] == 'Coincident Index'][['date', 'value']].rename(columns={'value': 'coincident'})
    
    if not leading_data.empty and not coincident_data.empty:
        merged_indices = pd.merge(leading_data, coincident_data, on='date', how='inner')
        if len(merged_indices) > 1:
            correlation, p_value = pearsonr(merged_indices['leading'], merged_indices['coincident'])
            correlation_results.append({
                'indicator_1': 'Leading Index',
                'indicator_2': 'Coincident Index', 
                'correlation': correlation,
                'p_value': p_value,
                'significance': 'Significant' if p_value < 0.05 else 'Not Significant',
                'data_points': len(merged_indices),
                'category': 'Economic Indices Correlation'
            })

    return pd.DataFrame(correlation_results)

def save_eda_data(df_economic_indicators, df_fx, df_sentiment, output_dir=eda_path):
    os.makedirs(output_dir, exist_ok=True)

    df_fx, fx_volatility_data = fx_analysis(df_fx)

    # Save raw data
    df_sentiment.to_csv(f'{output_dir}/sentiment_raw.csv', index=False, encoding='utf-8-sig')
    df_fx.to_csv(f'{output_dir}/fx_raw.csv', index=False, encoding='utf-8-sig')
    df_economic_indicators.to_csv(f'{output_dir}/economic_indicators_raw.csv', index=False, encoding='utf-8-sig')

    # Processed data
    key_indicators_df = key_indicators_analysis(df_economic_indicators)
    key_indicators_df.to_csv(f'{output_dir}/key_indicators_processed.csv', index=False, encoding='utf-8-sig')

    sentiment_analysis_df = sentiment_indicators_analysis(df_sentiment)
    sentiment_analysis_df.to_csv(f'{output_dir}/sentiment_processed.csv', index=False, encoding='utf-8-sig')

    correlation_df = cross_correlation_analysis(df_economic_indicators, df_fx)
    correlation_df.to_csv(f'{output_dir}/cross_correlations.csv', index=False, encoding='utf-8-sig')

    # FX Volatility (last 3 months)
    last_3_months_volatility = []
    if fx_volatility_data:
        fx_vol_df = pd.DataFrame(fx_volatility_data)
        last_3_months_volatility = fx_volatility_data

    # Leading-Coincident spread average
    leading_coincident_avg = None
    if 'Leading–Coincident Spread' in df_economic_indicators['indicator'].values:
        leading_coincident_avg = df_economic_indicators[df_economic_indicators['indicator'] == 'Leading–Coincident Spread']['value'].mean()

    # Build key insights
    key_insights = {
        # Market Data
        "market_indicators": {
            "kospi": {
                "latest": get_latest_value(df_economic_indicators, 'KOSPI'),
                "trend_3m": get_trend(df_economic_indicators, 'KOSPI'),
            },
            "leading_index": {
                "latest": get_latest_value(df_economic_indicators, 'Leading Index'),
                "trend_3m": get_trend(df_economic_indicators, 'Leading Index'),
            },
            "coincident_index": {
                "latest": get_latest_value(df_economic_indicators, 'Coincident Index'),
                "trend_3m": get_trend(df_economic_indicators, 'Coincident Index'),
            },
            "leading_coincident_spread": {
                "average": float(leading_coincident_avg) if pd.notna(leading_coincident_avg) else None,
                "latest": get_latest_value(df_economic_indicators, 'Leading–Coincident Spread'),
                "interpretation": "positive_leading" if leading_coincident_avg and leading_coincident_avg > 0 else "negative_leading" if leading_coincident_avg else "unknown"
            }
        },
        
        # FX Analysis - Use df_fx directly since it has pair column
        "fx_analysis": {
            "volatility_data": last_3_months_volatility,
            "usd_krw_latest": get_latest_value(df_fx, 'USD/KRW', 'exchange_rate') if not df_fx.empty else None,
            "available_pairs": list(df_fx['pair'].unique()) if not df_fx.empty else [],
            "data_points": len(df_fx)
        },
        
        # Sentiment Analysis
        "sentiment_analysis": {
            "available_indicators": list(df_sentiment['indicator'].unique()) if not df_sentiment.empty else [],
            "latest_sentiment": {},  # Will be filled below
            "data_points": len(df_sentiment)
        },
        
        # Correlation Analysis
        "correlations": {
            "results": correlation_df.to_dict('records') if not correlation_df.empty else [],
            "significant_correlations": len(correlation_df[correlation_df['significance'] == 'Significant']) if not correlation_df.empty else 0,
            "total_correlations": len(correlation_df) if not correlation_df.empty else 0
        },
        
        # Data Quality & Coverage
        "data_quality": {
            "economic_indicators": {
                "total_records": len(df_economic_indicators),
                "date_range": {
                    "earliest": df_economic_indicators['date'].min().strftime('%Y-%m-%d') if not df_economic_indicators.empty else None,
                    "latest": df_economic_indicators['date'].max().strftime('%Y-%m-%d') if not df_economic_indicators.empty else None
                },
                "unique_indicators": df_economic_indicators['indicator'].nunique() if not df_economic_indicators.empty else 0
            },
            "fx_data": {
                "total_records": len(df_fx),
                "currency_pairs": df_fx['pair'].nunique() if not df_fx.empty else 0
            },
            "sentiment_data": {
                "total_records": len(df_sentiment),
                "unique_indicators": df_sentiment['indicator'].nunique() if not df_sentiment.empty else 0
            }
        },
        
        # Summary Flags for Quick Assessment
        "health_check": {
            "has_market_data": not df_economic_indicators.empty,
            "has_fx_data": not df_fx.empty,
            "has_sentiment_data": not df_sentiment.empty,
            "has_correlations": not correlation_df.empty,
            "complete_dataset": all([
                not df_economic_indicators.empty,
                not df_fx.empty,
                not df_sentiment.empty
            ])
        }
    }
    
    # Fill sentiment latest values
    if not df_sentiment.empty:
        for indicator in df_sentiment['indicator'].unique():
            latest_val = get_latest_value(df_sentiment, indicator)
            if latest_val is not None:
                key_insights["sentiment_analysis"]["latest_sentiment"][indicator] = latest_val
    
    # Save insights
    with open(f"{output_dir}/key_insights.json", "w", encoding='utf-8') as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False, default=str)
    
    return key_insights

# Gemini Insight
def generate_insights(key_insights, output_dir):
    prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects. Extract non-obvious implications from the data below.

**Data Inputs**:
1. Summary Statistics:
{key_insights["market_indicators"]["kospi"]["latest"]}

2. Growth Rates (CAGR):
{key_insights["market_indicators"]["leading_index"]["trend_3m"]}

3. Correlation Matrix:
{key_insights["correlations"]["results"]}

4. Key Metrics:
{json.dumps(key_insights, indent=2)}

5. FX Volatility (last 3 months):
{key_insights["fx_analysis"]["volatility_data"]}

6. Leading-Coincident spread average:
{key_insights["market_indicators"]["leading_coincident_spread"]["average"]}

---

### **Required Output Format**
## Economy Sector Second-Order Effect Analysis

### Core Trend
• Economy: [TREND SUMMARY IN 5–10 WORDS]  
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

    with open(f"{output_dir}/gemini_insights.txt", "w", encoding="utf-8") as f:
        f.write(gemini_insight)

    print("✅ Gemini insights generated and saved.")

# Main execution
def main():
    # Load all datasets
    df_fx = load_fx_data()
    df_sentiment = load_economy_sentiment_data()
    df_economic_indicators = load_economic_indicators_data()
    
    # Run analysis and save results
    insights = save_eda_data(df_economic_indicators, df_fx, df_sentiment)
    
    # Generate AI insights
    generate_insights(insights, eda_path)
    
    print(f"\n✅ All data saved to: {eda_path}")
    print("="*50)

if __name__ == "__main__":
    main()