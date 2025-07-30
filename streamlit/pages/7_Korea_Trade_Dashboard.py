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
from utils.data_loader import load_korea_trade_data

# Page Config
st.set_page_config(
    page_title="Korea Trade Dashboard",
    page_icon="🇰🇷",
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
    <h1>🇰🇷 Korea Trade Dashboard</h1>
    <p>Comprehensive analysis of Korea's export/import trade, semiconductor industry, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_korea_trade_data():
    try:
        data = load_korea_trade_data()
        return data
    except Exception as e:
        st.error(f"Error loading Korea trade data: {str(e)}")
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
with st.spinner("Loading Korea trade intelligence data..."):
    data = load_cached_korea_trade_data()

# Extract data
export_top_partners = data.get("export_top_partners", pd.DataFrame())
import_top_partners = data.get("import_top_partners", pd.DataFrame())
export_top_items_by_amount = data.get("export_top_items_by_amount", pd.DataFrame())
export_top_items_by_yoy = data.get("export_top_items_by_yoy", pd.DataFrame())
import_top_items_by_amount = data.get("import_top_items_by_amount", pd.DataFrame())
import_top_items_by_yoy = data.get("import_top_items_by_yoy", pd.DataFrame())
trade_yoy_top_export_partners = data.get("trade_yoy_top_export_partners", pd.DataFrame())
trade_yoy_top_import_partners = data.get("trade_yoy_top_import_partners", pd.DataFrame())
trade_balance = data.get("trade_balance", pd.DataFrame())
value_index_top_yoy = data.get("value_index_top_yoy", pd.DataFrame())
value_index_bottom_yoy = data.get("value_index_bottom_yoy", pd.DataFrame())
value_index_volatility = data.get("value_index_volatility", pd.DataFrame())
wsts_top_monthly_regions = data.get("wsts_top_monthly_regions", pd.DataFrame())
wsts_top_annual_regions = data.get("wsts_top_annual_regions", pd.DataFrame())
wsts_volatility = data.get("wsts_volatility", pd.DataFrame())
wsts_trend_monthly = data.get("wsts_trend_monthly", pd.DataFrame())
wsts_trend_annual = data.get("wsts_trend_annual", pd.DataFrame())
wsts_yoy_monthly = data.get("wsts_yoy_monthly", pd.DataFrame())
wsts_yoy_annual = data.get("wsts_yoy_annual", pd.DataFrame())
wsts_market_share_monthly = data.get("wsts_market_share_monthly", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")
gemini_insights_data = data.get("gemini_insights_data", {})

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter for trade balance
if not trade_balance.empty and 'date' in trade_balance.columns:
    try:
        min_date = pd.to_datetime(trade_balance['date']).min()
        max_date = pd.to_datetime(trade_balance['date']).max()
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            trade_balance = trade_balance[(pd.to_datetime(trade_balance['date']).dt.date >= start_date) & (pd.to_datetime(trade_balance['date']).dt.date <= end_date)]
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Partner filter
if not export_top_partners.empty and 'partner' in export_top_partners.columns:
    st.sidebar.markdown("### 🤝 Partner Filter")
    all_partners = list(export_top_partners['partner'].unique())
    select_all_label = "Select All"
    multiselect_options = [select_all_label] + all_partners
    selected = st.sidebar.multiselect(
        "Select partners:",
        options=multiselect_options,
        default=[select_all_label],  # Only 'Select All' by default
        key="partner_multiselect"
    )
    if select_all_label in selected:
        selected_partners = all_partners
    else:
        selected_partners = [c for c in selected if c in all_partners]
    if selected_partners:
        export_top_partners = export_top_partners[export_top_partners['partner'].isin(selected_partners)]
        import_top_partners = import_top_partners[import_top_partners['partner'].isin(selected_partners)]

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if 'selected_partners' in locals() and selected_partners:
    if len(selected_partners) == len(all_partners):
        active_filters.append(f"Partners: All ({len(selected_partners)})")
    else:
        active_filters.append(f"Partners: {len(selected_partners)} selected")
if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Trade Metrics</h2></div>', unsafe_allow_html=True)

# Get data from key insights if available, otherwise use direct data
if key_insights and isinstance(key_insights, dict):
    export_analysis = key_insights.get("export_analysis", {})
    import_analysis = key_insights.get("import_analysis", {})
    
    top_export_commodity = export_analysis.get("top_commodity", "N/A")
    top_export_amount = export_analysis.get("top_commodity_amount", "N/A")
    top_import_commodity = import_analysis.get("top_commodity", "N/A")
    top_import_amount = import_analysis.get("top_commodity_amount", "N/A")
else:
    # Fallback to direct data extraction
    top_export_commodity = "N/A"
    top_export_amount = "N/A"
    top_import_commodity = "N/A"
    top_import_amount = "N/A"
    
    # Try to get from actual data if key insights not available
    if not export_top_items_by_amount.empty:
        top_export_commodity = export_top_items_by_amount.iloc[0]['commodity_name_en'] if len(export_top_items_by_amount) > 0 else "N/A"
        top_export_amount = export_top_items_by_amount.iloc[0]['export_amount'] if len(export_top_items_by_amount) > 0 else "N/A"
    
    if not import_top_items_by_amount.empty:
        top_import_commodity = import_top_items_by_amount.iloc[0]['commodity_name_en'] if len(import_top_items_by_amount) > 0 else "N/A"
        top_import_amount = import_top_items_by_amount.iloc[0]['import_amount'] if len(import_top_items_by_amount) > 0 else "N/A"

if not export_top_items_by_yoy.empty:
    top_export_yoy_item = export_top_items_by_yoy.iloc[0]['commodity_name_en'] if len(export_top_items_by_yoy) > 0 else "N/A"
    top_export_yoy_growth = export_top_items_by_yoy.iloc[0]['trade_yoy'] if len(export_top_items_by_yoy) > 0 else "N/A"

if not import_top_items_by_yoy.empty:
    top_import_yoy_item = import_top_items_by_yoy.iloc[0]['commodity_name_en'] if len(import_top_items_by_yoy) > 0 else "N/A"
    top_import_yoy_growth = import_top_items_by_yoy.iloc[0]['trade_yoy'] if len(import_top_items_by_yoy) > 0 else "N/A"

if not trade_yoy_top_export_partners.empty:
    top_export_partner = trade_yoy_top_export_partners.iloc[0]['partner'] if len(trade_yoy_top_export_partners) > 0 else "N/A"
    # Filter out "World" from key metrics
    if top_export_partner == "World":
        top_export_partner = "N/A"

if not trade_yoy_top_import_partners.empty:
    top_import_partner = trade_yoy_top_import_partners.iloc[0]['partner'] if len(trade_yoy_top_import_partners) > 0 else "N/A"
    # Filter out "World" from key metrics
    if top_import_partner == "World":
        top_import_partner = "N/A"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_metric_card(
        "📤 Top Export Commodity",
        top_export_commodity,
        f"${top_export_amount:,.0f}" if isinstance(top_export_amount, (int, float)) else str(top_export_amount),
        "#28a745"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "📥 Top Import Commodity",
        top_import_commodity,
        f"${top_import_amount:,.0f}" if isinstance(top_import_amount, (int, float)) else str(top_import_amount),
        "#007bff"
    ), unsafe_allow_html=True)
with col3:
    st.markdown(create_metric_card(
        "🤝 Top Export Partner",
        top_export_partner,
        "Trade Partner",
        "#ffc107"
    ), unsafe_allow_html=True)
with col4:
    st.markdown(create_metric_card(
        "🤝 Top Import Partner",
        top_import_partner,
        "Trade Partner",
        "#dc3545"
    ), unsafe_allow_html=True)

# Additional YoY Growth Metrics
col1, col2 = st.columns(2)
with col1:
    st.markdown(create_metric_card(
        "📤 Top Export YoY Item",
        top_export_yoy_item,
        f"YoY: {top_export_yoy_growth:.1f}%" if isinstance(top_export_yoy_growth, (int, float)) else str(top_export_yoy_growth),
        "#20c997"
    ), unsafe_allow_html=True)
with col2:
    st.markdown(create_metric_card(
        "📥 Top Import YoY Item",
        top_import_yoy_item,
        f"YoY: {top_import_yoy_growth:.1f}%" if isinstance(top_import_yoy_growth, (int, float)) else str(top_import_yoy_growth),
        "#17a2b8"
    ), unsafe_allow_html=True)



# Export/Import Partners Analysis
st.markdown('<div class="section-header"><h2>🤝 Trade Partners Analysis</h2></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if not export_top_partners.empty:
        export_top_partners = export_top_partners.copy()
        export_top_partners['export_amount_label'] = export_top_partners['export_amount'].round(0).astype(int).astype(str)
        fig_export = px.bar(
            export_top_partners.head(10),
            x="export_amount",
            y="partner",
            orientation='h',
            title="Top 10 Export Partners",
            labels={"export_amount": "Export Amount", "partner": "Partner"},
            color_discrete_sequence=["#28a745"],
            template="plotly_white"
        )
        fig_export = apply_chart_styling(fig_export)
        st.plotly_chart(fig_export, use_container_width=True)
    else:
        st.info("No export partners data available.")
with col2:
    if not import_top_partners.empty:
        import_top_partners = import_top_partners.copy()
        import_top_partners['import_amount_label'] = import_top_partners['import_amount'].round(0).astype(int).astype(str)
        fig_import = px.bar(
            import_top_partners.head(10),
            x="import_amount",
            y="partner",
            orientation='h',
            title="Top 10 Import Partners",
            labels={"import_amount": "Import Amount", "partner": "Partner"},
            color_discrete_sequence=["#007bff"],
            template="plotly_white"
        )
        fig_import = apply_chart_styling(fig_import)
        st.plotly_chart(fig_import, use_container_width=True)
    else:
        st.info("No import partners data available.")

# Trade Items Analysis
st.markdown('<div class="section-header"><h2>📦 Trade Items Analysis</h2></div>', unsafe_allow_html=True)

# Top Items by Amount
col1, col2 = st.columns(2)
with col1:
    if not export_top_items_by_amount.empty:
        export_top_items_by_amount = export_top_items_by_amount.copy()
        export_top_items_by_amount['export_amount_label'] = export_top_items_by_amount['export_amount'].round(0).astype(int).astype(str)
        fig_export_items = px.bar(
            export_top_items_by_amount.head(10),
            x="export_amount",
            y="commodity_name_en",
            orientation='h',
            title="Top 10 Export Items by Amount",
            labels={"export_amount": "Export Amount", "commodity_name_en": "Commodity"},
            color_discrete_sequence=["#28a745"],
            template="plotly_white"
        )
        fig_export_items = apply_chart_styling(fig_export_items)
        st.plotly_chart(fig_export_items, use_container_width=True)
    else:
        st.info("No export items data available.")
with col2:
    if not import_top_items_by_amount.empty:
        import_top_items_by_amount = import_top_items_by_amount.copy()
        import_top_items_by_amount['import_amount_label'] = import_top_items_by_amount['import_amount'].round(0).astype(int).astype(str)
        fig_import_items = px.bar(
            import_top_items_by_amount.head(10),
            x="import_amount",
            y="commodity_name_en",
            orientation='h',
            title="Top 10 Import Items by Amount",
            labels={"import_amount": "Import Amount", "commodity_name_en": "Commodity"},
            color_discrete_sequence=["#007bff"],
            template="plotly_white"
        )
        fig_import_items = apply_chart_styling(fig_import_items)
        st.plotly_chart(fig_import_items, use_container_width=True)
    else:
        st.info("No import items data available.")

# Top Items by YoY Growth
col1, col2 = st.columns(2)
with col1:
    if not export_top_items_by_yoy.empty:
        export_top_items_by_yoy = export_top_items_by_yoy.copy()
        export_top_items_by_yoy['trade_yoy_label'] = export_top_items_by_yoy['trade_yoy'].round(1).astype(str) + '%'
        fig_export_yoy = px.bar(
            export_top_items_by_yoy.head(10),
            x="trade_yoy",
            y="commodity_name_en",
            orientation='h',
            title="Top 10 Export Items by YoY Growth",
            labels={"trade_yoy": "YoY Growth (%)", "commodity_name_en": "Commodity"},
            color_discrete_sequence=["#20c997"],
            template="plotly_white"
        )
        fig_export_yoy = apply_chart_styling(fig_export_yoy)
        st.plotly_chart(fig_export_yoy, use_container_width=True)
    else:
        st.info("No export YoY data available.")
with col2:
    if not import_top_items_by_yoy.empty:
        import_top_items_by_yoy = import_top_items_by_yoy.copy()
        import_top_items_by_yoy['trade_yoy_label'] = import_top_items_by_yoy['trade_yoy'].round(1).astype(str) + '%'
        fig_import_yoy = px.bar(
            import_top_items_by_yoy.head(10),
            x="trade_yoy",
            y="commodity_name_en",
            orientation='h',
            title="Top 10 Import Items by YoY Growth",
            labels={"trade_yoy": "YoY Growth (%)", "commodity_name_en": "Commodity"},
            color_discrete_sequence=["#17a2b8"],
            template="plotly_white"
        )
        fig_import_yoy = apply_chart_styling(fig_import_yoy)
        st.plotly_chart(fig_import_yoy, use_container_width=True)
    else:
        st.info("No import YoY data available.")

# Trade YoY Analysis
st.markdown('<div class="section-header"><h2>📈 Trade YoY Analysis</h2></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if not trade_yoy_top_export_partners.empty:
        fig_export_yoy_partners = px.bar(
            trade_yoy_top_export_partners.head(10),
            x="value",
            y="partner",
            orientation='h',
            title="Top 10 Export Partners by Value",
            labels={"value": "Export Value (USD)", "partner": "Partner"},
            color_discrete_sequence=["#28a745"],
            template="plotly_white"
        )
        fig_export_yoy_partners = apply_chart_styling(fig_export_yoy_partners)
        st.plotly_chart(fig_export_yoy_partners, use_container_width=True)
    else:
        st.info("No export YoY partners data available.")
with col2:
    if not trade_yoy_top_import_partners.empty:
        fig_import_yoy_partners = px.bar(
            trade_yoy_top_import_partners.head(10),
            x="value",
            y="partner",
            orientation='h',
            title="Top 10 Import Partners by Value",
            labels={"value": "Import Value (USD)", "partner": "Partner"},
            color_discrete_sequence=["#007bff"],
            template="plotly_white"
        )
        fig_import_yoy_partners = apply_chart_styling(fig_import_yoy_partners)
        st.plotly_chart(fig_import_yoy_partners, use_container_width=True)
    else:
        st.info("No import YoY partners data available.")

# Value Index Analysis
st.markdown('<div class="section-header"><h2>💹 Value Index Analysis</h2></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if not value_index_top_yoy.empty:
        value_index_top_yoy = value_index_top_yoy.copy()
        value_index_top_yoy['yoy_change_label'] = value_index_top_yoy['yoy_change'].round(1).astype(str) + '%'
        fig_value_top = px.bar(
            value_index_top_yoy.head(10),
            x="yoy_change",
            y="item_en",
            orientation='h',
            title="Top Value Index Items by YoY Growth",
            labels={"yoy_change": "YoY Change (%)", "item_en": "Item"},
            color_discrete_sequence=["#20c997"],
            template="plotly_white",
            text="yoy_change_label"
        )
        fig_value_top.update_traces(textposition='outside')
        fig_value_top = apply_chart_styling(fig_value_top)
        st.plotly_chart(fig_value_top, use_container_width=True)
    else:
        st.info("No value index top YoY data available.")
with col2:
    if not value_index_bottom_yoy.empty:
        value_index_bottom_yoy = value_index_bottom_yoy.copy()
        value_index_bottom_yoy['yoy_change_label'] = value_index_bottom_yoy['yoy_change'].round(1).astype(str) + '%'
        fig_value_bottom = px.bar(
            value_index_bottom_yoy.head(10),
            x="yoy_change",
            y="item_en",
            orientation='h',
            title="Bottom Value Index Items by YoY Growth",
            labels={"yoy_change": "YoY Change (%)", "item_en": "Item"},
            color_discrete_sequence=["#dc3545"],
            template="plotly_white",
            text="yoy_change_label"
        )
        fig_value_bottom.update_traces(textposition='outside')
        fig_value_bottom = apply_chart_styling(fig_value_bottom)
        st.plotly_chart(fig_value_bottom, use_container_width=True)
    else:
        st.info("No value index bottom YoY data available.")

# Value Index Volatility
if not value_index_volatility.empty:
    # Aggregate by item_en, take the max volatility for each item
    volatility_agg = value_index_volatility.groupby('item_en', as_index=False)['value'].max()
    volatility_sorted = volatility_agg.sort_values('value', ascending=False).head(10)
    volatility_sorted = volatility_sorted.iloc[::-1]
    volatility_sorted = volatility_sorted.copy()
    volatility_sorted['value_label'] = volatility_sorted['value'].round(1).astype(str)
    fig_volatility = px.bar(
    volatility_sorted,
    x="value",
    y="item_en",
    orientation='h',
    title="Value Index Volatility (Top 10)",
    labels={"value": "Volatility (Std Dev)", "item_en": "Item"},
    color_discrete_sequence=["#fd7e14"],
    template="plotly_white",
    text="value_label"  # use for labeling
)
    fig_volatility.update_traces(
    textposition='outside',  # 'outside' puts label outside bar; use 'auto' for fallback
    cliponaxis=False  # allow text to render outside plot area
)
    fig_volatility.update_layout(
    margin=dict(l=120, r=40, t=60, b=40),
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)
    fig_volatility = apply_chart_styling(fig_volatility)
    st.plotly_chart(fig_volatility, use_container_width=True)

# Trade Balance Analysis
st.markdown('<div class="section-header"><h2>⚖️ Trade Balance Analysis</h2></div>', unsafe_allow_html=True)
if not trade_balance.empty and 'trade_balance' in trade_balance.columns:
    fig_balance = px.line(
        trade_balance,
        x="date",
        y="trade_balance",
        title="Trade Balance Over Time",
        labels={"trade_balance": "Trade Balance (USD)", "date": "Date"},
        color_discrete_sequence=["#6f42c1"],
        template="plotly_white"
    )
    fig_balance = apply_chart_styling(fig_balance)
    st.plotly_chart(fig_balance, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Trade Balance Data Available</h4>
        <p>No trade balance data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Semiconductor Industry Analysis
st.markdown('<div class="section-header"><h2>🔌 Semiconductor Industry Analysis</h2></div>', unsafe_allow_html=True)

# Monthly Trend
if not wsts_trend_monthly.empty:
    # Melt the data for plotting and exclude 'index' and 'World'
    wsts_melted = wsts_trend_monthly.reset_index().melt(id_vars=['date'], var_name='region', value_name='value')
    wsts_melted = wsts_melted[~wsts_melted['region'].isin(['index', 'World'])]
    
    if not wsts_melted.empty:
        fig_semiconductor = px.line(
            wsts_melted,
            x="date",
            y="value",
            color="region",
            title="Semiconductor Billings Trend (Monthly)",
            labels={"value": "Billings (USD)", "date": "Date"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white"
        )
        fig_semiconductor = apply_chart_styling(fig_semiconductor)
        st.plotly_chart(fig_semiconductor, use_container_width=True)
    else:
        st.info("No semiconductor monthly trend data available (excluding World and index).")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Semiconductor Monthly Trend Data Available</h4>
        <p>No semiconductor monthly trend data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Annual Trend
if not wsts_trend_annual.empty:
    wsts_annual_melted = wsts_trend_annual.reset_index().melt(id_vars=['date'], var_name='region', value_name='value')
    wsts_annual_melted = wsts_annual_melted[~wsts_annual_melted['region'].isin(['index', 'World'])]
    
    if not wsts_annual_melted.empty:
        fig_semiconductor_annual = px.line(
            wsts_annual_melted,
            x="date",
            y="value",
            color="region",
            title="Semiconductor Billings Trend (Annual)",
            labels={"value": "Billings (USD)", "date": "Date"},
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white"
        )
        fig_semiconductor_annual = apply_chart_styling(fig_semiconductor_annual)
        st.plotly_chart(fig_semiconductor_annual, use_container_width=True)
    else:
        st.info("No semiconductor annual trend data available (excluding World and index).")
# Semiconductor YoY Growth (Monthly/Annual)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        if not wsts_yoy_monthly.empty:
            wsts_yoy_monthly_filtered = wsts_yoy_monthly[
                (~wsts_yoy_monthly['country'].isin(['World', 'index'])) &
                (wsts_yoy_monthly['yoy_change'].notna()) &
                (wsts_yoy_monthly['country'].notna())
            ]
            wsts_yoy_monthly_grouped = (
                wsts_yoy_monthly_filtered
                .groupby('country', as_index=False)['yoy_change']
                .mean()
            )
            wsts_yoy_monthly_grouped = wsts_yoy_monthly_grouped.sort_values('yoy_change', ascending=False).head(10)
            wsts_yoy_monthly_grouped = wsts_yoy_monthly_grouped.iloc[::-1]
            wsts_yoy_monthly_grouped['yoy_label'] = wsts_yoy_monthly_grouped['yoy_change'].round(1).astype(str) + '%'

            if not wsts_yoy_monthly_grouped.empty:
                fig_yoy_monthly = px.bar(
                    wsts_yoy_monthly_grouped,
                    x="yoy_change",
                    y="country",
                    orientation='h',
                    title="Semiconductor YoY Growth (Monthly)",
                    labels={"yoy_change": "YoY Change (%)", "country": "Region"},
                    color_discrete_sequence=["#20c997"],
                    template="plotly_white",
                    text="yoy_label"  # Add labels
                )
                fig_yoy_monthly.update_traces(textposition='outside')
                fig_yoy_monthly = apply_chart_styling(fig_yoy_monthly)
                st.plotly_chart(fig_yoy_monthly, use_container_width=True)
            else:
                st.info("No semiconductor YoY monthly data available (excluding World and index).")
        else:
            st.info("No semiconductor YoY monthly data available.")

    with col2:
        if not wsts_yoy_annual.empty:
            wsts_yoy_annual_filtered = wsts_yoy_annual[
                (~wsts_yoy_annual['country'].isin(['World', 'index'])) &
                (wsts_yoy_annual['yoy_change'].notna()) &
                (wsts_yoy_annual['country'].notna())
            ]
            wsts_yoy_annual_grouped = (
                wsts_yoy_annual_filtered
                .groupby('country', as_index=False)['yoy_change']
                .mean()
            )
            wsts_yoy_annual_grouped = wsts_yoy_annual_grouped.sort_values('yoy_change', ascending=False).head(10)
            wsts_yoy_annual_grouped = wsts_yoy_annual_grouped.iloc[::-1]
            wsts_yoy_annual_grouped['yoy_label'] = wsts_yoy_annual_grouped['yoy_change'].round(1).astype(str) + '%'

            if not wsts_yoy_annual_grouped.empty:
                fig_yoy_annual = px.bar(
                    wsts_yoy_annual_grouped,
                    x="yoy_change",
                    y="country",
                    orientation='h',
                    title="Semiconductor YoY Growth (Annual)",
                    labels={"yoy_change": "YoY Change (%)", "country": "Region"},
                    color_discrete_sequence=["#17a2b8"],
                    template="plotly_white",
                    text="yoy_label"  # Add labels
                )
                fig_yoy_annual.update_traces(textposition='outside')
                fig_yoy_annual = apply_chart_styling(fig_yoy_annual)
                st.plotly_chart(fig_yoy_annual, use_container_width=True)
            else:
                st.info("No semiconductor YoY annual data available (excluding World and index).")
        else:
            st.info("No semiconductor YoY annual data available.")


# Market Share Analysis
if not wsts_market_share_monthly.empty:
    # Filter out 'World' from market share data
    wsts_market_share_filtered = wsts_market_share_monthly[~wsts_market_share_monthly['country'].isin(['World'])]
    if not wsts_market_share_filtered.empty:
        fig_market_share = px.line(
            wsts_market_share_filtered,
            x="date",
            y="market_share",
            color="country",
            title="Semiconductor Market Share Trends",
            labels={"market_share": "Market Share (%)", "date": "Date", "country": "Region"},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white"
        )
        fig_market_share = apply_chart_styling(fig_market_share)
        st.plotly_chart(fig_market_share, use_container_width=True)
    else:
        st.info("No semiconductor market share data available (excluding World).")

# Volatility Analysis
if not wsts_volatility.empty:
    # Filter out 'World' from volatility data
    wsts_volatility_filtered = wsts_volatility[~wsts_volatility['country'].isin(['World'])]
    if not wsts_volatility_filtered.empty:
        wsts_volatility_labeled = wsts_volatility_filtered.copy()
        wsts_volatility_labeled = wsts_volatility_labeled.sort_values("value", ascending=False).head(10)
        wsts_volatility_labeled = wsts_volatility_labeled.iloc[::-1]  # Reverse for top-to-bottom display
        wsts_volatility_labeled["volatility_label"] = wsts_volatility_labeled["value"].round(2).astype(str)

        fig_volatility_semiconductor = px.bar(
            wsts_volatility_labeled,
            x="value",
            y="country",
            orientation='h',
            title="Semiconductor Industry Volatility (Top 10)",
            labels={"value": "Volatility (Std Dev)", "country": "Region"},
            color_discrete_sequence=["#fd7e14"],
            template="plotly_white",
            text="volatility_label"  # Add label
        )
        fig_volatility_semiconductor.update_traces(textposition="outside", cliponaxis=False)
        fig_volatility_semiconductor = apply_chart_styling(fig_volatility_semiconductor)
        st.plotly_chart(fig_volatility_semiconductor, use_container_width=True)


# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)
 
# Text-based AI Insights
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
    # Format Last Updated to show only date
    last_updated_raw = gemini_insights_data.get("generated_at") if gemini_insights_data else None
    if last_updated_raw:
        try:
            last_updated = str(last_updated_raw)[:10]  # Handles both ISO and date strings
        except Exception:
            last_updated = datetime.now().strftime("%Y-%m-%d")
    else:
        last_updated = datetime.now().strftime("%Y-%m-%d")
    insight_metrics = {
        "Sections Available": len([s for s in sections.values() if s]),
        "Total Insight Length": len(gemini_insight),
        "Last Updated": last_updated
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤝 Trade Partners", "📦 Trade Items", "📈 Trade YoY", "💹 Value Index", "🔌 Semiconductor", "⚖️ Trade Balance"
])

with tab1:
    # Export Partners
    if not export_top_partners.empty:
        with st.expander("📊 Export Partners Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_partners"):
                    csv = export_top_partners.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"export_partners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_export_partners")
            if search_term:
                filtered_data = export_top_partners[
                    export_top_partners.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = export_top_partners
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No export partners data available.")
    # Import Partners
    if not import_top_partners.empty:
        with st.expander("📊 Import Partners Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="import_partners"):
                    csv = import_top_partners.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"import_partners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_import_partners")
            if search_term:
                filtered_data = import_top_partners[
                    import_top_partners.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = import_top_partners
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No import partners data available.")

with tab2:
    # Export Items by Amount
    if not export_top_items_by_amount.empty:
        with st.expander("📦 Export Items by Amount Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_items_amount"):
                    csv = export_top_items_by_amount.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"export_items_amount_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_export_items_amount")
            if search_term:
                filtered_data = export_top_items_by_amount[
                    export_top_items_by_amount.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = export_top_items_by_amount
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No export items data available.")
    # Import Items by Amount
    if not import_top_items_by_amount.empty:
        with st.expander("📦 Import Items by Amount Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="import_items_amount"):
                    csv = import_top_items_by_amount.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"import_items_amount_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_import_items_amount")
            if search_term:
                filtered_data = import_top_items_by_amount[
                    import_top_items_by_amount.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = import_top_items_by_amount
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No import items data available.")

with tab3:
    # Export Partners YoY
    if not trade_yoy_top_export_partners.empty:
        with st.expander("📈 Export Partners YoY Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="export_partners_yoy"):
                    csv = trade_yoy_top_export_partners.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"export_partners_yoy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_export_partners_yoy")
            if search_term:
                filtered_data = trade_yoy_top_export_partners[
                    trade_yoy_top_export_partners.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = trade_yoy_top_export_partners
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No export YoY partners data available.")
    # Import Partners YoY
    if not trade_yoy_top_import_partners.empty:
        with st.expander("📈 Import Partners YoY Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="import_partners_yoy"):
                    csv = trade_yoy_top_import_partners.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"import_partners_yoy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_import_partners_yoy")
            if search_term:
                filtered_data = trade_yoy_top_import_partners[
                    trade_yoy_top_import_partners.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = trade_yoy_top_import_partners
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No import YoY partners data available.")

with tab4:
    # Value Index Top YoY
    if not value_index_top_yoy.empty:
        with st.expander("💹 Value Index Top YoY Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="value_index_top_yoy"):
                    csv = value_index_top_yoy.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"value_index_top_yoy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_value_index_top_yoy")
            if search_term:
                filtered_data = value_index_top_yoy[
                    value_index_top_yoy.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = value_index_top_yoy
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No value index top YoY data available.")
    # Value Index Bottom YoY
    if not value_index_bottom_yoy.empty:
        with st.expander("💹 Value Index Bottom YoY Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="value_index_bottom_yoy"):
                    csv = value_index_bottom_yoy.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"value_index_bottom_yoy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_value_index_bottom_yoy")
            if search_term:
                filtered_data = value_index_bottom_yoy[
                    value_index_bottom_yoy.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = value_index_bottom_yoy
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No value index bottom YoY data available.")
    # Value Index Volatility
    if not value_index_volatility.empty:
        with st.expander("💹 Value Index Volatility Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="value_index_volatility"):
                    csv = value_index_volatility.to_csv()
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"value_index_volatility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_value_index_volatility")
            if search_term:
                filtered_data = value_index_volatility[
                    value_index_volatility.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = value_index_volatility
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No value index volatility data available.")

with tab5:
    # Semiconductor Monthly Trend Data
    if not wsts_trend_monthly.empty:
        with st.expander("🔌 Semiconductor Monthly Trend Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="wsts_trend_monthly"):
                    csv = wsts_trend_monthly.to_csv()
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"wsts_trend_monthly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search regions:", placeholder="Enter region name...", key="search_wsts_trend_monthly")
            if search_term:
                filtered_data = wsts_trend_monthly[
                    wsts_trend_monthly.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = wsts_trend_monthly
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No semiconductor monthly trend data available.")
    # Semiconductor YoY Monthly Data
    if not wsts_yoy_monthly.empty:
        with st.expander("🔌 Semiconductor YoY Monthly Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="wsts_yoy_monthly"):
                    csv = wsts_yoy_monthly.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"wsts_yoy_monthly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search regions:", placeholder="Enter region name...", key="search_wsts_yoy_monthly")
            if search_term:
                filtered_data = wsts_yoy_monthly[
                    wsts_yoy_monthly.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = wsts_yoy_monthly
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No semiconductor YoY monthly data available.")
    # Semiconductor Market Share Data
    if not wsts_market_share_monthly.empty:
        with st.expander("🔌 Semiconductor Market Share Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="wsts_market_share_monthly"):
                    csv = wsts_market_share_monthly.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"wsts_market_share_monthly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search regions:", placeholder="Enter region name...", key="search_wsts_market_share_monthly")
            if search_term:
                filtered_data = wsts_market_share_monthly[
                    wsts_market_share_monthly.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = wsts_market_share_monthly
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No semiconductor market share data available.")

with tab6:
    if not trade_balance.empty:
        with st.expander("⚖️ Trade Balance Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                if st.button("📥 Export Data", type="primary", key="trade_balance"):
                    csv = trade_balance.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"trade_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_trade_balance")
            if search_term:
                filtered_data = trade_balance[
                    trade_balance.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = trade_balance
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No trade balance data available.")



# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🇰🇷 Korea Trade Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> Korea Customs Service, World Semiconductor Trade Statistics | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive Korea trade analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True) 