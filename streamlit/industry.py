import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Page config
st.set_page_config(
    page_title="Korean Manufacturing & Steel Trade Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        manufacturing_df = pd.read_csv('manufacture_inventory_processed.csv')
        manufacturing_df['date'] = pd.to_datetime(manufacturing_df['date'])
        
        steel_df = pd.read_csv('steel_combined_processed.csv')
        steel_df['date'] = pd.to_datetime(steel_df['date'])
        
        return manufacturing_df, steel_df
    except FileNotFoundError:
        st.error("Data files not found. Please ensure CSV files are in the same directory.")
        return None, None

def calculate_metrics(df):
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date]
    
    try:
        investment_latest = latest_data[latest_data['category'] == '설비투자지수']['value'].iloc[0]
        inventory_latest = latest_data[latest_data['category'] == '제조업 재고율']['value'].iloc[0]
    except IndexError:
        return None

    year_ago = latest_date - relativedelta(years=1)
    year_ago = year_ago.replace(day=1)
    year_ago_data = df[df['date'].dt.to_period("M") == year_ago.to_period("M")]

    try:
        investment_yoy = year_ago_data[year_ago_data['category'] == '설비투자지수']['value'].iloc[0]
        inventory_yoy = year_ago_data[year_ago_data['category'] == '제조업 재고율']['value'].iloc[0]
        investment_change = ((investment_latest - investment_yoy) / investment_yoy) * 100
        inventory_change = ((inventory_latest - inventory_yoy) / inventory_yoy) * 100
    except IndexError:
        investment_change = 0
        inventory_change = 0

    return {
        'investment_latest': investment_latest,
        'inventory_latest': inventory_latest,
        'investment_change': investment_change,
        'inventory_change': inventory_change,
        'latest_date': latest_date
    }

def create_time_series_chart(df):
    pivot_df = df.pivot(index='date', columns='category', values='value').reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=pivot_df['date'],
            y=pivot_df['설비투자지수'],
            name='Capital Investment Index',
            line=dict(color='#1f77b4', width=3)
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=pivot_df['date'],
            y=pivot_df['제조업 재고율'],
            name='Manufacturing Inventory Rate',
            line=dict(color='#ff7f0e', width=3)
        ),
        secondary_y=True,
    )

    fig.add_shape(type="line", x0="2020-03-01", x1="2020-03-01", y0=0, y1=1, yref="paper", line=dict(color="red", width=2, dash="dash"))
    fig.add_shape(type="line", x0="2021-01-01", x1="2021-01-01", y0=0, y1=1, yref="paper", line=dict(color="green", width=2, dash="dash"))

    fig.add_annotation(x="2020-03-01", y=0.95, yref="paper", text="COVID-19 Impact", showarrow=False, font=dict(size=10), bgcolor="white")
    fig.add_annotation(x="2021-01-01", y=0.85, yref="paper", text="Recovery Period", showarrow=False, font=dict(size=10), bgcolor="white")

    fig.update_layout(
        title="Korean Manufacturing Indicators Over Time",
        xaxis_title="Date",
        yaxis_title="Capital Investment Index",
        hovermode='x unified',
        height=500
    )
    fig.update_yaxes(title_text="Capital Investment Index", secondary_y=False)
    fig.update_yaxes(title_text="Inventory Rate (%)", secondary_y=True)
    return fig

def create_correlation_analysis(df):
    pivot_df = df.pivot(index='date', columns='category', values='value')
    if '설비투자지수' not in pivot_df or '제조업 재고율' not in pivot_df:
        return None, None
    correlation = pivot_df.corr().loc['설비투자지수', '제조업 재고율']
    fig = px.scatter(
        x=pivot_df['설비투자지수'],
        y=pivot_df['제조업 재고율'],
        trendline="ols",
        labels={'x': 'Capital Investment Index', 'y': 'Inventory Rate (%)'},
        title=f"Correlation: {correlation:.3f}",
        height=400
    )
    return fig, correlation

def create_monthly_analysis(df):
    df['month'] = df['date'].dt.month
    monthly_avg = df.groupby(['month', 'category'])['value'].mean().reset_index()
    fig = px.line(
        monthly_avg,
        x='month',
        y='value',
        color='category',
        title="Seasonal Patterns - Monthly Averages",
        labels={'month': 'Month', 'value': 'Average Value'}
    )
    fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
    return fig

def create_steel_comparison_chart(steel_df):
    latest_steel = steel_df[steel_df['indicator'].str.contains('Jan–May')]
    key_regions = ['South Korea', 'China', 'Japan', 'United States', 'Germany', 'World']
    filtered_steel = latest_steel[latest_steel['region'].isin(key_regions)]
    fig = px.bar(
        filtered_steel,
        x='region',
        y='value',
        title="Steel Trade Performance: Jan-May 2025 YoY (%)",
        color='value',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0
    )
    return fig

def main():
    st.markdown('<h1 class="main-header">🏭 Korean Manufacturing & Steel Trade Dashboard</h1>', unsafe_allow_html=True)
    manufacturing_df, steel_df = load_data()
    if manufacturing_df is None or steel_df is None:
        st.stop()

    st.sidebar.header("📊 Dashboard Controls")
    min_date, max_date = manufacturing_df['date'].min(), manufacturing_df['date'].max()
    date_range = st.sidebar.date_input("Select Date Range", (min_date, max_date), min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        filtered_df = manufacturing_df[
            (manufacturing_df['date'] >= pd.to_datetime(date_range[0])) &
            (manufacturing_df['date'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        filtered_df = manufacturing_df

    metrics = calculate_metrics(filtered_df)
    if metrics is None:
        st.warning("Not enough data to calculate KPIs.")
        return

    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Latest Investment Index", f"{metrics['investment_latest']:.1f}", f"{metrics['investment_change']:+.1f}% YoY")
    with col2:
        st.metric("Latest Inventory Rate", f"{metrics['inventory_latest']:.1f}%", f"{metrics['inventory_change']:+.1f}% YoY")
    with col3:
        avg_investment = filtered_df[filtered_df['category'] == '설비투자지수']['value'].mean()
        st.metric("Avg Investment Index", f"{avg_investment:.1f}")
    with col4:
        avg_inventory = filtered_df[filtered_df['category'] == '제조업 재고율']['value'].mean()
        st.metric("Avg Inventory Rate", f"{avg_inventory:.1f}%")

    st.subheader("📊 Time Series Analysis")
    st.plotly_chart(create_time_series_chart(filtered_df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔗 Correlation Analysis")
        corr_fig, correlation = create_correlation_analysis(filtered_df)
        if corr_fig:
            st.plotly_chart(corr_fig, use_container_width=True)
            strength = "strong" if abs(correlation) > 0.5 else "moderate" if abs(correlation) > 0.3 else "weak"
            st.markdown(f"""
            <div class="insight-box">
            <b>Correlation Insight:</b> There is a {strength} 
            {'negative' if correlation < 0 else 'positive'} correlation 
            ({correlation:.3f}) between investment and inventory levels.
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.subheader("📅 Seasonal Patterns")
        st.plotly_chart(create_monthly_analysis(filtered_df), use_container_width=True)

    if not steel_df.empty:
        st.subheader("🌍 Global Steel Trade Context")
        st.plotly_chart(create_steel_comparison_chart(steel_df), use_container_width=True)

        sk_row = steel_df[(steel_df['region'] == 'South Korea') & (steel_df['indicator'].str.contains('Jan–May'))]
        world_row = steel_df[(steel_df['region'] == 'World') & (steel_df['indicator'].str.contains('Jan–May'))]

        if not sk_row.empty and not world_row.empty:
            sk_val = sk_row['value'].iloc[0]
            world_val = world_row['value'].iloc[0]
            out_perf = "outperformed" if sk_val > world_val else "underperformed"
            st.markdown(f"""
            <div class="insight-box">
            <b>Steel Trade Insight:</b> South Korea's steel trade changed by {sk_val:.1f}% in Jan–May 2025, compared to {world_val:.1f}% globally.  
            South Korea {out_perf} the global trend.
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📋 Data Summary"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Manufacturing Data**")
            st.write(f"- Range: {min_date.date()} to {max_date.date()}")
            st.write(f"- Records: {len(manufacturing_df):,}")
        with col2:
            st.write("**Steel Trade Data**")
            st.write(f"- Regions: {steel_df['region'].nunique()}")
            st.write(f"- Latest: Jan–May 2025")

if __name__ == "__main__":
    main()
