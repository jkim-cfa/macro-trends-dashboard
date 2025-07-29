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
from utils.data_loader import load_industry_data

# Page Config
st.set_page_config(
    page_title="Industry Dashboard",
    page_icon="🏭",
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
    <h1>🏭 Industry Dashboard</h1>
    <p>Comprehensive analysis of manufacturing inventory, steel production, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_industry_data():
    try:
        data = load_industry_data()
        return data
    except Exception as e:
        st.error(f"Error loading industry data: {str(e)}")
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
with st.spinner("Loading industry intelligence data..."):
    data = load_cached_industry_data()

# Extract data
manufacturing_inventory_raw = data.get("manufacturing_inventory_raw", pd.DataFrame())
steel_production_raw = data.get("steel_production_raw", pd.DataFrame())
inventory_processed_data = data.get("inventory_processed_data", pd.DataFrame())
inventory_volatility_analysis = data.get("inventory_volatility_analysis", pd.DataFrame())
steel_top_current = data.get("steel_top_current", pd.DataFrame())
steel_bottom_current = data.get("steel_bottom_current", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter for manufacturing inventory
if not manufacturing_inventory_raw.empty and 'date' in manufacturing_inventory_raw.columns:
    try:
        min_date = pd.to_datetime(manufacturing_inventory_raw['date']).min()
        max_date = pd.to_datetime(manufacturing_inventory_raw['date']).max()
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            manufacturing_inventory_raw = manufacturing_inventory_raw[(pd.to_datetime(manufacturing_inventory_raw['date']).dt.date >= start_date) & (pd.to_datetime(manufacturing_inventory_raw['date']).dt.date <= end_date)]
            inventory_processed_data = inventory_processed_data[(pd.to_datetime(inventory_processed_data['date']).dt.date >= start_date) & (pd.to_datetime(inventory_processed_data['date']).dt.date <= end_date)] if 'date' in inventory_processed_data.columns else inventory_processed_data
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Category filter for manufacturing inventory
if not manufacturing_inventory_raw.empty and 'category' in manufacturing_inventory_raw.columns:
    st.sidebar.markdown("### 🏷️ Category Filter")
    all_categories = list(manufacturing_inventory_raw['category'].unique())
    select_all_label = "Select All"
    multiselect_options = [select_all_label] + all_categories
    selected = st.sidebar.multiselect(
        "Select categories:",
        options=multiselect_options,
        default=multiselect_options,
        key="category_multiselect"
    )
    if select_all_label in selected:
        selected_categories = all_categories
    else:
        selected_categories = [c for c in selected if c in all_categories]
    if selected_categories:
        manufacturing_inventory_raw = manufacturing_inventory_raw[manufacturing_inventory_raw['category'].isin(selected_categories)]
        inventory_processed_data = inventory_processed_data[inventory_processed_data['category'].isin(selected_categories)] if 'category' in inventory_processed_data.columns else inventory_processed_data

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if 'selected_categories' in locals() and selected_categories:
    if len(selected_categories) == len(all_categories):
        active_filters.append(f"Categories: All ({len(selected_categories)})")
    else:
        active_filters.append(f"Categories: {len(selected_categories)} selected")
if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Industry Metrics</h2></div>', unsafe_allow_html=True)
if key_insights and "manufacturing_inventory" in key_insights:
    inv = key_insights["manufacturing_inventory"]
    avg_mom = inv.get("average_mom_change", "N/A")
    avg_yoy = inv.get("average_yoy_change", "N/A")
    latest_date = inv.get("latest_date", "N/A")
    vol_count = len(inv.get("volatility_summary", []))
else:
    avg_mom = avg_yoy = latest_date = vol_count = "N/A"
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_metric_card(
        "📦 Avg MoM Change",
        f"{avg_mom:.2f}%" if isinstance(avg_mom, (int, float)) else str(avg_mom),
        "Manufacturing Inventory",
        "#28a745"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "📦 Avg YoY Change",
        f"{avg_yoy:.2f}%" if isinstance(avg_yoy, (int, float)) else str(avg_yoy),
        "Manufacturing Inventory",
        "#007bff"
    ), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card(
        "📅 Latest Data",
        latest_date,
        "Inventory",
        "#ffc107"
    ), unsafe_allow_html=True)
with col4:
    st.markdown(create_metric_card(
        "📈 High Volatility Entries",
        f"{vol_count}" if isinstance(vol_count, int) else str(vol_count),
        "Inventory",
        "#dc3545"
    ), unsafe_allow_html=True)

# Manufacturing Inventory Trends
st.markdown('<div class="section-header"><h2>📦 Manufacturing Inventory Trends</h2></div>', unsafe_allow_html=True)
if not inventory_processed_data.empty:
    fig_inv = px.line(
        inventory_processed_data,
        x="date",
        y="value",
        color="category",
        title="Manufacturing Inventory by Category",
        labels={"value": "Inventory Index", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Set3,
        template="plotly_white"
    )
    fig_inv = apply_chart_styling(fig_inv)
    st.plotly_chart(fig_inv, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Inventory Data Available</h4>
        <p>No manufacturing inventory data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Steel Production Analysis
st.markdown('<div class="section-header"><h2>🏭 Steel Production Analysis</h2></div>', unsafe_allow_html=True)
if not steel_production_raw.empty:
    fig_steel = px.line(
        steel_production_raw,
        x="date",
        y="value",
        color="region",
        title="Steel Production by Region",
        labels={"value": "Production (thousand tons)", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    fig_steel = apply_chart_styling(fig_steel)
    st.plotly_chart(fig_steel, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Steel Production Data Available</h4>
        <p>No steel production data is currently available.</p>
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
tab1, tab2, tab3 = st.tabs([
    "📦 Manufacturing Inventory", "🏭 Steel Production", "📊 Volatility Analysis"
])
with tab1:
    if not manufacturing_inventory_raw.empty:
        st.dataframe(manufacturing_inventory_raw, use_container_width=True)
        csv = manufacturing_inventory_raw.to_csv(index=False)
        st.download_button("Download CSV", csv, "manufacturing_inventory_raw.csv", "text/csv")
    else:
        st.info("No data available.")
with tab2:
    if not steel_production_raw.empty:
        st.dataframe(steel_production_raw, use_container_width=True)
        csv = steel_production_raw.to_csv(index=False)
        st.download_button("Download CSV", csv, "steel_production_raw.csv", "text/csv")
    else:
        st.info("No data available.")
with tab3:
    if not inventory_volatility_analysis.empty:
        st.dataframe(inventory_volatility_analysis, use_container_width=True)
        csv = inventory_volatility_analysis.to_csv(index=False)
        st.download_button("Download CSV", csv, "inventory_volatility_analysis.csv", "text/csv")
    else:
        st.info("No data available.")

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🏭 Industry Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> Statistics Korea, World Steel Association | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive industry analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True) 