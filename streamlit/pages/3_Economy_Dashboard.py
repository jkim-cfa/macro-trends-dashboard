import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_economy_data

# Page Config
st.set_page_config(
    page_title="Economy Dashboard",
    page_icon="💹",
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
    <h1>💹 Economy Dashboard</h1>
    <p>Comprehensive analysis of economic indicators, FX rates, sentiment trends, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_economy_data():
    """Load and cache economy data with error handling"""
    try:
        data = load_economy_data()
        return data
    except Exception as e:
        st.error(f"Error loading economy data: {str(e)}")
        return {}

# Helper Functions
def format_dates_for_display(df):
    """Format date columns to show only date without time component"""
    if not df.empty and 'date' in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def extract_section(text, start, end=None):
    """Extract section between start and end markers."""
    if start not in text:
        return ""
    section = text.split(start)[1]
    if end and end in section:
        section = section.split(end)[0]
    return section.strip()

def format_insight_text(text):
    """Clean AI text for better markdown rendering in Streamlit."""
    if not text:
        return ""
    lines = text.strip().split('\n')
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Ensure all bullet points are properly formatted
        if line.startswith("•"):
            # Remove the bullet point and check if it starts with a number
            clean_line = line[1:].strip()
            # Check if the line starts with a number followed by a period (more robust check)
            if clean_line and clean_line[0].isdigit() and len(clean_line) > 1 and clean_line[1] == '.':
                # For numbered items like "1. Supply Chain Disruptions"
                formatted.append(clean_line)
            elif ":" in line:
                # Check if it contains a colon (like "Economy: Record global...")
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted.append(f"**{label}:** {content}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        
        # Handle emoji headers (🛠, 📊, 🎯, ⚠️, 📈, 📉, 🔄) - only if they're standalone headers
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and ':' in line:
            # This is content within a section, not a header - don't bold it
            formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            # This is a standalone header - bold it
            formatted.append(f"\n**{line}**")
        
        # Handle numbered lists (don't add bullet points to them)
        elif line and line[0].isdigit() and len(line) > 1 and line[1] == '.':
            formatted.append(line)
        # Handle other lines that might need bullet points
        elif line and not line.startswith("-"):
            formatted.append(f"• {line}")
        else:
            formatted.append(line)
    
    return "\n\n".join(formatted)

def apply_chart_styling(fig, title_color="#1e3c72"):
    """Apply consistent styling to charts"""
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

def create_metric_card(title, value, subtitle="", color="#007bff"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """

def format_currency(value, currency="₩"):
    """Format large numbers as currency with B/M/K suffixes"""
    if pd.isna(value) or value == 0:
        return "N/A"
    
    if value >= 1e12:
        return f"{currency}{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"{currency}{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{currency}{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{currency}{value/1e3:.2f}K"
    else:
        return f"{currency}{value:,.0f}"

# Load Data
with st.spinner("Loading economy intelligence data..."):
    data = load_cached_economy_data()

# Extract data with error handling - keep sentiment data completely separate
sentiment_raw = format_dates_for_display(data.get("sentiment_raw", pd.DataFrame()))
sentiment_processed = format_dates_for_display(data.get("sentiment_processed", pd.DataFrame()))

# Other data that can be filtered
fx_raw = format_dates_for_display(data.get("fx_raw", pd.DataFrame()))
economic_indicators_raw = format_dates_for_display(data.get("economic_indicators_raw", pd.DataFrame()))
key_indicators_processed = format_dates_for_display(data.get("key_indicators_processed", pd.DataFrame()))
cross_correlations = data.get("cross_correlations", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Get latest USD/KRW rate from FX data
usd_krw_latest = None
if not fx_raw.empty and 'pair' in fx_raw.columns and 'exchange_rate' in fx_raw.columns:
    usd_krw_data = fx_raw[fx_raw['pair'] == 'USD/KRW']
    if not usd_krw_data.empty:
        usd_krw_latest = usd_krw_data['exchange_rate'].iloc[-1]

# Create combined analysis dataframe for filtering (only from economic indicators, not sentiment)
combined_analysis = pd.DataFrame()
if not economic_indicators_raw.empty:
    combined_analysis = economic_indicators_raw.copy()

# Store original data for filtering
original_fx_raw = fx_raw.copy()
original_economic_indicators_raw = economic_indicators_raw.copy()
original_key_indicators_processed = key_indicators_processed.copy()

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter
if not combined_analysis.empty and 'date' in combined_analysis.columns:
    try:
        min_date = pd.to_datetime(combined_analysis['date']).min()
        max_date = pd.to_datetime(combined_analysis['date']).max()
        
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Apply date filter to all relevant datasets except sentiment
            combined_analysis = combined_analysis[
                (pd.to_datetime(combined_analysis['date']).dt.date >= start_date) &
                (pd.to_datetime(combined_analysis['date']).dt.date <= end_date)
            ]
            
            # Filter FX data
            if not fx_raw.empty and 'date' in fx_raw.columns:
                fx_raw = fx_raw[
                    (pd.to_datetime(fx_raw['date']).dt.date >= start_date) &
                    (pd.to_datetime(fx_raw['date']).dt.date <= end_date)
                ]
            
            # Filter economic indicators
            if not economic_indicators_raw.empty and 'date' in economic_indicators_raw.columns:
                economic_indicators_raw = economic_indicators_raw[
                    (pd.to_datetime(economic_indicators_raw['date']).dt.date >= start_date) &
                    (pd.to_datetime(economic_indicators_raw['date']).dt.date <= end_date)
                ]
            
            # Filter sentiment data
            if not sentiment_raw.empty and 'date' in sentiment_raw.columns:
                sentiment_raw = sentiment_raw[
                    (pd.to_datetime(sentiment_raw['date']).dt.date >= start_date) &
                    (pd.to_datetime(sentiment_raw['date']).dt.date <= end_date)
                ]
            
            # Filter processed sentiment data
            if not sentiment_processed.empty and 'date' in sentiment_processed.columns:
                sentiment_processed = sentiment_processed[
                    (pd.to_datetime(sentiment_processed['date']).dt.date >= start_date) &
                    (pd.to_datetime(sentiment_processed['date']).dt.date <= end_date)
                ]
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Indicator filter (only for economic indicators, not sentiment)
if not combined_analysis.empty and 'indicator' in combined_analysis.columns:
    st.sidebar.markdown("### 📊 Economic Indicator Filter")
    all_indicators = list(combined_analysis['indicator'].unique())
    select_all_label = "Select All"
    multiselect_options = [select_all_label] + all_indicators

    # Default selection - only "Select All" is selected by default
    default_selection = [select_all_label]

    selected = st.sidebar.multiselect(
        "Select economic indicators:",
        options=multiselect_options,
        default=default_selection,
        key="indicator_multiselect"
    )

    if select_all_label in selected:
        selected_indicators = all_indicators
    else:
        selected_indicators = [c for c in selected if c in all_indicators]

    if selected_indicators:
        # Apply indicator filter to economic indicators only
        combined_analysis = combined_analysis[combined_analysis['indicator'].isin(selected_indicators)]
        
        # Filter economic indicators
        if not economic_indicators_raw.empty and 'indicator' in economic_indicators_raw.columns:
            economic_indicators_raw = economic_indicators_raw[economic_indicators_raw['indicator'].isin(selected_indicators)]

# Currency pair filter for FX data
if not fx_raw.empty and 'pair' in fx_raw.columns:
    st.sidebar.markdown("### 💱 Currency Pair Filter")
    all_pairs = list(fx_raw['pair'].unique())
    select_all_pairs_label = "Select All Pairs"
    pair_options = [select_all_pairs_label] + all_pairs

    selected_pairs = st.sidebar.multiselect(
        "Select currency pairs:",
        options=pair_options,
        default=[select_all_pairs_label],
        key="pair_multiselect"
    )

    if select_all_pairs_label in selected_pairs:
        selected_currency_pairs = all_pairs
    else:
        selected_currency_pairs = [p for p in selected_pairs if p in all_pairs]

    if selected_currency_pairs:
        fx_raw = fx_raw[fx_raw['pair'].isin(selected_currency_pairs)]

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []

# Check date filter
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")

# Check indicator filter
if 'selected_indicators' in locals() and selected_indicators:
    if len(selected_indicators) == len(all_indicators):
        active_filters.append(f"Economic Indicators: All ({len(selected_indicators)})")
    else:
        active_filters.append(f"Economic Indicators: {len(selected_indicators)} selected")

# Check currency pair filter
if 'selected_currency_pairs' in locals() and selected_currency_pairs:
    if len(selected_currency_pairs) == len(all_pairs):
        active_filters.append(f"Currency Pairs: All ({len(selected_currency_pairs)})")
    else:
        active_filters.append(f"Currency Pairs: {len(selected_currency_pairs)} selected")

if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Economic Indicators</h2></div>', unsafe_allow_html=True)

# Dynamically calculate metrics from key insights
if key_insights and "market_indicators" in key_insights:
    market_data = key_insights["market_indicators"]
    
    # KOSPI
    kospi_latest = market_data.get("kospi", {}).get("latest", "N/A")
    kospi_trend = market_data.get("kospi", {}).get("trend_3m", "N/A")
    
    # Leading Index
    leading_latest = market_data.get("leading_index", {}).get("latest", "N/A")
    leading_trend = market_data.get("leading_index", {}).get("trend_3m", "N/A")
    
    # Coincident Index
    coincident_latest = market_data.get("coincident_index", {}).get("latest", "N/A")
    coincident_trend = market_data.get("coincident_index", {}).get("trend_3m", "N/A")
    
    # Leading-Coincident Spread
    spread_avg = market_data.get("leading_coincident_spread", {}).get("average", "N/A")
    spread_latest = market_data.get("leading_coincident_spread", {}).get("latest", "N/A")
    
else:
    kospi_latest = kospi_trend = leading_latest = leading_trend = coincident_latest = coincident_trend = "N/A"
    spread_avg = spread_latest = "N/A"

# Get last date from available data
last_date = "N/A"
if not economic_indicators_raw.empty and 'date' in economic_indicators_raw.columns:
    try:
        last_date = pd.to_datetime(economic_indicators_raw['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"
elif not fx_raw.empty and 'date' in fx_raw.columns:
    try:
        last_date = pd.to_datetime(fx_raw['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"
elif not sentiment_raw.empty and 'date' in sentiment_raw.columns:
    try:
        last_date = pd.to_datetime(sentiment_raw['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_metric_card(
        "📈 KOSPI",
        f"{kospi_latest:,.0f}" if isinstance(kospi_latest, (int, float)) else str(kospi_latest),
        f"Trend: {kospi_trend:.1f}%" if isinstance(kospi_trend, (int, float)) else "Trend: N/A",
        "#28a745" if isinstance(kospi_trend, (int, float)) and kospi_trend > 0 else "#dc3545"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card(
        "🎯 Leading Index",
        f"{leading_latest:.1f}" if isinstance(leading_latest, (int, float)) else str(leading_latest),
        f"Trend: {leading_trend:.1f}%" if isinstance(leading_trend, (int, float)) else "Trend: N/A",
        "#007bff"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card(
        "📊 Coincident Index",
        f"{coincident_latest:.1f}" if isinstance(coincident_latest, (int, float)) else str(coincident_latest),
        f"Trend: {coincident_trend:.1f}%" if isinstance(coincident_trend, (int, float)) else "Trend: N/A",
        "#ffc107"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card(
        "💱 USD/KRW",
        f"{usd_krw_latest:,.2f}" if isinstance(usd_krw_latest, (int, float)) else str(usd_krw_latest),
        "Exchange Rate",
        "#6f42c1"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(create_metric_card(
        "📅 Last Update",
        last_date,
        "Most recent data",
        "#17a2b8"
    ), unsafe_allow_html=True)

# Economic Indicators Trends
st.markdown('<div class="section-header"><h2>📈 Economic Indicators Trends</h2></div>', unsafe_allow_html=True)

if not economic_indicators_raw.empty and 'indicator' in economic_indicators_raw.columns:
    # Pivot data for plotting
    pivot_data = economic_indicators_raw.pivot(index='date', columns='indicator', values='value')
    
    if not pivot_data.empty:
        # Add "All Indicators" option
        all_indicator_options = ["All Indicators"] + list(pivot_data.columns)
        
        # Default selection - only the three main indicators
        default_indicators = ['KOSPI', 'Leading Index', 'Coincident Index']
        default_selection = [ind for ind in default_indicators if ind in pivot_data.columns]
        
        selected_trend_indicators = st.multiselect(
            "Select indicators for trend analysis:",
            options=all_indicator_options,
            default=default_selection
        )
        
        if selected_trend_indicators:
            if "All Indicators" in selected_trend_indicators:
                indicators_to_plot = list(pivot_data.columns)
            else:
                indicators_to_plot = selected_trend_indicators
            
            # Enhanced line chart with secondary y-axis for KOSPI
            fig_trend = go.Figure()
            
            # Define colors for indicators
            colors = px.colors.qualitative.Set3
            
            for i, indicator in enumerate(indicators_to_plot):
                if indicator == 'KOSPI':
                    # KOSPI on secondary y-axis
                    fig_trend.add_trace(
                        go.Scatter(
                            x=pivot_data.index,
                            y=pivot_data[indicator],
                            mode='lines',
                            name=f'{indicator} (Right)',
                            line=dict(color=colors[i % len(colors)], width=2),
                            yaxis='y2'
                        )
                    )
                else:
                    # Other indicators on primary y-axis
                    fig_trend.add_trace(
                        go.Scatter(
                            x=pivot_data.index,
                            y=pivot_data[indicator],
                            mode='lines',
                            name=indicator,
                            line=dict(color=colors[i % len(colors)], width=2)
                        )
                    )
            
            # Update layout with dual y-axes
            fig_trend.update_layout(
                title="Economic Indicators Over Time",
                xaxis_title="Date",
                yaxis_title="Index Value (Left)",
                yaxis2=dict(
                    title="KOSPI Value (Right)",
                    overlaying="y",
                    side="right",
                    showgrid=False
                ),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                template="plotly_white",
                title_font_size=18,
                title_font_color="#1e3c72",
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                margin=dict(l=50, r=80, t=80, b=50),
                height=400
            )
            
            # Apply grid styling
            fig_trend.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Separate chart for Leading-Coincident Spread
            if 'Leading–Coincident Spread' in pivot_data.columns:
                st.subheader("📊 Leading-Coincident Spread Analysis")
                
                # Create dedicated chart for the spread
                fig_spread = go.Figure()
                
                fig_spread.add_trace(
                    go.Scatter(
                        x=pivot_data.index,
                        y=pivot_data['Leading–Coincident Spread'],
                        mode='lines+markers',
                        name='Leading–Coincident Spread',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=6, color='#e74c3c'),
                        fill='tonexty',
                        fillcolor='rgba(231, 76, 60, 0.1)'
                    )
                )
                
                # Add zero line for reference
                fig_spread.add_hline(
                    y=0, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text="Zero Line (Neutral)",
                    annotation_position="bottom right"
                )
                
                fig_spread.update_layout(
                    title="Leading-Coincident Spread Over Time",
                    xaxis_title="Date",
                    yaxis_title="Spread Value",
                    template="plotly_white",
                    title_font_size=16,
                    title_font_color="#1e3c72",
                    xaxis_title_font_size=12,
                    yaxis_title_font_size=12,
                    margin=dict(l=50, r=50, t=80, b=50),
                    height=350,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                fig_spread.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
                fig_spread.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
                
                st.plotly_chart(fig_spread, use_container_width=True)
                
                # Spread statistics
                spread_data = pivot_data['Leading–Coincident Spread'].dropna()
                if not spread_data.empty:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Spread", f"{spread_data.iloc[-1]:.2f}")
                    with col2:
                        st.metric("Average Spread", f"{spread_data.mean():.2f}")
                    with col3:
                        st.metric("Min Spread", f"{spread_data.min():.2f}")
                    with col4:
                        st.metric("Max Spread", f"{spread_data.max():.2f}")
                    
                    # Spread interpretation
                    current_spread = spread_data.iloc[-1]
                    if current_spread > 0:
                        st.success("📈 **Positive Spread**: Leading indicators are above coincident indicators, suggesting economic expansion ahead.")
                    elif current_spread < 0:
                        st.warning("📉 **Negative Spread**: Leading indicators are below coincident indicators, suggesting potential economic slowdown.")
                    else:
                        st.info("➡️ **Neutral Spread**: Leading and coincident indicators are aligned.")
        else:
            st.warning("Please select at least one indicator to view trends.")
    else:
        st.markdown("""
        <div class="alert-box">
            <h4>⚠️ No Trend Data Available</h4>
            <p>No economic indicator trend data is currently available.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Economic Indicators Data Available</h4>
        <p>No economic indicators data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# FX Rates Analysis
st.markdown('<div class="section-header"><h2>💱 Foreign Exchange Analysis</h2></div>', unsafe_allow_html=True)

if not fx_raw.empty and 'pair' in fx_raw.columns:
    # Normalize FX rates for better comparison
    fx_norm = fx_raw.copy()
    fx_norm['normalized'] = fx_norm.groupby('pair')['exchange_rate'].transform(lambda x: x / x.iloc[0])
    
    # FX rates over time (normalized)
    fig_fx = px.line(
        fx_norm,
        x="date",
        y="normalized",
        color="pair",
        title="Normalized Foreign Exchange Rates (Relative to First Value)",
        labels={"normalized": "Normalized Exchange Rate", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    
    fig_fx = apply_chart_styling(fig_fx)
    st.plotly_chart(fig_fx, use_container_width=True)
    
    # FX statistics
    if len(fx_raw['pair'].unique()) > 1:
        st.subheader("📊 FX Statistics by Currency Pair")
        fx_stats = fx_raw.groupby('pair')['exchange_rate'].agg(['mean', 'std', 'min', 'max']).round(4)
        fx_stats.columns = ['Average Rate', 'Std Dev', 'Min Rate', 'Max Rate']
        st.dataframe(fx_stats, use_container_width=True)
        
        # Latest FX rates
        st.subheader("📈 Latest Exchange Rates")
        latest_fx = fx_raw.groupby('pair')['exchange_rate'].last().round(4)
        latest_fx_df = pd.DataFrame({
            'Currency Pair': latest_fx.index,
            'Latest Rate': latest_fx.values
        })
        st.dataframe(latest_fx_df, use_container_width=True)
        
        # FX Volatility Analysis from insights
        if key_insights and "fx_analysis" in key_insights:
            fx_analysis = key_insights["fx_analysis"]
            volatility_data = fx_analysis.get("volatility_data", [])
            
            if volatility_data:
                st.subheader("📊 FX Volatility Analysis")
                volatility_df = pd.DataFrame(volatility_data)
                
                # Display 3M and 12M volatility comparison
                if not volatility_df.empty:
                    # Pivot to show 3M vs 12M volatility
                    volatility_pivot = volatility_df.pivot(index='pair', columns='indicator', values='value')
                    volatility_pivot = volatility_pivot.round(3)
                    volatility_pivot.columns = [col.replace(' Volatility (3M)', ' (3M)').replace(' Volatility (12M)', ' (12M)') for col in volatility_pivot.columns]
                    
                    st.dataframe(volatility_pivot, use_container_width=True)
                    
                    # Volatility insights
                    st.info("💡 **Volatility Insights**: Higher 3M volatility compared to 12M suggests recent increase in currency market uncertainty.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No FX Data Available</h4>
        <p>No foreign exchange data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Sentiment Analysis - Completely isolated from filtering
st.markdown('<div class="section-header"><h2>😊 Economic Sentiment Analysis</h2></div>', unsafe_allow_html=True)

if not sentiment_raw.empty and 'indicator' in sentiment_raw.columns:
    # Display latest sentiment data from insights
    if key_insights and "sentiment_analysis" in key_insights:
        sentiment_data = key_insights["sentiment_analysis"]
        latest_sentiment = sentiment_data.get("latest_sentiment", {})
        
        if latest_sentiment:
            st.subheader("📊 Latest Sentiment Indicators")
            col1, col2, col3 = st.columns(3)
            
            for i, (indicator, value) in enumerate(latest_sentiment.items()):
                with [col1, col2, col3][i]:
                    st.metric(
                        indicator,
                        f"{value:.1f}" if isinstance(value, (int, float)) else str(value),
                        help=f"Latest value for {indicator}"
                    )
    
    # Sentiment trends
    fig_sentiment = px.line(
        sentiment_raw,
        x="date",
        y="value",
        color="indicator",
        title="Economic Sentiment Indicators Over Time",
        labels={"value": "Sentiment Index", "date": "Date"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    
    fig_sentiment = apply_chart_styling(fig_sentiment)
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Sentiment statistics
    if len(sentiment_raw['indicator'].unique()) > 1:
        st.subheader("📊 Sentiment Statistics by Indicator")
        sentiment_stats = sentiment_raw.groupby('indicator')['value'].agg(['mean', 'std', 'min', 'max']).round(2)
        sentiment_stats.columns = ['Average Index', 'Std Dev', 'Min Index', 'Max Index']
        st.dataframe(sentiment_stats, use_container_width=True)
    
    # Processed sentiment data
    if not sentiment_processed.empty and 'sentiment_strength' in sentiment_processed.columns:
        st.subheader("📊 Sentiment Strength Analysis")
        
        # Sentiment strength distribution
        strength_counts = sentiment_processed['sentiment_strength'].value_counts()
        fig_strength = px.bar(
            x=strength_counts.index,
            y=strength_counts.values,
            title="Sentiment Strength Distribution",
            labels={"x": "Sentiment Strength", "y": "Count"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            text=strength_counts.values
        )
        fig_strength.update_traces(
            textposition='auto',
            textfont_size=12,
            textfont_color='black',
        )
        fig_strength = apply_chart_styling(fig_strength)
        st.plotly_chart(fig_strength, use_container_width=True)
        
        # Latest sentiment strength by indicator
        latest_sentiment_strength = sentiment_processed.groupby('indicator')['sentiment_strength'].last()
        st.subheader("📈 Latest Sentiment Strength by Indicator")
        st.dataframe(latest_sentiment_strength.reset_index(), use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Sentiment Data Available</h4>
        <p>No economic sentiment data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Correlation Analysis
st.markdown('<div class="section-header"><h2>🔗 Cross-Asset Correlation Analysis</h2></div>', unsafe_allow_html=True)

if not cross_correlations.empty:
    # Correlation heatmap
    correlation_matrix = cross_correlations.pivot(index='indicator_1', columns='indicator_2', values='correlation')
    
    if not correlation_matrix.empty:
        # Calculate dynamic color scale
        corr_min = correlation_matrix.min().min()
        corr_max = correlation_matrix.max().max()
        
        # Ensure we have a reasonable range for visualization
        if corr_max - corr_min < 0.1:
            corr_min = max(-1, corr_min - 0.1)
            corr_max = min(1, corr_max + 0.1)
        
        fig_corr = px.imshow(
            correlation_matrix.round(2),
            title="Cross-Asset Correlation Matrix",
            color_continuous_scale="RdBu_r",
            zmin=corr_min,
            zmax=corr_max,
            aspect="auto",
            template="plotly_white",
            text_auto=True
        )
        
        fig_corr = apply_chart_styling(fig_corr)
        fig_corr.update_layout(height=500)
        fig_corr.update_xaxes(tickangle=-45)
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Correlation insights
        st.info(f"💡 **Correlation Insights**: Values range from {corr_min:.2f} to {corr_max:.2f}. Values closer to {corr_max:.2f} indicate strong positive correlation, while values closer to {corr_min:.2f} indicate strong negative correlation.")
        
        # Correlation statistics
        st.subheader("📊 Correlation Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Correlation", f"{correlation_matrix.mean().mean():.3f}")
        with col2:
            st.metric("Min Correlation", f"{corr_min:.3f}")
        with col3:
            st.metric("Max Correlation", f"{corr_max:.3f}")
        
        # Detailed correlation table
        st.subheader("📋 Detailed Correlation Results")
        st.dataframe(cross_correlations, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Correlation Data Available</h4>
        <p>No correlation analysis data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)

if gemini_insight and gemini_insight != "No AI insights found.":
    # Extract sections
    sections = {
        "Core Trend": extract_section(gemini_insight, "### Core Trend", "### Hidden Effects"),
        "Hidden Effects": extract_section(gemini_insight, "### Hidden Effects", "### Strategic Recommendations"),
        "Strategic Recommendations": extract_section(gemini_insight, "### Strategic Recommendations", "### Risk Assessment"),
        "Risk Assessment": extract_section(gemini_insight, "### Risk Assessment", "### Market Intelligence"),
        "Market Intelligence": extract_section(gemini_insight, "### Market Intelligence")
    }

    # Create tabs with enhanced styling
    tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
    tabs = st.tabs(tab_labels)

    for tab, (label, content) in zip(tabs, sections.items()):
        with tab:
            if content:
                st.markdown(f"### {label}")
                st.markdown(format_insight_text(content))
            else:
                st.info(f"No {label} insights available.")
    
    # Summary metrics
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

# Data Quality Overview
st.markdown('<div class="section-header"><h2>📊 Data Quality Overview</h2></div>', unsafe_allow_html=True)

if key_insights and "data_quality" in key_insights:
    data_quality = key_insights["data_quality"]
    
    col1, col2, col3 = st.columns([1.2, 1, 1])

    
    with col1:
        st.subheader("📈 Economic Indicators")
        eco_data = data_quality.get("economic_indicators", {})
        st.metric("Total Records", f"{eco_data.get('total_records', 0):,}")
        
        # Date Range with consistent font size
        earliest_date = eco_data.get('date_range', {}).get('earliest', 'N/A')
        latest_date = eco_data.get('date_range', {}).get('latest', 'N/A')
        st.metric("Unique Indicators", eco_data.get('unique_indicators', 0))
        
        # Use full date format
        if earliest_date != 'N/A' and latest_date != 'N/A':
            date_range_display = f"{earliest_date} to {latest_date}"
        else:
            date_range_display = f"{earliest_date} to {latest_date}"
        
        st.metric("Date Range", date_range_display)
        
    with col2:
        st.subheader("💱 FX Data")
        fx_data = data_quality.get("fx_data", {})
        st.metric("Total Records", f"{fx_data.get('total_records', 0):,}")
        st.metric("Currency Pairs", fx_data.get('currency_pairs', 0))
    
    with col3:
        st.subheader("😊 Sentiment Data")
        sent_data = data_quality.get("sentiment_data", {})
        st.metric("Total Records", f"{sent_data.get('total_records', 0):,}")
        st.metric("Unique Indicators", sent_data.get('unique_indicators', 0))

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)

# Create tabs for different data types
if not economic_indicators_raw.empty or not fx_raw.empty or not sentiment_raw.empty:
    tab1, tab2, tab3 = st.tabs(["📊 Economic Indicators", "💱 FX Data", "😊 Sentiment Data"])
    
    with tab1:
        if not economic_indicators_raw.empty:
            with st.expander("📊 Economic Indicators Data", expanded=False):
                # Export functionality
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_economic"):
                        csv = economic_indicators_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"economic_indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                # Search functionality
                search_term = st.text_input("🔍 Search indicators:", placeholder="Enter indicator name...", key="search_economic")
                
                if search_term:
                    filtered_data = economic_indicators_raw[
                        economic_indicators_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = economic_indicators_raw
                
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No economic indicators data available.")
    
    with tab2:
        if not fx_raw.empty:
            with st.expander("💱 FX Data", expanded=False):
                # Export functionality
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_fx"):
                        csv = fx_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"fx_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                # Search functionality
                search_term = st.text_input("🔍 Search currency pairs:", placeholder="Enter currency pair...", key="search_fx")
                
                if search_term:
                    filtered_data = fx_raw[
                        fx_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = fx_raw
                
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No FX data available.")
    
    with tab3:
        if not sentiment_raw.empty:
            with st.expander("😊 Sentiment Data", expanded=False):
                # Export functionality
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col4:
                    if st.button("📥 Export Data", type="primary", key="export_sentiment"):
                        csv = sentiment_raw.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"sentiment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                # Search functionality
                search_term = st.text_input("🔍 Search sentiment indicators:", placeholder="Enter indicator name...", key="search_sentiment")
                
                if search_term:
                    filtered_data = sentiment_raw[
                        sentiment_raw.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    ]
                else:
                    filtered_data = sentiment_raw
                
                st.dataframe(filtered_data, use_container_width=True)
        else:
            st.info("No sentiment data available.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Data Available</h4>
        <p>No economy data is currently available for exploration.</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")

# Get the latest data date from the insights
latest_data_date = "N/A"
if key_insights and "data_quality" in key_insights:
    eco_data = key_insights["data_quality"].get("economic_indicators", {})
    latest_data_date = eco_data.get("date_range", {}).get("latest", "N/A")

st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>💹 Economy Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> Bank of Korea (ECOS) | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive economic analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Data last updated: {} | Dashboard last updated: {}</p>
</div>
""".format(latest_data_date, datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)