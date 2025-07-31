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
manufacturing_inventory_processed = data.get("manufacturing_inventory_processed", pd.DataFrame())
inventory_volatility_analysis = data.get("inventory_volatility_analysis", pd.DataFrame())
inventory_trend_statistics = data.get("inventory_trend_statistics", pd.DataFrame())
steel_top_current = data.get("steel_top_current", pd.DataFrame())
steel_bottom_current = data.get("steel_bottom_current", pd.DataFrame())
steel_top_jan_current = data.get("steel_top_jan_current", pd.DataFrame())
steel_bottom_jan_current = data.get("steel_bottom_jan_current", pd.DataFrame())
steel_vs_world_current = data.get("steel_vs_world_current", pd.DataFrame())
steel_vs_world_jan_current = data.get("steel_vs_world_jan_current", pd.DataFrame())
steel_major_economies_current = data.get("steel_major_economies_current", pd.DataFrame())
steel_major_economies_jan_current = data.get("steel_major_economies_jan_current", pd.DataFrame())
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
            manufacturing_inventory_processed = manufacturing_inventory_processed[(pd.to_datetime(manufacturing_inventory_processed['date']).dt.date >= start_date) & (pd.to_datetime(manufacturing_inventory_processed['date']).dt.date <= end_date)] if 'date' in manufacturing_inventory_processed.columns else manufacturing_inventory_processed
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
        default=[select_all_label],  # Only 'Select All' is selected by default
        key="category_multiselect"
    )
    if select_all_label in selected:
        selected_categories = all_categories
    else:
        selected_categories = [c for c in selected if c in all_categories]
    if selected_categories:
        manufacturing_inventory_raw = manufacturing_inventory_raw[manufacturing_inventory_raw['category'].isin(selected_categories)]
        manufacturing_inventory_processed = manufacturing_inventory_processed[manufacturing_inventory_processed['category'].isin(selected_categories)] if 'category' in manufacturing_inventory_processed.columns else manufacturing_inventory_processed

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

# Get metrics from key insights
if key_insights:
    inv = key_insights.get("manufacturing_inventory", {})
    steel = key_insights.get("steel_production", {})
    data_quality = key_insights.get("data_quality", {})
    
    avg_mom = inv.get("average_mom_change", "N/A")
    avg_yoy = inv.get("average_yoy_change", "N/A")
    latest_date = inv.get("latest_date", "N/A")
    vol_count = len(inv.get("volatility_summary", []))
    total_indicators = inv.get("total_indicators", "N/A")
    
    # Steel metrics
    top_steel = steel.get("top_current_performers", [])
    top_steel_region = top_steel[0].get("region", "N/A") if top_steel else "N/A"
    total_regions = steel.get("total_regions", "N/A")
    
    # Data quality
    inv_completeness = data_quality.get("inventory_completeness", 0)
    steel_completeness = data_quality.get("steel_completeness", 0)
else:
    avg_mom = avg_yoy = latest_date = vol_count = total_indicators = "N/A"
    top_steel_region = total_regions = "N/A"
    inv_completeness = steel_completeness = 0

# Get last update date
def get_latest_update_date():
    dates = []
    if not manufacturing_inventory_raw.empty and 'date' in manufacturing_inventory_raw.columns:
        dates.append(pd.to_datetime(manufacturing_inventory_raw['date']).max())
    if not steel_production_raw.empty and 'date' in steel_production_raw.columns:
        dates.append(pd.to_datetime(steel_production_raw['date']).max())
    if dates:
        return max(dates).strftime('%Y-%m-%d')
    return "N/A"

last_update = get_latest_update_date()

# Expand to 6 columns
col1, col2, col3, col4, col5, col6 = st.columns(6)

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
        "🏭 Top Steel Producer",
        top_steel_region,
        f"Regions: {total_regions}",
        "#ffc107"
    ), unsafe_allow_html=True)
with col4:
    st.markdown(create_metric_card(
        "📈 High Volatility Entries",
        f"{vol_count}" if isinstance(vol_count, int) else str(vol_count),
        "Inventory",
        "#dc3545"
    ), unsafe_allow_html=True)
with col5:
    st.markdown(create_metric_card(
        "📊 Total Indicators",
        f"{total_indicators}" if isinstance(total_indicators, int) else str(total_indicators),
        "Manufacturing",
        "#6f42c1"
    ), unsafe_allow_html=True)
with col6:
    st.markdown(create_metric_card(
        "⏰ Last Update",
        last_update,
        "Latest data date",
        "#fd7e14"
    ), unsafe_allow_html=True)

# Manufacturing Inventory Trends
st.markdown('<div class="section-header"><h2>📦 Manufacturing Inventory Trends</h2></div>', unsafe_allow_html=True)
if not manufacturing_inventory_processed.empty:
    fig_inv = px.line(
        manufacturing_inventory_processed,
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

# Create two columns for steel analysis
col1, col2 = st.columns(2)

with col1:
    # Steel Production Trends - Relative Change
    if not steel_production_raw.empty:
        # Calculate relative change (percentage change from first value for each region)
        steel_relative = steel_production_raw.copy()
        steel_relative['relative_change'] = steel_relative.groupby('region')['value'].transform(
            lambda x: ((x - x.iloc[0]) / x.iloc[0]) * 100
        )
        
        fig_steel = px.line(
            steel_relative,
            x="date",
            y="relative_change",
            color="region",
            title="Steel Production - Relative Change by Region",
            labels={"relative_change": "Relative Change (%)", "date": "Date"},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white"
        )
        fig_steel = apply_chart_styling(fig_steel)
        # Add horizontal line at 0% for reference
        fig_steel.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig_steel, use_container_width=True)
    else:
        st.info("No steel production trend data available.")

with col2:
    # Top Steel Producers
    if not steel_top_current.empty:
        fig_top = px.bar(
            steel_top_current,
            x="region",
            y="value",
            title="Top 5 Steel Producers (Current)",
            labels={"value": "Production (thousand tons)", "region": "Region"},
            color="value",
            color_continuous_scale="Blues"
        )
        fig_top = apply_chart_styling(fig_top)
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("No top steel producers data available.")

# Steel Production Rankings
st.markdown('<div class="section-header"><h2>🏆 Steel Production Rankings</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🥇 Top 5 Producers - Current Month")
    if not steel_top_current.empty:
        st.dataframe(steel_top_current, use_container_width=True)
        st.caption("📊 Based on absolute production volume (thousand tons)")
    else:
        st.info("No current month top performers data available.")

with col2:
    st.subheader("🥉 Bottom 5 Producers - Current Month")
    if not steel_bottom_current.empty:
        st.dataframe(steel_bottom_current, use_container_width=True)
        st.caption("📊 Based on absolute production volume (thousand tons)")
    else:
        st.info("No current month bottom performers data available.")

# World Comparison Analysis
st.markdown('<div class="section-header"><h2>🌍 World Comparison Analysis</h2></div>', unsafe_allow_html=True)

if not steel_vs_world_current.empty:
    # Sort data by vs_world values in descending order (highest first)
    steel_vs_world_sorted = steel_vs_world_current.sort_values('vs_world', ascending=False)
    # Prepare data
    steel_vs_world_sorted = steel_vs_world_current.sort_values('vs_world', ascending=False).copy()
    steel_vs_world_sorted['label'] = steel_vs_world_sorted['vs_world'].round(1).astype(str) + "k"

    # Create labeled bar chart
    fig_world = px.bar(
        steel_vs_world_sorted,
        x="region",
        y="vs_world",
        title="Steel Production vs World Average",
        labels={"vs_world": "Difference from World Avg (thousand tons)", "region": "Region"},
        color="vs_world",
        color_continuous_scale="RdYlBu",
        text="label"
    )

    fig_world.update_traces(textposition="outside", cliponaxis=False)

    # Set the color scale midpoint manually
    fig_world.update_traces(marker=dict(
        colorbar=dict(title="Diff from World Avg", tickformat=".0f")
    ))

    fig_world = apply_chart_styling(fig_world)
    st.plotly_chart(fig_world, use_container_width=True)

# Major Economies Analysis
st.markdown('<div class="section-header"><h2>🏛️ Major Economies Analysis</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Month")
    if not steel_major_economies_current.empty:
        steel_major_economies_current = steel_major_economies_current.copy()
        steel_major_economies_current['label'] = steel_major_economies_current['value'].round(1).astype(str) + "k"

        fig_major_current = px.bar(
            steel_major_economies_current,
            x="region",
            y="value",
            title="Major Economies - Current Month",
            labels={"value": "Production (thousand tons)", "region": "Region"},
            color="value",
            color_continuous_scale="Greens",
            text="label"
        )
        fig_major_current.update_traces(textposition="outside", cliponaxis=False)
        fig_major_current = apply_chart_styling(fig_major_current)
        st.plotly_chart(fig_major_current, use_container_width=True)
    else:
        st.info("No major economies current data available.")

with col2:
    st.subheader("Year-to-Date Cumulative")
    if not steel_major_economies_jan_current.empty:
        steel_major_economies_jan_current = steel_major_economies_jan_current.copy()
        steel_major_economies_jan_current['label'] = steel_major_economies_jan_current['value'].round(1).astype(str) + "k"

        fig_major_jan = px.bar(
            steel_major_economies_jan_current,
            x="region",
            y="value",
            title="Major Economies - Year-to-Date Production",
            labels={"value": "Production (thousand tons)", "region": "Region"},
            color="value",
            color_continuous_scale="Oranges",
            text="label"
        )
        fig_major_jan.update_traces(textposition="outside", cliponaxis=False)
        fig_major_jan = apply_chart_styling(fig_major_jan)
        st.plotly_chart(fig_major_jan, use_container_width=True)
    else:
        st.info("No major economies year-to-date data available.")

# Trend Statistics Analysis
st.markdown('<div class="section-header"><h2>📈 Trend Statistics Analysis</h2></div>', unsafe_allow_html=True)

if not inventory_trend_statistics.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Trend consistency metrics
        if 'mom_volatility' in inventory_trend_statistics.columns and 'current_trend' in inventory_trend_statistics.columns:
            fig_trend = px.bar(
                inventory_trend_statistics,
                x="category",
                y="mom_volatility",
                color="current_trend",
                title="Trend Consistency by Category",
                labels={"mom_volatility": "MoM Volatility", "category": "Category"},
                color_discrete_map={
                    'Positive': '#28a745',
                    'Negative': '#dc3545',
                    'Neutral': '#6c757d'
                },
                text=inventory_trend_statistics["mom_volatility"].round(1).astype(str)
            )
            fig_trend.update_traces(textposition="outside", cliponaxis=False)
            fig_trend = apply_chart_styling(fig_trend)
            st.plotly_chart(fig_trend, use_container_width=True)

    
    with col2:
        # Momentum analysis
        if 'positive_momentum_3m' in inventory_trend_statistics.columns and 'positive_momentum_6m' in inventory_trend_statistics.columns:
            # Compute momentum ratio and labels
            momentum_data = inventory_trend_statistics[['category', 'positive_momentum_3m', 'positive_momentum_6m']].copy()
            momentum_data['momentum_ratio'] = momentum_data['positive_momentum_3m'] / momentum_data['positive_momentum_6m']
            momentum_data['label'] = momentum_data['momentum_ratio'].round(2).astype(str)

            # Define manual colors (matching trend direction if available)
            color_map = {
                "Equipment Investment Index": "#b30000",  # Red tone
                "Manufacturing Inventory Ratio": "#006400"  # Green tone
            }
            momentum_data['bar_color'] = momentum_data['category'].map(color_map)

            # Plot without color scale
            fig_momentum = px.bar(
                momentum_data,
                x="category",
                y="momentum_ratio",
                title="3M vs 6M Momentum Ratio",
                labels={"momentum_ratio": "3M/6M Momentum Ratio", "category": "Category"},
                text="label",
                color_discrete_sequence=["#999999"]  # dummy for compliance
            )
            fig_momentum.update_traces(
                textposition="outside",
                marker_color=momentum_data["bar_color"],
                cliponaxis=False
            )
            fig_momentum.update_layout(
                xaxis_tickangle=0,
                coloraxis_showscale=False  # hide unnecessary color scale
            )
            fig_momentum = apply_chart_styling(fig_momentum)
            fig_momentum.add_hline(y=1, line_dash="dot", line_color="gray", opacity=0.5)
            st.plotly_chart(fig_momentum, use_container_width=True)


    
    # Trend statistics summary table
    st.subheader("📊 Trend Statistics Summary")
    display_columns = ['category', 'avg_mom_change', 'avg_yoy_change', 'months_above_3m_ma', 'months_above_12m_ma']
    available_columns = [col for col in display_columns if col in inventory_trend_statistics.columns]
    
    if available_columns:
        summary_df = inventory_trend_statistics[available_columns].copy()
        # Format percentage columns
        if 'avg_mom_change' in summary_df.columns:
            summary_df['avg_mom_change'] = summary_df['avg_mom_change'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        if 'avg_yoy_change' in summary_df.columns:
            summary_df['avg_yoy_change'] = summary_df['avg_yoy_change'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.dataframe(inventory_trend_statistics, use_container_width=True)
else:
    st.info("No trend statistics data available.")

# Volatility Analysis
st.markdown('<div class="section-header"><h2>📊 Volatility Analysis</h2></div>', unsafe_allow_html=True)

if not inventory_volatility_analysis.empty:
    # Create volatility visualization
    # Add label column
    inventory_volatility_analysis["volatility_label"] = inventory_volatility_analysis["volatility_std"].round(2).astype(str) + " σ"

    # Create chart with labels
    fig_vol = px.bar(
        inventory_volatility_analysis,
        x="indicator",
        y="volatility_std",
        color="period",
        title="Inventory Volatility by Indicator and Period",
        labels={"volatility_std": "Standard Deviation", "indicator": "Indicator"},
        barmode="group",
        text="volatility_label"
    )
    fig_vol.update_traces(textposition="outside", cliponaxis=False)
    fig_vol = apply_chart_styling(fig_vol)
    st.plotly_chart(fig_vol, use_container_width=True)


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

# Data Quality Metrics
st.markdown('<div class="section-header"><h2>📋 Data Quality Metrics</h2></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Inventory Data Completeness", f"{inv_completeness*100:.1f}%")
with col2:
    st.metric("Steel Data Completeness", f"{steel_completeness*100:.1f}%")
with col3:
    st.metric("Total Data Points", len(manufacturing_inventory_raw) + len(steel_production_raw))
with col4:
    st.metric("Data Sources", "2")

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📦 Manufacturing Inventory", "🏭 Steel Production", "📊 Volatility Analysis", "📈 Trend Statistics", "🏆 Rankings", "🌍 World Comparison"
])

with tab1:
    if not manufacturing_inventory_raw.empty:
        with st.expander("📦 Manufacturing Inventory Raw Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_inventory"):
                    csv = manufacturing_inventory_raw.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"manufacturing_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search categories:", placeholder="Enter category name...", key="search_inventory")
            if search_term:
                filtered_data = manufacturing_inventory_raw[
                    manufacturing_inventory_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = manufacturing_inventory_raw
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No manufacturing inventory data available.")

with tab2:
    if not steel_production_raw.empty:
        with st.expander("🏭 Steel Production Raw Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_steel"):
                    csv = steel_production_raw.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"steel_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search regions:", placeholder="Enter region name...", key="search_steel")
            if search_term:
                filtered_data = steel_production_raw[
                    steel_production_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = steel_production_raw
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No steel production data available.")

with tab3:
    if not inventory_volatility_analysis.empty:
        with st.expander("📊 Volatility Analysis Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_volatility"):
                    csv = inventory_volatility_analysis.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"volatility_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            st.dataframe(inventory_volatility_analysis, use_container_width=True)
    else:
        st.info("No volatility analysis data available.")

with tab4:
    if not inventory_trend_statistics.empty:
        with st.expander("📈 Trend Statistics Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_trend_stats"):
                    csv = inventory_trend_statistics.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"trend_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            st.dataframe(inventory_trend_statistics, use_container_width=True)
    else:
        st.info("No trend statistics data available.")

with tab5:
    if not steel_top_current.empty or not steel_bottom_current.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥇 Top Performers")
            if not steel_top_current.empty:
                st.dataframe(steel_top_current, use_container_width=True)
        with col2:
            st.subheader("🥉 Bottom Performers")
            if not steel_bottom_current.empty:
                st.dataframe(steel_bottom_current, use_container_width=True)
    else:
        st.info("No rankings data available.")

with tab6:
    if not steel_vs_world_current.empty:
        with st.expander("🌍 World Comparison Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_world"):
                    csv = steel_vs_world_current.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"world_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            st.dataframe(steel_vs_world_current, use_container_width=True)
    else:
        st.info("No world comparison data available.")

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