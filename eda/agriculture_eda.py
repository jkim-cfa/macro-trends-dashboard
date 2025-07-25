import os
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
import numpy as np

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

EDA_DIR = os.getenv("EDA_DIR")
eda_path=os.path.join(EDA_DIR,"outputs","agriculture")

PG_USER = os.getenv("POSTGRES_USER", "postgres")    
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "macro2025")
PG_DB = os.getenv("POSTGRES_DB", "macrodb")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Load agriculture data
def load_agriculture_data(engine):
    query = """
    SELECT *
    FROM agriculture_crop_production_processed
    ORDER BY indicator, date
    """
    return pd.read_sql(query, engine)

def plot_production_trends(df, indicator='Production'):
    filtered = df[df['indicator'] == indicator]
    fig = px.line(
        filtered,
        x='date',
        y='value',
        color='commodity',
        title=f'🌾 Global {indicator} Trends (2000–2025)',
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

def analyze_growth_rates(df, indicator='Production'):
    growth_data = []
    for commodity in df[df['indicator'] == indicator]['commodity'].unique():
        subset = df[(df['commodity'] == commodity) & (df['indicator'] == indicator)].sort_values('date')
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
        title='📈 CAGR by Commodity',
        template='plotly_white'
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)
    fig.show()

    return growth_df

def analyze_seasonality(df, indicator='Production'):
    df['month'] = df['date'].dt.month
    seasonal_df = df[df['indicator'] == indicator]
    if seasonal_df['commodity'].nunique() > 1:
        fig = px.box(
            seasonal_df,
            x='month',
            y='value',
            color='commodity',
            title='📦 Monthly Production Distribution by Commodity',
            template='plotly_white'
        )
        fig.update_layout(xaxis_title='Month', yaxis_title='Production Value', boxmode='group')
        fig.show()
    else:
        print("Insufficient data for seasonal analysis.")

def save_aggregated_data(df, output_dir=eda_path):

    os.makedirs(output_dir, exist_ok=True)
    production_df = df[df['indicator'] == 'Production'].copy()

    # 📊 Pivoted time-series data
    trend_data = production_df.pivot(index='date', columns='commodity', values='value')
    trend_data.to_csv(f'{output_dir}/production_trends.csv')

    # 📈 Summary stats
    stats = production_df.groupby('commodity')['value'].agg(['mean', 'median', 'std', 'min', 'max', 'count'])
    stats.to_csv(f'{output_dir}/production_stats.csv')

    # 📉 YoY % change per commodity
    production_df.sort_values(['commodity', 'date'], inplace=True)
    production_df['yoy_change'] = production_df.groupby('commodity')['value'].pct_change() * 100
    production_df.to_csv(f"{output_dir}/production_yoy_change.csv", index=False)

    # 📈 CAGR growth rates (recomputed for saving)
    growth_data = []
    for commodity in production_df['commodity'].unique():
        subset = production_df[production_df['commodity'] == commodity]
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
    growth_df.to_csv(f"{output_dir}/growth_rates.csv", index=False)

    # 🔗 Correlation matrix
    pivot_df = production_df.pivot(index='date', columns='commodity', values='value')
    corr_matrix = pivot_df.corr()
    corr_matrix.to_csv(f"{output_dir}/correlation_matrix.csv")

    # 💡 Key insights
    key_insights = {}
    if not growth_df.empty:
        top = growth_df.iloc[0]
        key_insights["highest_growth"] = top['Commodity']
        key_insights["highest_growth_rate"] = round(top['CAGR (%)'], 2)
        key_insights["average_growth"] = round(growth_df['CAGR (%)'].mean(), 2)
    key_insights["most_recent_year"] = int(df['date'].max().year)

    import json
    with open(f"{output_dir}/key_insights.json", "w") as f:
        json.dump(key_insights, f, indent=2)

    print(f"✅ All EDA outputs saved to: {output_dir}")

def main():
    df = load_agriculture_data(engine)
    df['date'] = pd.to_datetime(df['date'])

    print("\n=== Data Overview ===")
    print(f"Time Range: {df['date'].min().year} to {df['date'].max().year}")
    print(f"Commodities: {df['commodity'].nunique()}")
    print(f"Indicators: {df['indicator'].unique()}")

    production_df = df[df['indicator'] == 'Production']
    print("\n=== Summary Stats ===")
    print(production_df.groupby('commodity')['value'].describe().round(2))

    # Run EDA
    plot_production_trends(df)
    growth_df = analyze_growth_rates(df)
    analyze_seasonality(df)
    save_aggregated_data(df)

    # Correlation matrix
    print("\n=== Correlation Matrix ===")
    pivot_df = production_df.pivot(index='date', columns='commodity', values='value')
    corr_matrix = pivot_df.corr()
    print(corr_matrix.round(2))

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu',
        title='🔗 Commodity Correlation Matrix',
        template='plotly_white'
    )
    fig.update_layout(height=600)
    fig.show()

if __name__ == "__main__":
    main()
