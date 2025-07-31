import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime   
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_energy_data

# Page Config
st.set_page_config(
    page_title="Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    .section-header {
        background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .alert-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Title with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>⚡ Energy Dashboard</h1>
    <p>Comprehensive analysis of global energy stocks, oil imports, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_energy_data():
    try:
        data = load_energy_data()
        return data
    except Exception as e:
        st.error(f"Error loading energy data: {str(e)}")
        return {}

# Helper Functions
def format_dates_for_display(df):
    if not df.empty and 'date' in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def create_metric_card(title, value, subtitle="", color="#007bff"):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """

def apply_chart_styling(fig, title_color="#1e3c72"):
    fig.update_layout(
        title_font_size=18,
        title_font_color=title_color,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
        height=400
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    return fig

def extract_section(text, start, end=None):
    if start not in text:
        return ""
    section = text.split(start)[1]
    if end and end in section:
        section = section.split(end)[0]
    return section.strip()

def format_insight_text(text):
    if not text:
        return ""
    lines = text.strip().split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("•"):
            clean_line = line[1:].strip()
            if clean_line and clean_line[0].isdigit() and len(clean_line) > 1 and clean_line[1] == '.':
                formatted.append(clean_line)
            elif ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted.append(f"**{label}:** {content}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and ':' in line:
            formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            formatted.append(f"\n**{line}**")
        elif line and line[0].isdigit() and len(line) > 1 and line[1] == '.':
            formatted.append(line)
        elif line and not line.startswith("-"):
            formatted.append(f"• {line}")
        else:
            formatted.append(line)
    return "\n\n".join(formatted)

def format_opec_text(text):
    """Format OPEC analysis text with numbered points and emojis in styled containers"""
    if not text or text == "No OPEC insights found.":
        return ""
    
    # Split into lines and add proper spacing
    lines = text.strip().split('\n')
    formatted_lines = []
    point_counter = 1
    
    # Define emojis for different types of content
    emoji_map = {
        'oil': '🛢️', 'petroleum': '🛢️', 'crude': '🛢️', 'barrel': '🛢️',
        'production': '⚙️', 'output': '⚙️', 'supply': '📦', 'demand': '📈',
        'price': '💰', 'cost': '💰', 'revenue': '💰', 'profit': '💰',
        'market': '📊', 'trade': '🔄', 'export': '📤', 'import': '📥',
        'opec': '🛢️', 'saudi': '🇸🇦', 'arabia': '🇸🇦', 'iran': '🇮🇷',
        'iraq': '🇮🇶', 'kuwait': '🇰🇼', 'uae': '🇦🇪', 'venezuela': '🇻🇪',
        'nigeria': '🇳🇬', 'angola': '🇦🇴', 'algeria': '🇩🇿', 'libya': '🇱🇾',
        'russia': '🇷🇺', 'china': '🇨🇳', 'india': '🇮🇳', 'us': '🇺🇸',
        'europe': '🇪🇺', 'asia': '🌏', 'africa': '🌍', 'america': '🌎',
        'increase': '📈', 'growth': '📈', 'rise': '📈', 'higher': '📈',
        'decrease': '📉', 'decline': '📉', 'lower': '📉', 'drop': '📉',
        'report': '📊', 'analysis': '📊', 'data': '📊', 'statistics': '📊',
        'recommend': '💡', 'suggest': '💡', 'propose': '💡', 'advise': '💡',
        'risk': '⚠️', 'danger': '⚠️', 'threat': '⚠️', 'warning': '⚠️',
        'cooperation': '🤝', 'international': '🌍', 'global': '🌍', 'world': '🌍',
        'energy': '⚡', 'fuel': '⛽', 'gasoline': '⛽', 'diesel': '⛽',
        'refinery': '🏭', 'pipeline': '🛢️', 'tanker': '🚢', 'shipping': '🚢'
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove existing bullet points
        if line.startswith('•'):
            line = line[1:].strip()
        elif line.startswith('-'):
            line = line[1:].strip()
        
        if line:
            # Determine appropriate emoji based on content
            line_lower = line.lower()
            selected_emoji = '📋'  # Default emoji
            
            for keyword, emoji in emoji_map.items():
                if keyword in line_lower:
                    selected_emoji = emoji
                    break
            
            # Create styled container for each point
            container_html = f"""
            <div style="
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px 16px;
                margin: 8px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            ">
                <div style="
                    display: flex;
                    align-items: flex-start;
                    gap: 8px;
                ">
                    <span style="
                        background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 0.8rem;
                        font-weight: bold;
                        min-width: 60px;
                        text-align: center;
                    ">Point {point_counter}</span>
                    <span style="font-size: 1.2rem; margin-right: 8px;">{selected_emoji}</span>
                    <span style="flex-grow: 1; line-height: 1.5;">{line}</span>
                </div>
            </div>
            """
            formatted_lines.append(container_html)
            point_counter += 1
    
    return "\n".join(formatted_lines)

# Load Data
with st.spinner("Loading energy intelligence data..."):
    data = load_cached_energy_data()

# Extract data
iea_stocks_raw = format_dates_for_display(data.get("iea_stocks_raw", pd.DataFrame()))
oil_imports_raw = format_dates_for_display(data.get("oil_imports_raw", pd.DataFrame()))
opec_summary_raw = data.get("opec_summary_raw", pd.DataFrame())
stock_country_ranking = data.get("stock_country_ranking", pd.DataFrame())
stock_volatility_analysis = data.get("stock_volatility_analysis", pd.DataFrame())
stock_seasonality_patterns = data.get("stock_seasonality_patterns", pd.DataFrame())
stock_stockpile_statistics = data.get("stock_stockpile_statistics", pd.DataFrame())
import_regional_share_trends = data.get("import_regional_share_trends", pd.DataFrame())
import_volume_by_region = data.get("import_volume_by_region", pd.DataFrame())
import_value_by_region = data.get("import_value_by_region", pd.DataFrame())
import_price_by_region = data.get("import_price_by_region", pd.DataFrame())
import_dominant_supplier_trend = data.get("import_dominant_supplier_trend", pd.DataFrame())
import_metric_breakdown = data.get("import_metric_breakdown", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter (for IEA stocks)
if not iea_stocks_raw.empty and 'date' in iea_stocks_raw.columns:
    try:
        min_date = pd.to_datetime(iea_stocks_raw['date']).min()
        max_date = pd.to_datetime(iea_stocks_raw['date']).max()
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            iea_stocks_raw = iea_stocks_raw[(pd.to_datetime(iea_stocks_raw['date']).dt.date >= start_date) & (pd.to_datetime(iea_stocks_raw['date']).dt.date <= end_date)]
            stock_country_ranking = stock_country_ranking[(pd.to_datetime(stock_country_ranking['date']).dt.date >= start_date) & (pd.to_datetime(stock_country_ranking['date']).dt.date <= end_date)] if 'date' in stock_country_ranking.columns else stock_country_ranking
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Country filter for IEA stocks
if not iea_stocks_raw.empty and 'country' in iea_stocks_raw.columns:
    st.sidebar.markdown("### 🌍 Country Filter")
    all_countries = list(iea_stocks_raw['country'].unique())
    select_all_label = "Select All"
    multiselect_options = [select_all_label] + all_countries
    selected = st.sidebar.multiselect(
        "Select countries:",
        options=multiselect_options,
        default=[select_all_label],  # Only 'Select All' is selected by default
        key="country_multiselect"
    )
    if select_all_label in selected:
        selected_countries = all_countries
    else:
        selected_countries = [c for c in selected if c in all_countries]
    if selected_countries:
        iea_stocks_raw = iea_stocks_raw[iea_stocks_raw['country'].isin(selected_countries)]
        stock_country_ranking = stock_country_ranking[stock_country_ranking['country'].isin(selected_countries)] if 'country' in stock_country_ranking.columns else stock_country_ranking

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if 'selected_countries' in locals() and selected_countries:
    if len(selected_countries) == len(all_countries):
        active_filters.append(f"Countries: All ({len(selected_countries)})")
    else:
        active_filters.append(f"Countries: {len(selected_countries)} selected")
if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Energy Metrics</h2></div>', unsafe_allow_html=True)

# Dynamically calculate metrics from key insights
if key_insights and "summary_statistics" in key_insights:
    stats = key_insights["summary_statistics"]
    total_stock = stats.get("total_iea_stocks_latest_value", "N/A")
    top_import_region = stats.get("top_import_region_volume", "N/A")
    top_import_volume = stats.get("top_import_volume_value", "N/A")
    avg_import_price = stats.get("avg_import_price_latest", "N/A")
else:
    total_stock = top_import_region = top_import_volume = avg_import_price = "N/A"
# Get top import region share
if key_insights and "import_analysis" in key_insights:
    dependency_risk = key_insights["import_analysis"].get("dependency_risk", {})
    top_import_region_share = dependency_risk.get("max_dependency", None)
else:
    top_import_region_share = None
# Get last update date (latest date from IEA stocks or oil imports)
def get_latest_update_date():
    dates = []
    if not iea_stocks_raw.empty and 'date' in iea_stocks_raw.columns:
        dates.append(pd.to_datetime(iea_stocks_raw['date']).max())
    if not oil_imports_raw.empty and 'date' in oil_imports_raw.columns:
        dates.append(pd.to_datetime(oil_imports_raw['date']).max())
    if dates:
        return max(dates).strftime('%Y-%m-%d')
    return "N/A"
last_update = get_latest_update_date()

# Expand metrics row to 6 columns
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(create_metric_card(
        "🌍 Top Import Region",
        top_import_region,
        f"Volume: {top_import_volume:,.0f}" if isinstance(top_import_volume, (int, float)) else "",
        "#007bff"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "🏆 Top Import Region Share",
        f"{top_import_region_share:.1f}%" if isinstance(top_import_region_share, (int, float)) else str(top_import_region_share),
        "Share of total imports",
        "#20c997"
    ), unsafe_allow_html=True)
        
with col3:
    st.markdown(create_metric_card(
        "💰 Top Import Volume",
        f"{top_import_volume:,.0f}" if isinstance(top_import_volume, (int, float)) else str(top_import_volume),
        "Latest",
        "#ffc107"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card(
        "💵 Avg Import Price",
        f"{avg_import_price:,.2f}" if isinstance(avg_import_price, (int, float)) else str(avg_import_price),
        "Latest USD/bbl",
        "#6f42c1"
    ), unsafe_allow_html=True)
with col5:
    st.markdown(create_metric_card(
        "🛢️ Total IEA Stocks",
        f"{total_stock:,.0f}" if isinstance(total_stock, (int, float)) else str(total_stock),
        "Latest value",
        "#28a745"
    ), unsafe_allow_html=True)
with col6:
    st.markdown(create_metric_card(
        "⏰ Last Update",
        last_update,
        "Latest data date",
        "#fd7e14"
    ), unsafe_allow_html=True)


# After Import Price Trends, add Dominant Supplier Trend
st.markdown('<div class="section-header"><h2>🏅 Dominant Supplier Trend</h2></div>', unsafe_allow_html=True)
if not import_dominant_supplier_trend.empty:
    # Create two columns for the charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dom = px.line(
            import_dominant_supplier_trend,
            x="date", y="dominant_region_share", color="dominant_region_name",
            title="Dominant Supplier Share (Last 12 Months)",
            labels={"dominant_region_share": "Share (%)", "date": "Date"}
        )
        fig_dom = apply_chart_styling(fig_dom)
        st.plotly_chart(fig_dom, use_container_width=True)
    
    with col2:
        # Create pie chart for latest regional shares
        if not import_regional_share_trends.empty:
            # Get the latest date
            latest_date = import_regional_share_trends['date'].max()
            latest_shares = import_regional_share_trends[import_regional_share_trends['date'] == latest_date]
            
            if not latest_shares.empty:
                fig_pie = px.pie(
                    latest_shares,
                    values='value',
                    names='region',
                    title=f"Regional Share Distribution ({pd.to_datetime(latest_date).strftime('%Y-%m-%d')})",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(
                    title_font_size=16,
                    title_font_color="#1e3c72",
                    height=400,
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No latest share data available for pie chart.")
        else:
            st.info("No regional share data available for pie chart.")
else:
    st.info("No dominant supplier trend data available.")
    
# Oil Import Analysis
st.markdown('<div class="section-header"><h2>🚢 Oil Import Analysis</h2></div>', unsafe_allow_html=True)
if not import_volume_by_region.empty:
    fig_imports = px.line(
        import_volume_by_region,
        x="date",
        y="value",
        color="region",
        title="Oil Import Volume by Region",
        labels={"value": "Volume (thousand bbl)", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    fig_imports = apply_chart_styling(fig_imports)
    st.plotly_chart(fig_imports, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Oil Import Data Available</h4>
        <p>No oil import data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# After Oil Import Analysis, add Import Value and Price Trends
st.markdown('<div class="section-header"><h2>💰 Import Value Trends</h2></div>', unsafe_allow_html=True)
if not import_value_by_region.empty:
    fig_value = px.line(
        import_value_by_region,
        x="date", y="value", color="region",
        title="Oil Import Value by Region",
        labels={"value": "Value (thousand USD)", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_value = apply_chart_styling(fig_value)
    st.plotly_chart(fig_value, use_container_width=True)
else:
    st.info("No import value data available.")
st.markdown('<div class="section-header"><h2>💵 Import Price Trends</h2></div>', unsafe_allow_html=True)
if not import_price_by_region.empty:
    fig_price = px.line(
        import_price_by_region,
        x="date", y="value", color="region",
        title="Oil Import Price by Region",
        labels={"value": "Price (USD/bbl)", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_price = apply_chart_styling(fig_price)
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("No import price data available.")

# IEA Oil Stocks Trends
st.markdown('<div class="section-header"><h2>📈 IEA Oil Stocks Trends</h2></div>', unsafe_allow_html=True)
if not iea_stocks_raw.empty:
    # Filter out regional totals and get top 8 countries
    regional_totals = ['Total IEA', 'Total IEA Asia Pacific', 'Total IEA Europe', 'Total IEA net importers']
    filtered_stocks = iea_stocks_raw[~iea_stocks_raw['country'].isin(regional_totals)]
    
    # Get the latest date to determine top countries
    latest_date = filtered_stocks['date'].max()
    latest_stocks = filtered_stocks[filtered_stocks['date'] == latest_date]
    top_8_countries = latest_stocks.nlargest(8, 'value')['country'].tolist()
    
    # Filter data to only include top 8 countries
    top_8_data = filtered_stocks[filtered_stocks['country'].isin(top_8_countries)]
    
    if not top_8_data.empty:
        fig_stocks = px.line(
            top_8_data,
            x="date",
            y="value",
            color="country",
            title="IEA Oil Stocks by Country (Top 8)",
            labels={"value": "Stock (thousand bbl)", "date": "Date"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white"
        )
        fig_stocks = apply_chart_styling(fig_stocks)
        st.plotly_chart(fig_stocks, use_container_width=True)
    else:
        st.markdown("""
        <div class="alert-box">
            <h4>⚠️ No IEA Oil Stocks Data Available</h4>
            <p>No IEA oil stocks data is currently available after filtering.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No IEA Oil Stocks Data Available</h4>
        <p>No IEA oil stocks data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)


# After Key Metrics section, add Stockpile Statistics Table
st.markdown('<div class="section-header"><h2>🏆 Top 5 IEA Stockpilers</h2></div>', unsafe_allow_html=True)
if not stock_stockpile_statistics.empty:
    st.dataframe(stock_stockpile_statistics.head(5), use_container_width=True)
else:
    st.info("No stockpile statistics available.")

# After IEA Oil Stocks Trends, add Volatility by Country
st.markdown('<div class="section-header"><h2>📉 Volatility by Country</h2></div>', unsafe_allow_html=True)
if not stock_volatility_analysis.empty:
    df_vol = stock_volatility_analysis.sort_values("volatility", ascending=False).head(10).copy()
    df_vol['vol_label'] = df_vol['volatility'].round(1).astype(str)
    fig_vol = px.bar(
        df_vol,
        x="country", y="volatility",
        color="volatility", color_continuous_scale="Blues",
        title="Top 10 Most Volatile IEA Oil Stocks by Country",
        text="vol_label"
    )
    fig_vol.update_traces(textposition='auto', textfont_size=12, textfont_color='black')
    fig_vol = apply_chart_styling(fig_vol)
    st.plotly_chart(fig_vol, use_container_width=True)
else:
    st.info("No volatility analysis data available.")

# After Volatility, add Seasonality Patterns
st.markdown('<div class="section-header"><h2>📅 Seasonality Patterns</h2></div>', unsafe_allow_html=True)
if not stock_seasonality_patterns.empty:
    # 1. Order countries by total average stock (descending)
    country_totals = stock_seasonality_patterns.groupby('country')['monthly_avg_stock'].mean().sort_values(ascending=False)
    top_countries = country_totals.head(15).index.tolist()  # Top 15 countries for better visualization
    
    # Filter data to top countries
    filtered_seasonality = stock_seasonality_patterns[stock_seasonality_patterns['country'].isin(top_countries)]
    
    # 2. Create pivot with ordered countries
    pivot = filtered_seasonality.pivot(index="month", columns="country", values="monthly_avg_stock")
    
    # Reorder columns by total average stock
    pivot = pivot[top_countries]
    
    # 3. Create improved heatmap
    fig_season = px.imshow(
        pivot,
        labels=dict(x="Country", y="Month", color="Avg Stock (thousand bbl)"),
        aspect="auto",
        title="Monthly Average IEA Oil Stocks by Country (Top 15)",
        color_continuous_scale="Blues",  # Use Blues scale for better contrast
        text_auto=True
    )
    
    # 4. Improve axis formatting and styling
    fig_season.update_layout(
        title_font_size=18,
        title_font_color="#1e3c72",
        xaxis_title="Country",
        yaxis_title="Month",
        height=500,
        margin=dict(l=80, r=50, t=100, b=100)
    )
    
    # Rotate x-axis labels and improve spacing
    fig_season.update_xaxes(
        tickangle=-45,
        tickmode='array',
        ticktext=pivot.columns,
        tickvals=list(range(len(pivot.columns))),
        tickfont=dict(size=10),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)'
    )
    
    # Improve y-axis (months)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig_season.update_yaxes(
        tickmode='array',
        ticktext=month_names,
        tickvals=list(range(1, 13)),
        tickfont=dict(size=12),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)'
    )
    
    # Add colorbar improvements
    fig_season.update_coloraxes(
        colorbar=dict(
            title=dict(text="Avg Stock (thousand bbl)"),
            thickness=15,
            len=0.8,
            outlinewidth=1,
            outlinecolor="black"
        )
    )
    
    st.plotly_chart(fig_season, use_container_width=True)
    
    # Add summary statistics
    st.subheader("📊 Seasonality Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Countries Analyzed", len(top_countries))
    
    with col2:
        st.metric("Months Covered", len(pivot.index))
    
    with col3:
        max_stock = pivot.max().max()
        st.metric("Highest Monthly Average", f"{max_stock:,.0f}")
    
else:
    st.info("No seasonality pattern data available.")

# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)
if gemini_insight and gemini_insight != "No AI insights found.":
    sections = {
        "Core Trend": extract_section(gemini_insight, "### Core Trend", "### Hidden Effects"),
        "Hidden Effects": extract_section(gemini_insight, "### Hidden Effects", "### Strategic Recommendations"),
        "Strategic Recommendations": extract_section(gemini_insight, "### Strategic Recommendations", "### Risk Assessment"),
        "Risk Assessment": extract_section(gemini_insight, "### Risk Assessment", "### Market Intelligence"),
        "Market Intelligence": extract_section(gemini_insight, "### Market Intelligence")
    }
    tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
    tabs = st.tabs(tab_labels)
    for tab, (label, content) in zip(tabs, sections.items()):
        with tab:
            if content:
                st.markdown(f"### {label}")
                st.markdown(format_insight_text(content))
            else:
                st.info(f"No {label} insights available.")
    st.subheader("📊 AI Insight Summary")
    insight_metrics = {
        "Sections Available": len([s for s in sections.values() if s]),
        "Total Insight Length": len(gemini_insight),
        "Last Updated": datetime.now().strftime("%Y-%m-%d")
    }
    col1, col2, col3 = st.columns(3)
    for i, (key, value) in enumerate(insight_metrics.items()):
        with [col1, col2, col3][i]:
            st.metric(key, value)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>🌟 AI Insights Unavailable</h4>
        <p>No AI-powered strategic insights are currently available. This could be due to:</p>
        <ul>
            <li>Insufficient data for analysis</li>
            <li>AI service configuration issues</li>
            <li>Data quality concerns</li>
        </ul>
        <p>Please check your data sources and AI service setup.</p>
    </div>
    """, unsafe_allow_html=True)

# OPEC Insights
st.markdown('<div class="section-header"><h2>🛢️ OPEC Monthly Report Insights</h2></div>', unsafe_allow_html=True)

if not opec_summary_raw.empty:
    with st.expander("🔍 View OPEC Analysis", expanded=False):
        # Format and display OPEC insights
        opec_text = "\n".join([f"Topic: {row['topic']} - Insight: {row['insight']}" for _, row in opec_summary_raw.iterrows()])
        formatted_opec = format_opec_text(opec_text)
        st.markdown(formatted_opec, unsafe_allow_html=True)
        
        # OPEC metrics
        st.subheader("📈 OPEC Analysis Metrics")
        opec_metrics = {
            "Total Insights": len(opec_summary_raw),
            "Unique Topics": opec_summary_raw['topic'].nunique() if 'topic' in opec_summary_raw.columns else 0,
            "Analysis Length": len(opec_text),
            "Contains Market Data": "Yes" if any(word in opec_text.lower() for word in ['market', 'price', 'demand', 'supply']) else "No",
            "Last Updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, (key, value) in enumerate(opec_metrics.items()):
            with [col1, col2, col3, col4, col5][i]:
                st.metric(key, value)
else:
    st.info("No OPEC insights available at the moment.")

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)
if not iea_stocks_raw.empty or not oil_imports_raw.empty or not opec_summary_raw.empty or not import_metric_breakdown.empty:
    tab1, tab2, tab3, tab4 = st.tabs(["🛢️ IEA Stocks", "🚢 Oil Imports", "🛢️ OPEC Insights", "📊 Import Metric Breakdown"])
    with tab1:
        if not iea_stocks_raw.empty:
            with st.expander("🛢️ IEA Oil Stocks Data", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_iea"):
                        csv = iea_stocks_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"iea_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                search_term = st.text_input("🔍 Search countries:", placeholder="Enter country name...", key="search_iea")
                if search_term:
                    filtered_data = iea_stocks_raw[
                        iea_stocks_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = iea_stocks_raw
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No IEA stocks data available.")
    with tab2:
        if not oil_imports_raw.empty:
            with st.expander("🚢 Oil Imports Data", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_imports"):
                        csv = oil_imports_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"oil_imports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                search_term = st.text_input("🔍 Search regions/countries:", placeholder="Enter region or country...", key="search_imports")
                if search_term:
                    filtered_data = oil_imports_raw[
                        oil_imports_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = oil_imports_raw
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No oil imports data available.")
    with tab3:
        if not opec_summary_raw.empty:
            with st.expander("🛢️ OPEC Insights Data", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_opec"):
                        csv = opec_summary_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"opec_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                search_term = st.text_input("🔍 Search topics/insights:", placeholder="Enter topic or keyword...", key="search_opec")
                if search_term:
                    filtered_data = opec_summary_raw[
                        opec_summary_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = opec_summary_raw
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No OPEC insights data available.")
    with tab4:
        if not import_metric_breakdown.empty:
            with st.expander("📊 Import Metric Breakdown Data", expanded=False):
                # Display the breakdown as a summary table with clear labels
                st.markdown("#### Import Metric Breakdown Summary")
                # If the CSV has no row labels, just show as a table with a note
                st.dataframe(import_metric_breakdown, use_container_width=True)
                st.caption("Summary statistics for key import metrics. Row order corresponds to different metrics (see documentation for mapping if available). Columns: count, mean, std, min, 25%, 50%, 75%, max.")
        else:
            st.info("No import metric breakdown data available.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Data Available</h4>
        <p>No energy data is currently available for exploration.</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>⚡ Energy Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> IEA, OPEC | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive energy analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
