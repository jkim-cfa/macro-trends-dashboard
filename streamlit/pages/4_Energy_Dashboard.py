import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from functools import lru_cache
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
        default=multiselect_options,
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

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_metric_card(
        "🛢️ Total IEA Stocks",
        f"{total_stock:,.0f}" if isinstance(total_stock, (int, float)) else str(total_stock),
        "Latest value",
        "#28a745"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "🌍 Top Import Region",
        top_import_region,
        f"Volume: {top_import_volume:,.0f}" if isinstance(top_import_volume, (int, float)) else "",
        "#007bff"
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

# IEA Oil Stocks Trends
st.markdown('<div class="section-header"><h2>📈 IEA Oil Stocks Trends</h2></div>', unsafe_allow_html=True)
if not iea_stocks_raw.empty:
    fig_stocks = px.line(
        iea_stocks_raw,
        x="date",
        y="value",
        color="country",
        title="IEA Oil Stocks by Country",
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
        <p>No IEA oil stocks data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

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

# OPEC Insights
st.markdown('<div class="section-header"><h2>🛢️ OPEC Insights</h2></div>', unsafe_allow_html=True)
if not opec_summary_raw.empty:
    st.dataframe(opec_summary_raw, use_container_width=True)
else:
    st.info("No OPEC insights available.")

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

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)
if not iea_stocks_raw.empty or not oil_imports_raw.empty or not opec_summary_raw.empty:
    tab1, tab2, tab3 = st.tabs(["🛢️ IEA Stocks", "🚢 Oil Imports", "🛢️ OPEC Insights"])
    with tab1:
        if not iea_stocks_raw.empty:
            with st.expander("🛢️ IEA Oil Stocks Data", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export IEA Stocks", type="primary", key="export_iea"):
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
                    if st.button("📥 Export Oil Imports", type="primary", key="export_imports"):
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
                    if st.button("📥 Export OPEC Insights", type="primary", key="export_opec"):
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