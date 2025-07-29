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
from utils.data_loader import load_global_trade_data

# Page Config
st.set_page_config(
    page_title="Global Trade Dashboard",
    page_icon="🌏",
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
    <h1>🌏 Global Trade Dashboard</h1>
    <p>Comprehensive analysis of global trade flows, shipping indices, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_global_trade_data():
    try:
        data = load_global_trade_data()
        return data
    except Exception as e:
        st.error(f"Error loading global trade data: {str(e)}")
        return {}

# Helper Functions
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
with st.spinner("Loading global trade intelligence data..."):
    data = load_cached_global_trade_data()

# Extract data
export_decrease_items_top5 = data.get("export_decrease_items_top5", pd.DataFrame())
export_increase_items_top5 = data.get("export_increase_items_top5", pd.DataFrame())
export_increase_countries_top5 = data.get("export_increase_countries_top5", pd.DataFrame())
trade_partners_top5 = data.get("trade_partners_top5", pd.DataFrame())
shipping_index_pivoted = data.get("shipping_index_pivoted", pd.DataFrame())
shipping_index_correlation = data.get("shipping_index_correlation", pd.DataFrame())
shipping_index_3m_volatility = data.get("shipping_index_3m_volatility", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter for shipping index
if not shipping_index_pivoted.empty and 'date' in shipping_index_pivoted.index:
    shipping_index_pivoted = shipping_index_pivoted.reset_index()
if not shipping_index_pivoted.empty and 'date' in shipping_index_pivoted.columns:
    try:
        min_date = pd.to_datetime(shipping_index_pivoted['date']).min()
        max_date = pd.to_datetime(shipping_index_pivoted['date']).max()
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            shipping_index_pivoted = shipping_index_pivoted[(pd.to_datetime(shipping_index_pivoted['date']).dt.date >= start_date) & (pd.to_datetime(shipping_index_pivoted['date']).dt.date <= end_date)]
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Trade Metrics</h2></div>', unsafe_allow_html=True)
if key_insights and "summary_statistics" in key_insights:
    stats = key_insights["summary_statistics"]
    top5_decrease = stats.get("Top 5 YoY Decrease Items", [])
    top5_increase = stats.get("Top 5 YoY Increase Items", [])
    top5_countries = stats.get("Top 5 Export Increase Countries", [])
    top5_partners = stats.get("Top Trade Partners by Export Value", [])
else:
    top5_decrease = top5_increase = top5_countries = top5_partners = []
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_metric_card(
        "⬇️ Top Decrease Item",
        top5_decrease[0]["commodity_full_name"] if top5_decrease else "N/A",
        f"YoY: {top5_decrease[0]['yoy_change_percent']:.1f}%" if top5_decrease else "",
        "#dc3545"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "⬆️ Top Increase Item",
        top5_increase[0]["commodity_full_name"] if top5_increase else "N/A",
        f"YoY: {top5_increase[0]['yoy_change_percent']:.1f}%" if top5_increase else "",
        "#28a745"
    ), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card(
        "🌍 Top Increase Country",
        f"{top5_countries[0]['country']} → {top5_countries[0]['partner']}" if top5_countries else "N/A",
        f"YoY: {top5_countries[0]['yoy_change_percent']:.1f}%" if top5_countries else "",
        "#007bff"
    ), unsafe_allow_html=True)
with col4:
    st.markdown(create_metric_card(
        "🤝 Top Trade Partner",
        f"{top5_partners[0]['country']} → {top5_partners[0]['partner']}" if top5_partners else "N/A",
        f"Export: {top5_partners[0]['export_value_thousand_usd']:,}" if top5_partners else "",
        "#ffc107"
    ), unsafe_allow_html=True)

# Shipping Index Trends
st.markdown('<div class="section-header"><h2>🚢 Shipping Index Trends</h2></div>', unsafe_allow_html=True)
if not shipping_index_pivoted.empty:
    indicators = [col for col in shipping_index_pivoted.columns if col != "date"]
    selected_indicators = st.multiselect(
        "Select shipping indices:",
        options=["All Indices"] + indicators,
        default=["All Indices"]
    )
    if selected_indicators:
        if "All Indices" in selected_indicators:
            indices_to_plot = indicators
        else:
            indices_to_plot = selected_indicators
        fig_ship = px.line(
            shipping_index_pivoted,
            x="date",
            y=indices_to_plot,
            title="Shipping Indices Over Time",
            labels={"value": "Index Value", "date": "Date"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white"
        )
        fig_ship = apply_chart_styling(fig_ship)
        st.plotly_chart(fig_ship, use_container_width=True)
    else:
        st.warning("Please select at least one index to view trends.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Shipping Index Data Available</h4>
        <p>No shipping index data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Correlation
st.markdown('<div class="section-header"><h2>🔗 Shipping Index Correlation</h2></div>', unsafe_allow_html=True)
if not shipping_index_correlation.empty:
    corr_matrix = shipping_index_correlation.set_index(shipping_index_correlation.columns[0])
    corr_min = corr_matrix.min().min()
    corr_max = corr_matrix.max().max()
    if corr_max - corr_min < 0.1:
        corr_min = max(-1, corr_min - 0.1)
        corr_max = min(1, corr_max + 0.1)
    fig_corr = px.imshow(
        corr_matrix,
        title="Shipping Index Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=corr_min,
        zmax=corr_max,
        aspect="auto",
        template="plotly_white"
    )
    fig_corr = apply_chart_styling(fig_corr)
    fig_corr.update_layout(height=500)
    fig_corr.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_corr, use_container_width=True)
    st.info(f"💡 **Correlation Insights**: Values range from {corr_min:.2f} to {corr_max:.2f}. Values closer to {corr_max:.2f} indicate strong positive correlation, while values closer to {corr_min:.2f} indicate strong negative correlation.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Correlation Data Available</h4>
        <p>No shipping index correlation data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⬇️ Top 5 Decrease Items", "⬆️ Top 5 Increase Items", "🌍 Top 5 Increase Countries", "🤝 Top 5 Trade Partners", "🚢 Shipping Index"
])
with tab1:
    if not export_decrease_items_top5.empty:
        st.dataframe(export_decrease_items_top5, use_container_width=True)
        csv = export_decrease_items_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_decrease_items_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab2:
    if not export_increase_items_top5.empty:
        st.dataframe(export_increase_items_top5, use_container_width=True)
        csv = export_increase_items_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_increase_items_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab3:
    if not export_increase_countries_top5.empty:
        st.dataframe(export_increase_countries_top5, use_container_width=True)
        csv = export_increase_countries_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_increase_countries_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab4:
    if not trade_partners_top5.empty:
        st.dataframe(trade_partners_top5, use_container_width=True)
        csv = trade_partners_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "trade_partners_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab5:
    if not shipping_index_pivoted.empty:
        st.dataframe(shipping_index_pivoted, use_container_width=True)
        csv = shipping_index_pivoted.to_csv(index=False)
        st.download_button("Download CSV", csv, "shipping_index_pivoted.csv", "text/csv")
    else:
        st.info("No data available.")

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🌏 Global Trade Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> UN Comtrade, BDI, etc. | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive global trade analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True) 