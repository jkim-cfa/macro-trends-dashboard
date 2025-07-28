import os
import warnings
import pandas as pd
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv
import numpy as np
import google.generativeai as genai

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR", "eda_outputs")
eda_path = os.path.join(EDA_DIR, "outputs", "industry")
os.makedirs(eda_path, exist_ok=True)

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Mapping dictionary
indicator_rename_map = {
    '설비투자지수': 'Equipment Investment Index',
    '제조업 재고율': 'Manufacturing Inventory Ratio',
}

# Load manufacturing inventory datasets
def load_manufacturing_inventory_data():
    query = """
    SELECT date, category, value, source
    FROM industry_manufacture_inventory_processed
    ORDER BY date
    """
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    df['category'] = df['category'].map(lambda x: indicator_rename_map.get(x, x))
    return df

# Load steel production datasets
def load_steel_production_data():
    query = """
    SELECT date, region, indicator, value, unit, source
    FROM industry_steel_combined_processed
    ORDER BY date
    """
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Manufacturing inventory analysis
def manufacturing_inventory_analysis(df):
    df = df.copy()
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    all_processed = []
    volatility_results = []
    trend_stats_all = {}

    for category, group in df.groupby('category'):
        group = group.sort_values('date').copy()

        # Basic indicators
        group['mom_change'] = group['value'].pct_change() * 100
        group['yoy_change'] = group['value'].pct_change(periods=12) * 100
        group['ma_3m'] = group['value'].rolling(window=3, min_periods=1).mean()
        group['ma_12m'] = group['value'].rolling(window=12, min_periods=1).mean()
        group['above_3m_ma'] = (group['value'] > group['ma_3m']).astype(int)
        group['above_12m_ma'] = (group['value'] > group['ma_12m']).astype(int)

        # Momentum
        def calculate_momentum(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            slope = np.polyfit(x, series, 1)[0]
            return slope / series.mean() if series.mean() != 0 else 0

        group['momentum_3m'] = group['value'].rolling(3, min_periods=2).apply(calculate_momentum)
        group['momentum_6m'] = group['value'].rolling(6, min_periods=3).apply(calculate_momentum)

        # Volatility
        current_date = group['date'].max()
        for label, months in {'3M': 3, '6M': 6, '12M': 12}.items():
            subset = group[group['date'] >= current_date - pd.DateOffset(months=months)]
            values = subset['value']
            if len(values) > 1:
                rolling_std = values.rolling(window=min(3, len(values))).std()
                high_vol_periods = (rolling_std > rolling_std.quantile(0.75)).sum()

                volatility_results.append({
                    'indicator': category,
                    'period': label,
                    'data_points': len(values),
                    'current_value': values.iloc[-1],
                    'period_return': ((values.iloc[-1] / values.iloc[0]) - 1) * 100,
                    'volatility_std': values.std(),
                    'high_volatility_periods': int(high_vol_periods),
                    'volatility_classification': 'High' if values.std() > group['value'].std() else 'Normal'
                })

        # Trend stats
        mom_std = group['mom_change'].std()
        yoy_std = group['yoy_change'].std()
        trend_stats_all[category] = {
            'total_data_points': len(group),
            'avg_mom_change': group['mom_change'].mean(),
            'avg_yoy_change': group['yoy_change'].mean(),
            'months_above_3m_ma': group['above_3m_ma'].sum(),
            'months_above_12m_ma': group['above_12m_ma'].sum(),
            'significant_mom_increases': (group['mom_change'] > mom_std).sum() if not pd.isna(mom_std) else 0,
            'significant_mom_decreases': (group['mom_change'] < -mom_std).sum() if not pd.isna(mom_std) else 0,
            'positive_momentum_3m': (group['momentum_3m'] > 0).sum(),
            'positive_momentum_6m': (group['momentum_6m'] > 0).sum(),
            'trend_consistency': {
                'mom_volatility': mom_std,
                'yoy_volatility': yoy_std,
                'current_trend': (
                    'Positive' if group['momentum_3m'].iloc[-1] > 0
                    else 'Negative' if group['momentum_3m'].iloc[-1] < 0
                    else 'Neutral'
                )
            }
        }

        all_processed.append(group)

    return {
        'processed_data': pd.concat(all_processed),
        'volatility_analysis': pd.DataFrame(volatility_results),
        'trend_statistics': trend_stats_all
    }

# Steel production analysis
def steel_production_analysis(df):
    # Extract start and end dates from the data
    start_date = df['date'].min()
    end_date = df['date'].max()

    # Format the period labels
    jan_to_label = f"{start_date.strftime('%b')}–{end_date.strftime('%b %Y')}"
    current_month_label = end_date.strftime('%B %Y')

    # Separate cumulative (e.g., Jan–May) and single-month (e.g., May) data
    jan_to_current = df[df['indicator'].str.contains('–', na=False)].copy()
    current_month = df[~df['indicator'].str.contains('–', na=False)].copy()

    # Top/bottom performers
    top_jan_to_current = jan_to_current.nlargest(5, 'value')[['region', 'value']]
    bottom_jan_to_current = jan_to_current.nsmallest(5, 'value')[['region', 'value']]
    top_current_month = current_month.nlargest(5, 'value')[['region', 'value']]
    bottom_current_month = current_month.nsmallest(5, 'value')[['region', 'value']]

    # World comparison (delta from global average)
    world_jan_to_current = jan_to_current[jan_to_current['region'] == 'World']['value'].values[0]
    world_current_month = current_month[current_month['region'] == 'World']['value'].values[0]

    jan_to_current['vs_world'] = jan_to_current['value'] - world_jan_to_current
    current_month['vs_world'] = current_month['value'] - world_current_month

    # Focus on major economies
    majors = ['China', 'United States']
    major_jan_to_current = jan_to_current[jan_to_current['region'].isin(majors)][['region', 'value']]
    major_current_month = current_month[current_month['region'].isin(majors)][['region', 'value']]

    return {
        'top_bottom': {
            'top_jan_current': top_jan_to_current,
            'bottom_jan_current': bottom_jan_to_current,
            'top_current': top_current_month,
            'bottom_current': bottom_current_month
        },
        'vs_world': {
            'jan_current': jan_to_current[['date', 'region', 'value', 'vs_world']],
            'current': current_month[['date', 'region', 'value', 'vs_world']]
        },
        'major_economies': {
            'jan_current': major_jan_to_current,
            'current': major_current_month
        },
        'metadata': {
            'jan_to_period': jan_to_label,
            'current_month': current_month_label
        }
    }

# Save EDA output and build key insights
def save_eda_data(df_inventory, df_steel, output_dir=eda_path):
    os.makedirs(output_dir, exist_ok=True)
    df_inventory.to_csv(f"{output_dir}/manufacturing_inventory_raw.csv", index=False, encoding="utf-8-sig")
    df_steel.to_csv(f"{output_dir}/steel_production_raw.csv", index=False, encoding="utf-8-sig")

    inv_results = manufacturing_inventory_analysis(df_inventory)
    steel_results = steel_production_analysis(df_steel)

    for k, v in inv_results.items():
        if isinstance(v, pd.DataFrame):
            v.to_csv(f"{output_dir}/inventory_{k}.csv", index=False, encoding="utf-8-sig")
    for k, v in steel_results.items():
        if isinstance(v, pd.DataFrame):
            v.to_csv(f"{output_dir}/steel_{k}.csv", index=False, encoding="utf-8-sig")

    key_insights = {
        "manufacturing_inventory": {
            "latest_date": inv_results["processed_data"]["date"].max().strftime("%Y-%m-%d"),
            "average_mom_change": round(np.mean([v["avg_mom_change"] for v in inv_results["trend_statistics"].values()]), 2),
            "average_yoy_change": round(np.mean([v["avg_yoy_change"] for v in inv_results["trend_statistics"].values()]), 2),
            "trend_consistency": {
                cat: v["trend_consistency"] for cat, v in inv_results["trend_statistics"].items()
            },
            "volatility_summary": inv_results["volatility_analysis"].to_dict("records"),
        },
        "steel_production": {
        "top_current_performers": steel_results["top_bottom"].get("top_current", pd.DataFrame()).to_dict("records"),
        "bottom_current_performers": steel_results["top_bottom"].get("bottom_current", pd.DataFrame()).to_dict("records"),
        "vs_world_comparison": steel_results["vs_world"]["current"].to_dict("records"),
        "major_economies": {
            "jan_current": steel_results["major_economies"]["jan_current"].to_dict("records"),
            "current": steel_results["major_economies"]["current"].to_dict("records")
        }
    },
    }

    with open(f"{output_dir}/key_insights.json", "w", encoding="utf-8") as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False, default=str)

    return key_insights

# Gemini insights
def generate_insights(key_insights, output_dir):
    try:
        inv = key_insights["manufacturing_inventory"]
        steel = key_insights["steel_production"]

        inventory_preview = f"""
- Latest Date: {inv.get("latest_date", "N/A")}
- Avg MoM Change: {round(inv.get("average_mom_change", 0.0), 2)}
- Avg YoY Change: {round(inv.get("average_yoy_change", 0.0), 2)}
- High Volatility Entries: {len(inv.get("volatility_summary", []))}
"""

        top = steel.get("top_current_performers", [])
        bottom = steel.get("bottom_current_performers", [])

        trend_lines = []
        for cat, t in inv.get("trend_consistency", {}).items():
            label = f"{cat}: {t.get('current_trend', 'Unknown')} (MoM σ={round(t.get('mom_volatility', 0.0),2)})"
            trend_lines.append(label)
        inventory_preview += "- Trend Signals:\n  " + "\n  ".join(trend_lines) + "\n"

        steel_preview = f"""
- Top Current Performers: {', '.join([d.get('region', 'N/A') for d in top])}
- Bottom Current Performers: {', '.join([d.get('region', 'N/A') for d in bottom])}
- Major Economies Tracked: {len(steel.get("major_economies", {}).get("current", []))}
- Global vs Regional Differentials: {len(steel.get("vs_world_comparison", []))}
"""

        prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects.

**Data Inputs**:

1. 📦 Manufacturing Inventory:
{inventory_preview}

2. 🏭 Steel Production:
{steel_preview}

3. 🧠 Full Key Insights JSON:
{json.dumps(key_insights, indent=2, ensure_ascii=False, default=str)}

---

### **Required Output Format**
## Industry Sector Second-Order Effect Analysis

### Core Trend
• Industry: [TREND SUMMARY IN 5–10 WORDS]  
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
        response_text = response.text.strip() if hasattr(response, "text") else str(response)

        os.makedirs(output_dir, exist_ok=True)
        with open(f"{output_dir}/gemini_insight.txt", "w", encoding="utf-8") as f:
            f.write(response_text)

        print("✅ Gemini insights generated and saved.")

    except Exception as e:
        print(f"❌ Gemini insight generation failed: {e}")

# Main execution
def main():
    df_inventory = load_manufacturing_inventory_data()
    df_steel = load_steel_production_data()

    print("🔍 Loaded datasets:")
    print(f"- Manufacturing inventory: {len(df_inventory)} rows")
    print(f"- Steel production: {len(df_steel)} rows")

    key_insights = save_eda_data(df_inventory, df_steel, eda_path)

    if key_insights["manufacturing_inventory"]["average_yoy_change"] is not None and \
       key_insights["steel_production"]["top_current_performers"]:
        generate_insights(key_insights, eda_path)
    else:
        print("⚠️ Gemini generation skipped due to missing data.")

    print("✅ EDA complete. Ready for Streamlit visualizations.")

if __name__ == "__main__":
    main()
