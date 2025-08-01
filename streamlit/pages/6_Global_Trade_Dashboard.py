import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
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
        height: 180px;
        min-width: 150px;
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
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        word-wrap: break-word;
        max-width: 100%;
        line-height: 1.3;
        overflow-wrap: break-word;
        hyphens: auto;
        padding: 0 0.5rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #6c757d;
        font-weight: 400;
        margin-top: 0.5rem;
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
    # Truncate long values for better display
    if isinstance(value, str) and len(value) > 40:
        value = value[:37] + "..."
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """

def format_currency(value):
    """Format currency values with appropriate units"""
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.0f}"

def truncate_text(text, max_length=35):
    """Truncate text to fit in metric cards"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def truncate_chart_labels(text, max_length=30):
    """Truncate text for chart labels"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def apply_chart_styling(fig, title_color="#1e3c72"):
    fig.update_layout(
        title_font_size=18,
        title_font_color=title_color,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=120),  # Increased bottom margin
        height=550  # Increased height
    )
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        tickangle=-30,  # Reduced rotation angle
        tickfont=dict(size=12)  # Increased font size
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        tickfont=dict(size=12)
    )
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

def detect_global_trade_signals(export_decrease_data, export_increase_data, export_countries_data, trade_partners_data, shipping_volatility_data):
    """Detect market signals specific to global trade sector"""
    signals = []
    
    # Signal 1: Export decline patterns
    if not export_decrease_data.empty:
        avg_decrease = export_decrease_data['yoy_change_percent'].mean()
        if avg_decrease < -20:
            signals.append({
                "signal": "🚨 Significant Export Decline Detected",
                "description": f"Average YoY decline of {abs(avg_decrease):.1f}% across top export decrease items indicates weakening global demand or supply chain disruptions.",
                "implication": "Consider diversifying export markets, exploring new product categories, or strengthening supply chain resilience to mitigate trade risks.",
                "confidence": "High",
                "type": "bearish"
            })
        elif avg_decrease < -10:
            signals.append({
                "signal": "⚠️ Moderate Export Decline Warning",
                "description": f"Average YoY decline of {abs(avg_decrease):.1f}% suggests some trade headwinds that require monitoring.",
                "implication": "Monitor trade partner relationships and consider hedging strategies for export-dependent businesses.",
                "confidence": "Medium",
                "type": "warning"
            })
    
    # Signal 2: Export growth opportunities
    if not export_increase_data.empty:
        avg_increase = export_increase_data['yoy_change_percent'].mean()
        if avg_increase > 30:
            signals.append({
                "signal": "📈 Strong Export Growth Momentum",
                "description": f"Average YoY growth of {avg_increase:.1f}% across top export increase items indicates robust global demand.",
                "implication": "Opportunity to expand production capacity and explore new markets for high-growth commodities.",
                "confidence": "High",
                "type": "bullish"
            })
        elif avg_increase > 15:
            signals.append({
                "signal": "🟢 Positive Export Growth Trend",
                "description": f"Average YoY growth of {avg_increase:.1f}% shows healthy trade expansion in key sectors.",
                "implication": "Consider increasing investment in growing export categories and strengthening trade partnerships.",
                "confidence": "Medium",
                "type": "bullish"
            })
    
    # Signal 3: Geographic trade concentration
    if not export_countries_data.empty:
        # Check for geographic concentration risk
        top_country = export_countries_data.iloc[0]
        if top_country['yoy_change_percent'] > 50:
            signals.append({
                "signal": "🌍 Geographic Trade Concentration Risk",
                "description": f"Excessive growth in {top_country['country']} exports ({top_country['yoy_change_percent']:.1f}% YoY) may indicate over-dependency on single market.",
                "implication": "Diversify trade partnerships to reduce geographic concentration risk and enhance trade resilience.",
                "confidence": "Medium",
                "type": "warning"
            })
    
    # Signal 4: Shipping volatility impact
    if not shipping_volatility_data.empty:
        current_vol = shipping_volatility_data['value'].iloc[-1]
        avg_vol = shipping_volatility_data['value'].mean()
        
        if current_vol > avg_vol * 1.5:
            signals.append({
                "signal": "🚢 High Shipping Volatility Alert",
                "description": f"Current shipping volatility ({current_vol:.1f}) is {((current_vol/avg_vol)-1)*100:.0f}% above average, indicating supply chain instability.",
                "implication": "Expect increased shipping costs and delivery delays. Consider alternative logistics routes and buffer inventory levels.",
                "confidence": "High",
                "type": "bearish"
            })
        elif current_vol < avg_vol * 0.7:
            signals.append({
                "signal": "⚓ Stable Shipping Conditions",
                "description": f"Current shipping volatility ({current_vol:.1f}) is {((1-current_vol/avg_vol)*100):.0f}% below average, indicating stable logistics environment.",
                "implication": "Favorable conditions for trade expansion and cost-effective shipping operations.",
                "confidence": "Medium",
                "type": "bullish"
            })
    
    # Signal 5: Trade partner value concentration
    if not trade_partners_data.empty:
        top_partner_value = trade_partners_data.iloc[0]['export_value_thousand_usd']
        total_value = trade_partners_data['export_value_thousand_usd'].sum()
        concentration = (top_partner_value / total_value) * 100
        
        if concentration > 40:
            signals.append({
                "signal": "🤝 Trade Partner Concentration Risk",
                "description": f"Top trade partner accounts for {concentration:.1f}% of total export value, indicating high dependency risk.",
                "implication": "Diversify trade partnerships to reduce dependency on single partner and enhance trade security.",
                "confidence": "High",
                "type": "warning"
            })
    
    return signals

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

# Create sections dictionary after data is loaded
sections = {
    "Insight": extract_section(gemini_insight, "### Top 1 actionable insight", "### Key risks"),
    "Main Risk": extract_section(gemini_insight, "### Key risks", "### Recommended actions"),
    "Strategic Recommendations": extract_section(gemini_insight, "### Recommended actions", "### Core Trend"),
}
# Executive Summary Header
st.markdown('<div class="section-header" style="margin-bottom: 1rem;"><h2>🌍 Executive Summary: Global Trade Trends</h2></div>', unsafe_allow_html=True)

# Three-column Insight Cards
col1, col2, col3 = st.columns(3)

with col1:
    if sections["Insight"]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #66bb6a 0%, #83c5be 100%); padding: 1.5rem; border-radius: 10px; color: white; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0;">💡 Actionable Insight</h4>
                <p style="margin: 0; line-height: 1.5;">{}</p>
            </div>
        </div>
        """.format(sections["Insight"]), unsafe_allow_html=True)
    else:
        st.info("No actionable insight available")

with col2:
    if sections["Main Risk"]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffa726 0%, #adb5bd 100%); padding: 1.5rem; border-radius: 10px; color: white; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0;">⚠️ Key Risk</h4>
                <p style="margin: 0; line-height: 1.5;">{}</p>
            </div>
        </div>
        """.format(sections["Main Risk"]), unsafe_allow_html=True)
    else:
        st.info("No risk data available")

with col3:
    if sections["Strategic Recommendations"]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #90caf9 0%, #a8dadc 100%); padding: 1.5rem; border-radius: 10px; color: white; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="margin: 0 0 1rem 0;">🛠️ Recommendations</h4>
                <p style="margin: 0; line-height: 1.5;">{}</p>
            </div>
        </div>
        """.format(sections["Strategic Recommendations"]), unsafe_allow_html=True)
    else:
        st.info("No recommendations available")


# Spacer between card row and macro summary
st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Unified Macro Summary Box
st.markdown("""
<div style="background: linear-gradient(90deg, #f8f9fa, #e9ecef);
            border-left: 5px solid #1d3557; padding: 1.25rem 1.5rem;
            border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <p style="margin: 0.25rem 0;"><strong>📊 Macro Context:</strong> Global trade flows show dynamic shifts with emerging market demand growth, supply chain rebalancing post-pandemic, and shipping cost volatility creating both opportunities and risks for international commerce. Regional trade partnerships are evolving with shifting geopolitical dynamics and changing consumer preferences.</p>
    <p style="margin: 0.25rem 0;"><strong>🧠 Takeaway:</strong> Monitor export-import patterns for emerging opportunities, diversify trade partnerships to reduce geographic concentration risk, and leverage shipping index trends to optimize logistics costs and supply chain resilience in an increasingly volatile global trade environment.</p>
</div>
""", unsafe_allow_html=True)

# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 Strategic Implications</h2></div>', unsafe_allow_html=True)
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
st.markdown("---")

# Key Metrics with enhanced styling and better text formatting
st.markdown('<div class="section-header"><h2>📊 Key Indicators</h2></div>', unsafe_allow_html=True)
if key_insights and "summary_statistics" in key_insights:
    stats = key_insights["summary_statistics"]
    top5_decrease = stats.get("Top 5 YoY Decrease Items", [])
    top5_increase = stats.get("Top 5 YoY Increase Items", [])
    top5_countries = stats.get("Top 5 Export Increase Countries", [])
    top5_partners = stats.get("Top Trade Partners by Export Value", [])
else:
    top5_decrease = top5_increase = top5_countries = top5_partners = []

# Get volatility metrics
volatility_metrics = {}
if not shipping_index_3m_volatility.empty:
    volatility_data = shipping_index_3m_volatility.dropna()
    if not volatility_data.empty:
        volatility_metrics = {
            "current": volatility_data['value'].iloc[-1],
            "average": volatility_data['value'].mean(),
            "max": volatility_data['value'].max(),
            "min": volatility_data['value'].min()
        }

# First row: 3 cards
col1, col2, col3 = st.columns(3)
with col1:
    decrease_name = truncate_text(top5_decrease[0]["commodity_full_name"], 30) if top5_decrease else "N/A"
    decrease_pct = f"{top5_decrease[0]['yoy_change_percent']:.1f}%" if top5_decrease else ""
    st.markdown(create_metric_card(
        "⬇️ Top Decrease Item",
        decrease_name,
        f"YoY: {decrease_pct}",
        "#dc3545"
    ), unsafe_allow_html=True)

with col2:
    increase_name = truncate_text(top5_increase[0]["commodity_full_name"], 30) if top5_increase else "N/A"
    increase_pct = f"{top5_increase[0]['yoy_change_percent']:.1f}%" if top5_increase else ""
    st.markdown(create_metric_card(
        "⬆️ Top Increase Item",
        increase_name,
        f"YoY: {increase_pct}",
        "#28a745"
    ), unsafe_allow_html=True)

with col3:
    if top5_countries:
        country_pair = f"{top5_countries[0]['country']} → {top5_countries[0]['partner']}"
        country_display = truncate_text(country_pair, 30)
        country_pct = f"{top5_countries[0]['yoy_change_percent']:.1f}%"
    else:
        country_display = "N/A"
        country_pct = ""
    st.markdown(create_metric_card(
        "🌍 Top Increase Country",
        country_display,
        f"YoY: {country_pct}",
        "#007bff"
    ), unsafe_allow_html=True)

# Second row: 3 cards
col4, col5, col6 = st.columns(3)
with col4:
    if top5_partners:
        partner_pair = f"{top5_partners[0]['country']} → {top5_partners[0]['partner']}"
        partner_display = truncate_text(partner_pair, 30)
        export_value = format_currency(top5_partners[0]['export_value_thousand_usd'] * 1000)  # Convert to actual USD
    else:
        partner_display = "N/A"
        export_value = ""
    st.markdown(create_metric_card(
        "🤝 Top Trade Partner",
        partner_display,
        f"Export: {export_value}",
        "#ffc107"
    ), unsafe_allow_html=True)

with col5:
    current_vol = f"{volatility_metrics.get('current', 0):.1f}" if volatility_metrics else "N/A"
    avg_vol = f"Avg: {volatility_metrics.get('average', 0):.1f}" if volatility_metrics else ""
    st.markdown(create_metric_card(
        "📊 Current Volatility",
        current_vol,
        avg_vol,
        "#e74c3c"
    ), unsafe_allow_html=True)

with col6:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(create_metric_card(
        "🕒 Last Update",
        current_time,
        "Data refresh time",
        "#6c757d"
    ), unsafe_allow_html=True)

# Signal Detection
st.markdown('<div class="section-header"><h2>🚨 Global Trade Sector Signals</h2></div>', unsafe_allow_html=True)

# Generate and display global trade-specific signals
signals = detect_global_trade_signals(export_decrease_items_top5, export_increase_items_top5, export_increase_countries_top5, trade_partners_top5, shipping_index_3m_volatility)

if signals:
    for signal in signals:
        if signal["type"] == "bullish":
            signal_color = "#28a745"
            signal_emoji = "🟢"
        elif signal["type"] == "bearish":
            signal_color = "#dc3545"
            signal_emoji = "🔴"
        elif signal["type"] == "warning":
            signal_color = "#ffc107"
            signal_emoji = "🟡"
        else:  # neutral
            signal_color = "#6c757d"
            signal_emoji = "⚪"
        
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: {signal_color};">
            <h4>{signal_emoji} {signal["signal"]}</h4>
            <p><strong>📊 What We See:</strong> {signal["description"]}</p>
            <p><strong>💡 What This Means:</strong> {signal["implication"]}</p>
            <p><strong>🎯 Confidence Level:</strong> {signal["confidence"]}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No significant global trade market signals detected at this time.")

# Top 5 Export Decrease Items
st.markdown('<div class="section-header"><h2>⬇️ Top 5 Export Decrease Items (YoY)</h2></div>', unsafe_allow_html=True)
if not export_decrease_items_top5.empty:
    # Sort by YoY change (ascending - lowest decrease first)
    decrease_data = export_decrease_items_top5.head(5).sort_values('yoy_change_percent', ascending=True)
    
    # Truncate labels for better display
    decrease_data = decrease_data.copy()
    decrease_data['commodity_display'] = decrease_data['commodity_full_name'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 decrease items
    fig_decrease = px.bar(
        decrease_data,
        x='commodity_display',
        y='yoy_change_percent',
        title="Top 5 Export Items with Largest YoY Decrease",
        labels={'commodity_display': 'Commodity', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Reds_r',  # Darker reds for larger decreases
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_decrease.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full commodity names
    fig_decrease.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Commodity: %{customdata}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=decrease_data['commodity_full_name']
    )
    
    fig_decrease = apply_chart_styling(fig_decrease)
    
    # Customize y-axis to show increments of 10
    fig_decrease.update_layout(
        yaxis=dict(
            dtick=10,  # Set tick interval to 10
            tickmode='linear',
            range=[-45, 0]  # Set range from -45 to 0 for better spacing
        )
    )
    
    st.plotly_chart(fig_decrease, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_decrease = decrease_data[['commodity_full_name', 'export_value_thousand_usd', 'yoy_change_percent', 'country']].copy()
    display_decrease['export_value_thousand_usd'] = display_decrease['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_decrease['yoy_change_percent'] = display_decrease['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_decrease.columns = ['Commodity', 'Export Value (USD)', 'YoY Change (%)', 'Country']
    st.dataframe(display_decrease, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Decrease Data Available</h4>
        <p>No export decrease data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Export Increase Items
st.markdown('<div class="section-header"><h2>⬆️ Top 5 Export Increase Items (YoY)</h2></div>', unsafe_allow_html=True)
if not export_increase_items_top5.empty:
    # Sort by YoY change (descending - highest increase first)
    increase_data = export_increase_items_top5.head(5).sort_values('yoy_change_percent', ascending=False)
    
    # Truncate labels for better display
    increase_data = increase_data.copy()
    increase_data['commodity_display'] = increase_data['commodity_full_name'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 increase items
    fig_increase = px.bar(
        increase_data,
        x='commodity_display',
        y='yoy_change_percent',
        title="Top 5 Export Items with Largest YoY Increase",
        labels={'commodity_display': 'Commodity', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Greens',  # Lighter greens for larger increases (reversed)
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_increase.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full commodity names
    fig_increase.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Commodity: %{customdata}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=increase_data['commodity_full_name']
    )
    
    fig_increase = apply_chart_styling(fig_increase)
    st.plotly_chart(fig_increase, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_increase = increase_data[['commodity_full_name', 'export_value_thousand_usd', 'yoy_change_percent', 'country']].copy()
    display_increase['export_value_thousand_usd'] = display_increase['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_increase['yoy_change_percent'] = display_increase['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_increase.columns = ['Commodity', 'Export Value (USD)', 'YoY Change (%)', 'Country']
    st.dataframe(display_increase, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Increase Data Available</h4>
        <p>No export increase data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Export Increase Countries
st.markdown('<div class="section-header"><h2>🌍 Top 5 Export Increase Countries (YoY)</h2></div>', unsafe_allow_html=True)
if not export_increase_countries_top5.empty:
    # Sort by YoY change (descending - highest increase first)
    countries_data = export_increase_countries_top5.head(5).sort_values('yoy_change_percent', ascending=False)
    
    # Truncate labels for better display
    countries_data = countries_data.copy()
    countries_data['country_display'] = countries_data['country'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 increase countries
    fig_countries = px.bar(
        countries_data,
        x='country_display',
        y='yoy_change_percent',
        title="Top 5 Countries with Largest Export YoY Increase",
        labels={'country_display': 'Country', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Oranges',  # Orange scale for better distinction
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_countries.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full country names and partner info
    fig_countries.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Country: %{customdata[0]}<br>' +
                     'Partner: %{customdata[1]}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=list(zip(countries_data['country'], countries_data['partner']))
    )
    
    fig_countries = apply_chart_styling(fig_countries)
    st.plotly_chart(fig_countries, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_countries = export_increase_countries_top5.head(5)[['country', 'partner', 'export_value_thousand_usd', 'yoy_change_percent']].copy()
    display_countries['export_value_thousand_usd'] = display_countries['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_countries['yoy_change_percent'] = display_countries['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_countries.columns = ['Country', 'Trade Partner', 'Export Value (USD)', 'YoY Change (%)']
    st.dataframe(display_countries, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Countries Data Available</h4>
        <p>No export countries data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Trading Partners
st.markdown('<div class="section-header"><h2>🤝 Top 5 Trading Partners by Export Value</h2></div>', unsafe_allow_html=True)
if not trade_partners_top5.empty:
    # Sort by export value (descending - highest value first)
    partners_data = trade_partners_top5.head(5).sort_values('export_value_thousand_usd', ascending=False)
    
    # Create country pair labels
    partners_data = partners_data.copy()
    partners_data['country_pair'] = partners_data['country'] + ' → ' + partners_data['partner']
    
    # Create horizontal bar chart for top 5 trading partners
    fig_partners = px.bar(
        partners_data,
        x='export_value_thousand_usd',
        y='country_pair',
        orientation='h',  # Horizontal orientation
        title="Top 5 Trading Partners by Export Value",
        labels={'export_value_thousand_usd': 'Export Value (USD)', 'country_pair': 'Country Pair'},
        color='export_value_thousand_usd',
        color_continuous_scale='Reds',  # Red scale to highlight importance
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_partners.update_traces(
        textposition='outside',
        texttemplate='$%{x:,.0f}B',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full country names and partner info
    fig_partners.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Country Pair: %{y}<br>' +
                     'Export Value: $%{x:,.0f}B<br>' +
                     '<extra></extra>'
    )
    
    # Custom styling for horizontal chart
    fig_partners.update_layout(
        title_font_size=18,
        title_font_color="#1e3c72",
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
        height=550,
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(size=12),
            tickformat=',.0f',  # Format x-axis ticks with commas
            tickprefix='$',
            ticksuffix='B',
            range=[0, partners_data['export_value_thousand_usd'].max() * 1.1]  # Add 10% padding
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(size=12)
        )
    )
    
    st.plotly_chart(fig_partners, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_partners = trade_partners_top5.head(5)[['country', 'partner', 'export_value_thousand_usd', 'yoy_change_percent']].copy()
    display_partners['export_value_thousand_usd'] = display_partners['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_partners['yoy_change_percent'] = display_partners['yoy_change_percent'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    display_partners.columns = ['Country', 'Trade Partner', 'Export Value (USD)', 'YoY Change (%)']
    st.dataframe(display_partners, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Trading Partners Data Available</h4>
        <p>No trading partners data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Trends - FIXED VERSION
st.markdown('<div class="section-header"><h2>🚢 Shipping Index Trends</h2></div>', unsafe_allow_html=True)
if not shipping_index_pivoted.empty:
    indicators = [col for col in shipping_index_pivoted.columns if col != "date"]
    
    # Check data availability and latest values for each indicator
    data_availability = {}
    for indicator in indicators:
        non_null_count = shipping_index_pivoted[indicator].dropna().shape[0]
        total_count = shipping_index_pivoted.shape[0]
        availability_pct = (non_null_count / total_count) * 100
        
        # Get the latest value for this indicator
        latest_value = shipping_index_pivoted[indicator].dropna().iloc[-1] if non_null_count > 0 else None
        latest_date = shipping_index_pivoted.loc[shipping_index_pivoted[indicator].dropna().index[-1], 'date'] if non_null_count > 0 else None
        
        data_availability[indicator] = {
            'count': non_null_count,
            'percentage': availability_pct,
            'latest_value': latest_value,
            'latest_date': latest_date
        }
    
    # Display latest values info
    st.subheader("📊 Latest Values")
    availability_cols = st.columns(len(indicators))
    for i, indicator in enumerate(indicators):
        with availability_cols[i]:
            if data_availability[indicator]['latest_value'] is not None:
                latest_value = data_availability[indicator]['latest_value']
                latest_date = data_availability[indicator]['latest_date']
                # Format the value based on its magnitude
                if latest_value >= 1000:
                    formatted_value = f"{latest_value:,.0f}"
                else:
                    formatted_value = f"{latest_value:.2f}"
                st.metric(
                    f"{indicator}",
                    formatted_value,
                    f"as of {latest_date.strftime('%Y-%m-%d')}"
                )
            else:
                st.metric(
                    f"{indicator}",
                    "No data",
                    "No available data"
                )
    
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
        
        # Create tabs for different chart views
        tab1, tab2, tab3 = st.tabs(["📈 Relative Change", "📊 Absolute Values", "🔍 Data Points"])
        
        with tab1:
            # Calculate relative changes (percentage change from first available value)
            shipping_relative = shipping_index_pivoted.copy()
            
            fig_relative = go.Figure()
            
            colors = px.colors.qualitative.Set3
            
            for i, indicator in enumerate(indices_to_plot):
                # Get only non-null values
                indicator_data = shipping_relative[[indicator, 'date']].dropna()
                
                if not indicator_data.empty:
                    # Get the first non-null value for this indicator
                    first_value = indicator_data[indicator].iloc[0]
                    
                    # Calculate percentage change from the first value
                    relative_values = ((indicator_data[indicator] - first_value) / first_value) * 100
                    
                    fig_relative.add_trace(go.Scatter(
                        x=indicator_data['date'],
                        y=relative_values,
                        mode='lines+markers',
                        name=indicator,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{indicator}</b><br>' +
                                    'Date: %{x}<br>' +
                                    'Relative Change: %{y:.1f}%<br>' +
                                    '<extra></extra>'
                    ))
            
            # Add horizontal line at 0% for reference
            fig_relative.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig_relative.update_layout(
                title="Shipping Indices Relative Change Over Time",
                xaxis_title="Date",
                yaxis_title="Relative Change (%)",
                template="plotly_white",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_relative, use_container_width=True)
            st.info("📊 **Relative Change**: Shows percentage change from the first available value for each index. A value of 0% represents the starting point, positive values show growth, and negative values show decline.")
        
        with tab2:
            # Show absolute values
            fig_absolute = go.Figure()
            
            for i, indicator in enumerate(indices_to_plot):
                # Get only non-null values
                indicator_data = shipping_index_pivoted[[indicator, 'date']].dropna()
                
                if not indicator_data.empty:
                    fig_absolute.add_trace(go.Scatter(
                        x=indicator_data['date'],
                        y=indicator_data[indicator],
                        mode='lines+markers',
                        name=indicator,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{indicator}</b><br>' +
                                    'Date: %{x}<br>' +
                                    'Value: %{y:.2f}<br>' +
                                    '<extra></extra>'
                    ))
            
            fig_absolute.update_layout(
                title="Shipping Indices Absolute Values Over Time",
                xaxis_title="Date",
                yaxis_title="Index Value",
                template="plotly_white",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_absolute, use_container_width=True)
            st.info("📊 **Absolute Values**: Shows the actual index values without normalization.")
        
        with tab3:
            # Show data points summary
            st.subheader("📋 Data Points Summary")
            
            summary_data = []
            for indicator in indices_to_plot:
                indicator_data = shipping_index_pivoted[[indicator, 'date']].dropna()
                if not indicator_data.empty:
                    summary_data.append({
                        'Index': indicator,
                        'Data Points': len(indicator_data),
                        'First Date': indicator_data['date'].min().strftime('%Y-%m-%d'),
                        'Last Date': indicator_data['date'].max().strftime('%Y-%m-%d'),
                        'Min Value': indicator_data[indicator].min(),
                        'Max Value': indicator_data[indicator].max(),
                        'Latest Value': indicator_data[indicator].iloc[-1],
                        'Data Coverage': f"{(len(indicator_data) / len(shipping_index_pivoted)) * 100:.1f}%"
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.warning("No data available for selected indices.")
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
    
    # Ensure proper color scale range
    if corr_max - corr_min < 0.1:
        corr_min = max(-1, corr_min - 0.1)
        corr_max = min(1, corr_max + 0.1)
    
    # Create enhanced correlation heatmap with annotations
    fig_corr = px.imshow(
        corr_matrix,
        title="Shipping Index Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        template="plotly_white"
    )
    
    # Add correlation values as text annotations
    for i in range(len(corr_matrix.index)):
        for j in range(len(corr_matrix.columns)):
            value = corr_matrix.iloc[i, j]
            if not pd.isna(value):
                # Format the correlation value
                if abs(value) >= 0.8:
                    text_color = 'white'  # High contrast for strong correlations
                else:
                    text_color = 'black'
                
                fig_corr.add_annotation(
                    x=j,
                    y=i,
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(color=text_color, size=10),
                    xanchor='center',
                    yanchor='middle'
                )
    
    # Fix colorbar with proper tick marks
    fig_corr.update_layout(
        coloraxis=dict(
            colorbar=dict(
                tickmode='array',
                tickvals=[-1, -0.5, 0, 0.5, 1],
                ticktext=['-1.0', '-0.5', '0.0', '0.5', '1.0'],
                title="Correlation Coefficient",
                len=0.8,
                thickness=20
            )
        ),
        height=600,
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickangle=0)
    )
    
    fig_corr = apply_chart_styling(fig_corr)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Enhanced correlation insights and summary
    st.markdown("### 📊 Correlation Analysis Summary")
    
    # Find strongest correlations
    corr_pairs = []
    for i in range(len(corr_matrix.index)):
        for j in range(i+1, len(corr_matrix.columns)):
            value = corr_matrix.iloc[i, j]
            if not pd.isna(value):
                corr_pairs.append({
                    'index1': corr_matrix.index[i],
                    'index2': corr_matrix.columns[j],
                    'correlation': value
                })
    
    # Sort by absolute correlation value
    corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    # Display correlation insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔗 Strongest Correlations")
        if corr_pairs:
            for i, pair in enumerate(corr_pairs[:5]):  # Top 5 correlations
                corr_val = pair['correlation']
                strength = "Strong Positive" if corr_val > 0.7 else "Strong Negative" if corr_val < -0.7 else "Moderate Positive" if corr_val > 0.3 else "Moderate Negative" if corr_val < -0.3 else "Weak"
                color = "🟢" if corr_val > 0.7 else "🔴" if corr_val < -0.7 else "🟡"
                st.markdown(f"{color} **{pair['index1']}** ↔ **{pair['index2']}**: {corr_val:.3f} ({strength})")
    
    with col2:
        st.markdown("#### 📈 Correlation Strength Guide")
        st.markdown("""
        - **🟢 Strong Positive (0.7-1.0)**: Indices move together strongly
        - **🟡 Moderate Positive (0.3-0.7)**: Indices tend to move in same direction
        - **⚪ Weak (-0.3 to 0.3)**: Little relationship between indices
        - **🟡 Moderate Negative (-0.7 to -0.3)**: Indices tend to move in opposite directions
        - **🔴 Strong Negative (-1.0 to -0.7)**: Indices move strongly in opposite directions
        """)
    
    # Detailed explanation
    st.markdown("#### 💡 What This Means")
    st.markdown("""
    **Strong Positive Correlations** (red squares with values >0.7) indicate that when one shipping index rises, the other tends to rise as well. 
    This often happens with indices that track similar routes or vessel types.
    
    **Strong Negative Correlations** (blue squares with values <-0.7) suggest that when one index rises, the other tends to fall. 
    This could indicate different market segments or competing routes.
    
    **Weak Correlations** (neutral colors with values between -0.3 and 0.3) suggest that the indices move independently of each other.
    """)
    
    # Correlation statistics
    st.markdown("#### 📊 Correlation Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Correlation", f"{corr_matrix.mean().mean():.3f}")
    with col2:
        st.metric("Strongest Positive", f"{corr_max:.3f}")
    with col3:
        st.metric("Strongest Negative", f"{corr_min:.3f}")
    with col4:
        strong_correlations = ((corr_matrix.abs() > 0.7).sum().sum() - len(corr_matrix)) / 2  # Subtract diagonal
        st.metric("Strong Correlations", f"{strong_correlations:.0f}")
        
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Correlation Data Available</h4>
        <p>No shipping index correlation data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Volatility Analysis
st.markdown('<div class="section-header"><h2>📊 Shipping Index Volatility Analysis</h2></div>', unsafe_allow_html=True)
if not shipping_index_3m_volatility.empty:
    # Clean the data - remove empty rows
    volatility_data = shipping_index_3m_volatility.dropna()
    
    if not volatility_data.empty:
        # Convert date column to datetime if not already
        if 'date' in volatility_data.columns:
            volatility_data['date'] = pd.to_datetime(volatility_data['date'])
            
        # Create volatility trend chart
        fig_vol = px.line(
            volatility_data,
            x="date",
            y="value",
            title="3-Month Rolling Volatility of Shipping Indices",
            labels={"value": "Volatility (Standard Deviation)", "date": "Date"},
            template="plotly_white"
        )
        fig_vol = apply_chart_styling(fig_vol)
        fig_vol.update_traces(line_color='#e74c3c', line_width=3)
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Volatility statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Volatility", f"{volatility_data['value'].iloc[-1]:.1f}")
        with col2:
            st.metric("Average Volatility", f"{volatility_data['value'].mean():.1f}")
        with col3:
            st.metric("Max Volatility", f"{volatility_data['value'].max():.1f}")
        with col4:
            st.metric("Min Volatility", f"{volatility_data['value'].min():.1f}")
        
        # Volatility insights
        current_vol = volatility_data['value'].iloc[-1]
        avg_vol = volatility_data['value'].mean()
        
        if current_vol > avg_vol * 1.2:
            st.warning("⚠️ **High Volatility Alert**: Current volatility is significantly above average, indicating increased market uncertainty.")
        elif current_vol < avg_vol * 0.8:
            st.success("✅ **Low Volatility**: Current volatility is below average, suggesting relative market stability.")
        else:
            st.info("ℹ️ **Normal Volatility**: Current volatility is within normal range.")
            
    else:
        st.markdown("""
        <div class="alert-box">
            <h4>⚠️ No Volatility Data Available</h4>
            <p>No valid volatility data is currently available.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Volatility Data Available</h4>
        <p>No shipping index volatility data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)


# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⬇️ Top 5 Decrease Items", "⬆️ Top 5 Increase Items", "🌍 Top 5 Increase Countries", "🤝 Top 5 Trade Partners", "🚢 Shipping Index", "📊 Volatility Analysis"
])

with tab1:
    if not export_decrease_items_top5.empty:
        with st.expander("📊 Export Decrease Items Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                csv = export_decrease_items_top5.to_csv(index=False)
                st.download_button(
                    label="📥 Export Data",
                    data=csv,
                    file_name=f"export_decrease_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    key="export_decrease_items"
                )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_decrease_items")
            if search_term:
                filtered_data = export_decrease_items_top5[
                    export_decrease_items_top5.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = export_decrease_items_top5
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No data available.")

with tab2:
    if not export_increase_items_top5.empty:
        with st.expander("📈 Export Increase Items Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                csv = export_increase_items_top5.to_csv(index=False)
                st.download_button(
                    label="📥 Export Data",
                    data=csv,
                    file_name=f"export_increase_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    key="export_increase_items"
                )
            search_term = st.text_input("🔍 Search items:", placeholder="Enter item name...", key="search_increase_items")
            if search_term:
                filtered_data = export_increase_items_top5[
                    export_increase_items_top5.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = export_increase_items_top5
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No data available.")

with tab3:
    if not export_increase_countries_top5.empty:
        with st.expander("🌍 Export Increase Countries Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                csv = export_increase_countries_top5.to_csv(index=False)
                st.download_button(
                    label="📥 Export Data",
                    data=csv,
                    file_name=f"export_increase_countries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    key="export_increase_countries"
                )
            search_term = st.text_input("🔍 Search countries:", placeholder="Enter country name...", key="search_increase_countries")
            if search_term:
                filtered_data = export_increase_countries_top5[
                    export_increase_countries_top5.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = export_increase_countries_top5
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No data available.")

with tab4:
    if not trade_partners_top5.empty:
        with st.expander("🤝 Trade Partners Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                csv = trade_partners_top5.to_csv(index=False)
                st.download_button(
                    label="📥 Export Data",
                    data=csv,
                    file_name=f"trade_partners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    key="export_trade_partners"
                )
            search_term = st.text_input("🔍 Search partners:", placeholder="Enter partner name...", key="search_trade_partners")
            if search_term:
                filtered_data = trade_partners_top5[
                    trade_partners_top5.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = trade_partners_top5
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No data available.")

with tab5:
    if not shipping_index_pivoted.empty:
        with st.expander("🚢 Shipping Index Data", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col4:
                csv = shipping_index_pivoted.to_csv(index=False)
                st.download_button(
                    label="📥 Export Data",
                    data=csv,
                    file_name=f"shipping_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    key="export_shipping_index"
                )
            search_term = st.text_input("🔍 Search indices:", placeholder="Enter index name...", key="search_shipping_index")
            if search_term:
                filtered_data = shipping_index_pivoted[
                    shipping_index_pivoted.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                ]
            else:
                filtered_data = shipping_index_pivoted
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("No data available.")

with tab6:
    if not shipping_index_3m_volatility.empty:
        volatility_display = shipping_index_3m_volatility.dropna()
        if not volatility_display.empty:
            with st.expander("📊 Volatility Analysis Data", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    csv = volatility_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Export Data",
                        data=csv,
                        file_name=f"volatility_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="primary",
                        key="export_volatility"
                    )
                search_term = st.text_input("🔍 Search volatility data:", placeholder="Enter search term...", key="search_volatility")
                if search_term:
                    filtered_data = volatility_display[
                        volatility_display.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = volatility_display
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No valid volatility data available.")
    else:
        st.info("No volatility data available.")

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