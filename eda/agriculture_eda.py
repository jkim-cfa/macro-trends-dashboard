import os
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
import numpy as np
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

PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "macro2025")
PG_DB = os.getenv("POSTGRES_DB", "macrodb")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

def load_agriculture_data(engine):
    query = """
    SELECT *
    FROM agriculture_crop_production_processed
    ORDER BY indicator, date
    """
    return pd.read_sql(query, engine)

def plot_production_trends(df):
    filtered = df
    fig = px.line(
        filtered,
        x='date',
        y='value',
        color='commodity',
        title=f'\U0001F33E Global Production Trends (2000–2025)',
        markers=True,
        template='plotly_white'
    )
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Production Value',
        legend_title='Commodity',
        height=600
    )
    fig.show()

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
    growth_df = pd.DataFrame(growth_data).sort_values('CAGR (%)', ascending=False)

    fig = px.bar(
        growth_df,
        x='Commodity',
        y='CAGR (%)',
        color='CAGR (%)',
        color_continuous_scale='Viridis',
        title='\U0001F4C8 CAGR by Commodity',
        template='plotly_white'
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)
    fig.show()

    return growth_df

def analyse_yearly_variation(df):
    seasonal_df = df

    if seasonal_df['commodity'].nunique() > 1:
        fig = px.box(
            seasonal_df,
            x='commodity',
            y='value',
            color='commodity',
            title='\U0001F4E6 Yearly Production Distribution by Commodity',
            template='plotly_white'
        )
        fig.update_layout(
            xaxis_title='Commodity',
            yaxis_title='Production Value',
            boxmode='group',
            showlegend=False
        )
        fig.show()
    else:
        print("Insufficient data for production variation analysis.")

def save_aggregated_data(df, output_dir=eda_path):
    os.makedirs(output_dir, exist_ok=True)
    production_df = df

    trend_data = production_df.pivot(index='date', columns='commodity', values='value')
    trend_data.to_csv(f'{output_dir}/production_trends.csv')

    stats_df = production_df.groupby('commodity')['value'].agg(['mean', 'median', 'std', 'min', 'max', 'count'])
    stats_df.to_csv(f'{output_dir}/production_stats.csv')

    production_df.sort_values(['commodity', 'date'], inplace=True)
    production_df['yoy_change'] = production_df.groupby('commodity')['value'].pct_change() * 100
    production_df.to_csv(f"{output_dir}/production_yoy_change.csv", index=False)

    growth_df_out = analyse_growth_rates(df)
    growth_df_out.to_csv(f"{output_dir}/growth_rates.csv", index=False)

    pivot_df = production_df.pivot(index='date', columns='commodity', values='value')
    corr_matrix_out = pivot_df.corr()
    corr_matrix_out.to_csv(f"{output_dir}/correlation_matrix.csv")

    # Key Insights: Top Commodity, Highest Growth Rate, Average Growth Rate, Most Recent Year
    key_insights = {}
    if not growth_df_out.empty:
        top = growth_df_out.iloc[0]
        key_insights["highest_growth"] = top['Commodity']
        key_insights["highest_growth_rate"] = round(top['CAGR (%)'], 2)
        key_insights["average_growth"] = round(growth_df_out['CAGR (%)'].mean(), 2)
    key_insights["most_recent_year"] = int(df['date'].max().year)

    with open(f"{output_dir}/key_insights.json", "w") as f:
        json.dump(key_insights, f, indent=2)

    return stats_df, growth_df_out, corr_matrix_out, key_insights

# Gemini Insight
def generate_insights(stats_df, growth_df_out, corr_matrix_out, key_insights, output_dir):
    try:
        prompt = f""" Respond concisely with minimal words and no formatting. Avoid repetition or filler.

You are a strategic economic intelligence analyst.

The following agriculture production data includes:
- Summary statistics (mean, median, volatility)
- Growth rates (CAGR)
- Inter-commodity correlations
- Key metadata

Your task:
1. Identify 3–5 *second-order insights*. These are not just about what the data says, but what the implications might be.
2. Highlight any surprising correlations and propose plausible macroeconomic or geopolitical explanations.
3. Suggest how these trends might evolve given current global contexts such as climate shifts, trade policy, fertilizer prices, and food security concerns.

Data:
Summary Statistics:
{stats_df.to_markdown(index=False)}

CAGR (% Growth):
{growth_df_out.to_markdown(index=False)}

Correlation Matrix:
{corr_matrix_out.to_string(index=False)}

Key Metrics:
{json.dumps(key_insights, indent=2)}

Avoid restating exact numbers. Focus on relationships, causes, risks, and opportunities.
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

    production_df = df
    print("\n=== Summary Stats ===")
    print(production_df.groupby('commodity')['value'].describe().round(2))

    plot_production_trends(df)
    analyse_yearly_variation(df)
    stats_df, growth_df_out, corr_matrix_out, key_insights = save_aggregated_data(df)

    print("\n=== Correlation Matrix ===")
    print(corr_matrix_out.round(2))

    fig = px.imshow(
        corr_matrix_out,
        text_auto=True,
        color_continuous_scale='RdBu',
        title='\U0001F517 Commodity Correlation Matrix',
        template='plotly_white'
    )
    fig.update_layout(height=600)
    fig.show()

    generate_insights(stats_df, growth_df_out, corr_matrix_out, key_insights, eda_path)

if __name__ == "__main__":
    main()
