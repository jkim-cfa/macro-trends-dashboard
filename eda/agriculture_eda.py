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
eda_path = os.path.join(EDA_DIR, "outputs", "agriculture")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

def load_agriculture_data(engine):
    query = """
    SELECT *
    FROM agriculture_crop_production_processed
    ORDER BY indicator, date
    """
    return pd.read_sql(query, engine)

def analyse_growth_rates(df):
    growth_data = []
    for commodity in df['commodity'].unique():
        subset = df[(df['commodity'] == commodity)].sort_values('date')
        if len(subset) < 2:
            continue
        start_value = subset.iloc[0]['value']
        end_value = subset.iloc[-1]['value']
        years = (subset.iloc[-1]['date'] - subset.iloc[0]['date']).days / 365.25
        if start_value > 0 and years > 0:
            cagr = (end_value / start_value) ** (1/years) - 1
            growth_data.append({
                'Commodity': commodity,
                'Start Value': start_value,
                'End Value': end_value,
                'CAGR (%)': cagr * 100
            })
    return pd.DataFrame(growth_data).sort_values('CAGR (%)', ascending=False)

# Save
def save_aggregated_data(df, output_dir=eda_path):
    os.makedirs(output_dir, exist_ok=True)
    production_df = df

    # Trend data for line charts
    trend_data = production_df.pivot(index='date', columns='commodity', values='value')
    trend_data.to_csv(f'{output_dir}/production_trends.csv')

    # Summary statistics
    stats_df = production_df.groupby('commodity')['value'].agg(['mean', 'median', 'std', 'min', 'max', 'count'])
    stats_df.to_csv(f'{output_dir}/production_stats.csv')

    # Year-over-year changes
    production_df.sort_values(['commodity', 'date'], inplace=True)
    production_df['yoy_change'] = production_df.groupby('commodity')['value'].pct_change() * 100
    production_df.to_csv(f"{output_dir}/production_yoy_change.csv", index=False)

    # Growth rates
    growth_df = analyse_growth_rates(df)
    growth_df.to_csv(f"{output_dir}/growth_rates.csv", index=False)

    # Correlation matrix
    pivot_df = production_df.pivot(index='date', columns='commodity', values='value')
    corr_matrix = pivot_df.corr()
    corr_matrix.to_csv(f"{output_dir}/correlation_matrix.csv")

    # Clean data for Streamlit
    streamlit_df = production_df[['date', 'commodity', 'value']].copy()
    streamlit_df.to_csv(f"{output_dir}/streamlit_ready_data.csv", index=False)

    # Key insights for AI analysis
    key_insights = {}
    if not growth_df.empty:
        top = growth_df.iloc[0]
        key_insights["highest_growth"] = top['Commodity']
        key_insights["highest_growth_rate"] = round(top['CAGR (%)'], 2)
        key_insights["average_growth"] = round(growth_df['CAGR (%)'].mean(), 2)
    key_insights["most_recent_year"] = int(df['date'].max().year)

    with open(f"{output_dir}/key_insights.json", "w") as f:
        json.dump(key_insights, f, indent=2)

    return stats_df, growth_df, corr_matrix, key_insights

# Gemini Insight
def generate_insights(stats_df, growth_df, corr_matrix, key_insights, output_dir):
    try:
        prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects. Extract non-obvious implications from the data below.

**Data Inputs**:
1. Summary Statistics:
{stats_df.to_markdown(index=False)}

2. Growth Rates (CAGR):
{growth_df.to_markdown(index=False)}

3. Correlation Matrix:
{corr_matrix.to_string(index=False)}

4. Key Metrics:
{json.dumps(key_insights, indent=2)}

---

### **Required Output Format**
## Agriculture Sector Second-Order Effect Analysis

### Core Trend
• Agriculture: [TREND SUMMARY IN 5–10 WORDS]  
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

def main():
    df = load_agriculture_data(engine)
    df['date'] = pd.to_datetime(df['date'])

    print("\n=== Data Overview ===")
    print(f"Time Range: {df['date'].min().year} to {df['date'].max().year}")
    print(f"Commodities: {df['commodity'].nunique()}")
    print(f"Indicators: {df['indicator'].unique()}")

    print("\n=== Summary Stats ===")
    print(df.groupby('commodity')['value'].describe().round(2))

    # Process and save all data
    stats_df, growth_df, corr_matrix, key_insights = save_aggregated_data(df)

    print("\n=== Growth Rates (CAGR) ===")
    print(growth_df.head())

    print("\n=== Correlation Matrix ===")
    print(corr_matrix.round(2))

    # Generate AI insights
    generate_insights(stats_df, growth_df, corr_matrix, key_insights, eda_path)

    print(f"\n✅ All data saved to: {eda_path}")
    print("Files created:")
    print("- production_trends.csv (for trend charts)")
    print("- streamlit_ready_data.csv (clean data for Streamlit)")
    print("- growth_rates.csv (CAGR analysis)")
    print("- correlation_matrix.csv (commodity correlations)")
    print("- gemini_insight.txt (AI analysis)")

if __name__ == "__main__":
    main()