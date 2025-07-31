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
from utils.data_loader import load_defence_data

# Page Config
st.set_page_config(
    page_title="Defence Procurement Dashboard",
    page_icon="🛡️",
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
    <h1>🛡️ Defence Procurement Intelligence Dashboard</h1>
    <p>Advanced analytics and strategic insights for defence contract analysis</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_defence_data():
    """Load and cache defence data with error handling"""
    try:
        data = load_defence_data()
        return data
    except Exception as e:
        st.error(f"Error loading defence data: {str(e)}")
        return {}

# Helper Functions
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

def format_date_range(start_date, end_date):
    """Format date range for display"""
    if pd.isna(start_date) or pd.isna(end_date):
        return "N/A"
    return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

def create_metric_card(title, value, subtitle="", color="#007bff"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """

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

def extract_insight_sections(text, sections):
    """Extract specific sections from AI insight text"""
    if not text or text == "No AI insights found.":
        return {}
    
    result = {}
    for section_name, markers in sections.items():
        start_marker, end_marker = markers
        if start_marker in text:
            section = text.split(start_marker)[1]
            if end_marker and end_marker in section:
                section = section.split(end_marker)[0]
            
            # Format the section text with proper line breaks and bold formatting
            formatted_section = format_insight_section(section.strip())
            result[section_name] = formatted_section
        else:
            result[section_name] = ""
    return result

def format_insight_section(text):
    """Format insight section text with proper line breaks and bold formatting"""
    if not text:
        return ""
    
    # Split into lines and process each
    lines = text.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Handle bullet points with proper formatting
        if line.startswith('•'):
            # Remove the bullet point and check if it starts with a number
            clean_line = line[1:].strip()
            # Check if the line starts with a number followed by a period (more robust check)
            if clean_line and clean_line[0].isdigit() and len(clean_line) > 1 and clean_line[1] == '.':
                # For numbered items like "1. Supply Chain Disruptions"
                formatted_lines.append(clean_line)
            elif ':' in line:
                # Check if it contains a colon (like "Defence: Record global...")
                parts = line.split(':', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted_lines.append(f"**{label}:** {content}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        # Handle emoji headers (🛠, 📊, 🎯, ⚠️, 📈, 📉, 🔄) - only if they're standalone headers
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and ':' in line:
            # This is content within a section, not a header - don't bold it
            formatted_lines.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            # This is a standalone header - bold it
            formatted_lines.append(f"\n**{line}**")
        
        # Handle numbered lists (don't add bullet points to them)
        elif line and line[0].isdigit() and len(line) > 1 and line[1] == '.':
            formatted_lines.append(line)
        # Handle other lines that might need bullet points
        elif line and not line.startswith('-'):
            formatted_lines.append(f"• {line}")
        else:
            formatted_lines.append(line)
    
    return "\n\n".join(formatted_lines)

def format_sipri_text(text):
    """Format SIPRI analysis text with numbered points and emojis in styled containers"""
    if not text or text == "No SIPRI insights found.":
        return ""
    
    # Split into lines and add proper spacing
    lines = text.strip().split('\n')
    formatted_lines = []
    point_counter = 1
    
    # Define emojis for different types of content
    emoji_map = {
        'spending': '💰', 'military': '🛡️', 'defence': '🛡️', 'defense': '🛡️',
        'conflict': '⚔️', 'war': '⚔️', 'battle': '⚔️', 'fighting': '⚔️',
        'nuclear': '☢️', 'atomic': '☢️', 'missile': '🚀', 'weapon': '🔫',
        'russia': '🇷🇺', 'ukraine': '🇺🇦', 'europe': '🇪🇺', 'asia': '🌏',
        'china': '🇨🇳', 'india': '🇮🇳', 'us': '🇺🇸', 'america': '🇺🇸',
        'ai': '🤖', 'artificial': '🤖', 'intelligence': '🤖', 'cyber': '💻',
        'technology': '⚡', 'modern': '⚡', 'digital': '💻', 'computer': '💻',
        'fatalities': '💀', 'death': '💀', 'casualty': '💀', 'killed': '💀',
        'increase': '📈', 'growth': '📈', 'rise': '📈', 'higher': '📈',
        'decrease': '📉', 'decline': '📉', 'lower': '📉', 'drop': '📉',
        'report': '📊', 'analysis': '📊', 'data': '📊', 'statistics': '📊',
        'recommend': '💡', 'suggest': '💡', 'propose': '💡', 'advise': '💡',
        'risk': '⚠️', 'danger': '⚠️', 'threat': '⚠️', 'warning': '⚠️',
        'cooperation': '🤝', 'international': '🌍', 'global': '🌍', 'world': '🌍'
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
                        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
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
with st.spinner("Loading defence intelligence data..."):
    data = load_cached_defence_data()

# Extract data with error handling
high_value_contracts = data.get("high_value", pd.DataFrame())
emergency_contracts = data.get("emergency", pd.DataFrame())
frequent_items = data.get("frequent", pd.DataFrame())
combined_analysis = data.get("combined", pd.DataFrame())
word_frequency = data.get("word_freq", pd.DataFrame())
comprehensive_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")
sipri_insight = data.get("sipri_insight", "No SIPRI insights found.")

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter
if not combined_analysis.empty:
    min_date = combined_analysis['date'].min()
    max_date = combined_analysis['date'].max()
    
    st.sidebar.markdown("### 📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        combined_analysis = combined_analysis[
            (combined_analysis['date'].dt.date >= start_date) &
            (combined_analysis['date'].dt.date <= end_date)
        ]

# Value threshold filter
st.sidebar.markdown("### 💰 Value Threshold")
min_value = st.sidebar.number_input(
    "Minimum contract value (KRW):",
    min_value=0,
    value=0,
    step=1000000,
    format="%d"
)

if min_value > 0 and not combined_analysis.empty:
    combined_analysis = combined_analysis[combined_analysis['value'] >= min_value]

# Category filter
if not combined_analysis.empty and 'category' in combined_analysis.columns:
    st.sidebar.markdown("### 📋 Categories")
    all_categories = ["All"] + list(combined_analysis['category'].unique())
    selected_category = st.sidebar.selectbox("Select category:", all_categories)
    
    if selected_category != "All":
        combined_analysis = combined_analysis[combined_analysis['category'] == selected_category]

# Key Performance Metrics
st.markdown('<div class="section-header"><h2>📊 Key Performance Indicators</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty:
    # Calculate metrics
    total_value = combined_analysis['value'].sum()
    avg_value = combined_analysis['value'].mean()
    total_contracts = len(combined_analysis)
    max_value = combined_analysis['value'].max()
    min_date_display = combined_analysis['date'].min()
    max_date_display = combined_analysis['date'].max()
    
    # Calculate additional metrics
    median_value = combined_analysis['value'].median()
    value_std = combined_analysis['value'].std()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Contract Value",
            format_currency(total_value),
            f"{total_contracts:,} contracts",
            "#28a745"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Average Contract Value",
            format_currency(avg_value),
            f"±{format_currency(value_std)} std dev",
            "#007bff"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Largest Contract",
            format_currency(max_value),
            "Single contract value",
            "#ffc107"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Planned Order Date",
            max_date_display.strftime("%Y-%m-%d"),
            f"{total_contracts:,} contracts analyzed",
            "#6f42c1"
        ), unsafe_allow_html=True)
    
    # Additional metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Median Contract Value",
            format_currency(median_value),
            "50th percentile",
            "#17a2b8"
        ), unsafe_allow_html=True)
    
    with col2:
        # Calculate contracts above 1B KRW
        high_value_count = len(combined_analysis[combined_analysis['value'] >= 1e9])
        high_value_pct = (high_value_count / total_contracts * 100) if total_contracts > 0 else 0
        st.markdown(create_metric_card(
            "High-Value Contracts",
            f"{high_value_count:,}",
            f"{high_value_pct:.1f}% of total",
            "#dc3545"
        ), unsafe_allow_html=True)
    
    with col3:
        # Calculate emergency contracts
        emergency_count = len(emergency_contracts) if not emergency_contracts.empty else 0
        emergency_pct = (emergency_count / total_contracts * 100) if total_contracts > 0 else 0
        st.markdown(create_metric_card(
            "Emergency Contracts",
            f"{emergency_count:,}",
            f"{emergency_pct:.1f}% of total",
            "#fd7e14"
        ), unsafe_allow_html=True)
    
    with col4:
        # Calculate unique categories
        unique_categories = combined_analysis['category'].nunique() if 'category' in combined_analysis.columns else 0
        st.markdown(create_metric_card(
            "Contract Categories",
            f"{unique_categories}",
            "Different types",
            "#20c997"
        ), unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Data Available</h4>
        <p>No defence contract data is currently available. Please check your data sources or try refreshing the dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

# Contract Value Analysis
st.markdown('<div class="section-header"><h2>💰 Contract Value Distribution</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Enhanced distribution chart with log scale option
        log_scale = st.checkbox("Use log scale for better visualization", value=False)
        
        fig_dist = px.histogram(
            combined_analysis,
            x="value",
            nbins=30,
            title="Distribution of Contract Values",
            labels={"value": "Contract Value (KRW)", "count": "Number of Contracts"},
            color_discrete_sequence=["#1e3c72"],
            template="plotly_white"
        )
        
        if log_scale:
            fig_dist.update_xaxes(type="log")
            fig_dist.update_layout(title="Distribution of Contract Values (Log Scale)")
        
        fig_dist = apply_chart_styling(fig_dist)
        # Make the chart taller to align with value ranges
        fig_dist.update_layout(height=500)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        st.subheader("📊 Value Statistics")
        
        # Calculate percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        stats_data = []
        
        for p in percentiles:
            value = combined_analysis['value'].quantile(p/100)
            stats_data.append({
                "Percentile": f"{p}th",
                "Value": format_currency(value),
                "Raw Value": value
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df[["Percentile", "Value"]], use_container_width=True, hide_index=True)
        
        # Value range info
        st.markdown("**Value Ranges:**")
        st.markdown(f"• **Min:** {format_currency(combined_analysis['value'].min())}")
        st.markdown(f"• **Max:** {format_currency(combined_analysis['value'].max())}")
        st.markdown(f"• **Range:** {format_currency(combined_analysis['value'].max() - combined_analysis['value'].min())}")

# Top Contracts Analysis
st.markdown('<div class="section-header"><h2>🏆 Top Contracts Analysis</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty:
    # Top contracts with enhanced visualization
    top_n = st.slider("Number of top contracts to display:", 5, 20, 10)
    top_contracts = combined_analysis.nlargest(top_n, 'value')
    
    # Enhanced bar chart - full width
    fig_top = px.bar(
        top_contracts,
        x="indicator",
        y="value",
        title=f"Top {top_n} Contracts by Value",
        labels={"value": "Contract Value (KRW)", "indicator": "Contract Description"},
        color="value",
        color_continuous_scale="viridis",
        template="plotly_white"
    )
    
    # Show actual contract names (truncated) instead of "Contract 1, 2, 3"
    truncated_names = [name[:40] + "..." if len(name) > 40 else name for name in top_contracts['indicator']]
    fig_top.update_xaxes(
        tickangle=-45, 
        tickmode='array', 
        ticktext=truncated_names, 
        tickvals=list(range(len(top_contracts)))
    )
    
    fig_top = apply_chart_styling(fig_top)
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Top contracts table below the chart
    st.subheader(f"📋 Top {top_n} Contracts")
    
    # Enhanced table with better formatting
    display_df = top_contracts[['indicator', 'value', 'date', 'category']].copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
    display_df['value_formatted'] = display_df['value'].apply(format_currency)
    display_df['indicator_short'] = display_df['indicator'].str[:80] + '...'
    
    # Create a proper table
    table_df = display_df[['indicator_short', 'value_formatted', 'date', 'category']].copy()
    table_df.columns = ['Contract Description', 'Value', 'Date', 'Category']
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Contract Description': st.column_config.TextColumn(
                'Contract Description',
                width='large',
                help='Click to see full description'
            ),
            'Value': st.column_config.TextColumn(
                'Value',
                width='medium'
            ),
            'Date': st.column_config.TextColumn(
                'Date',
                width='small'
            ),
            'Category': st.column_config.TextColumn(
                'Category',
                width='medium'
            )
        }
    )

# Category Analysis
st.markdown('<div class="section-header"><h2>📋 Category Analysis</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty and 'category' in combined_analysis.columns:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Enhanced pie chart - showing contract counts (original logic)
        category_counts = combined_analysis['category'].value_counts()
        
        fig_cat = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Contracts by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_cat = apply_chart_styling(fig_cat)
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        st.subheader("📊 Category Statistics")
        
        # Enhanced category stats table with both count and value metrics
        category_stats = combined_analysis.groupby('category').agg({
            'value': ['count', 'sum', 'mean']
        }).round(2)
        category_stats.columns = ['Count', 'Total Value', 'Average Value']
        category_stats['Total Value'] = category_stats['Total Value'].apply(format_currency)
        category_stats['Average Value'] = category_stats['Average Value'].apply(format_currency)
        category_stats['Percentage'] = (category_stats['Count'] / category_stats['Count'].sum() * 100).round(1)
        
        # Sort by percentage in descending order
        category_stats = category_stats.sort_values('Percentage', ascending=False)
        
        st.dataframe(category_stats, use_container_width=True)

# Temporal Analysis
st.markdown('<div class="section-header"><h2>📅 Temporal Trends</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty:
    # Time aggregation options
    time_granularity = st.selectbox(
        "Select time granularity:",
        ["Monthly", "Quarterly", "Yearly"],
        index=0
    )
    
    # Prepare time series data
    if time_granularity == "Monthly":
        combined_analysis['time_period'] = combined_analysis['date'].dt.to_period('M')
    elif time_granularity == "Quarterly":
        combined_analysis['time_period'] = combined_analysis['date'].dt.to_period('Q')
    else:  # Yearly
        combined_analysis['time_period'] = combined_analysis['date'].dt.to_period('Y')
    
    time_series = combined_analysis.groupby('time_period').agg({
        'value': ['sum', 'count', 'mean'],
        'date': 'min'
    }).reset_index()
    
    time_series.columns = ['period', 'total_value', 'contract_count', 'avg_value', 'period_start']
    time_series['period_str'] = time_series['period'].astype(str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Value trend
        fig_value_trend = px.line(
            time_series,
            x="period_str",
            y="total_value",
            title=f"Total Contract Value Over Time ({time_granularity})",
            labels={"total_value": "Total Value (KRW)", "period_str": "Period"},
            color_discrete_sequence=["#1e3c72"],
            template="plotly_white"
        )
        fig_value_trend = apply_chart_styling(fig_value_trend)
        st.plotly_chart(fig_value_trend, use_container_width=True)
    
    with col2:
        # Count trend
        fig_count_trend = px.line(
            time_series,
            x="period_str",
            y="contract_count",
            title=f"Number of Contracts Over Time ({time_granularity})",
            labels={"contract_count": "Number of Contracts", "period_str": "Period"},
            color_discrete_sequence=["#28a745"],
            template="plotly_white"
        )
        fig_count_trend = apply_chart_styling(fig_count_trend)
        st.plotly_chart(fig_count_trend, use_container_width=True)
    


# Emergency Procurement Analysis
st.markdown('<div class="section-header"><h2>🚨 Emergency Procurement Analysis</h2></div>', unsafe_allow_html=True)

if not emergency_contracts.empty:
    # Calculate emergency metrics
    total_emergency = len(emergency_contracts)
    total_emergency_value = emergency_contracts['value'].sum()
    avg_emergency_value = emergency_contracts['value'].mean()
    max_emergency_value = emergency_contracts['value'].max()
    emergency_pct = (total_emergency / len(combined_analysis) * 100) if not combined_analysis.empty else 0
    
    # Largest Emergency Contract - single metric at top
    st.markdown(create_metric_card(
        "🏆 Largest Emergency Contract",
        format_currency(max_emergency_value),
        "Single contract value",
        "#6f42c1"
    ), unsafe_allow_html=True)
    
    # Create metrics in a grid layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card(
            "🚨 Emergency Contracts",
            f"{total_emergency:,}",
            f"{emergency_pct:.1f}% of total",
            "#dc3545"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "💰 Total Emergency Value",
            format_currency(total_emergency_value),
            "Combined value",
            "#fd7e14"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "📊 Average Emergency Value",
            format_currency(avg_emergency_value),
            "Per contract",
            "#e83e8c"
        ), unsafe_allow_html=True)
    
    
    # Emergency contracts detailed table
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h3 style="color: #c53030; margin-bottom: 1rem;">📋 Emergency Contract Details</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced table with better formatting
    emergency_display = emergency_contracts.copy()
    emergency_display['date'] = pd.to_datetime(emergency_display['date']).dt.strftime('%Y-%m-%d')
    emergency_display['value_formatted'] = emergency_display['value'].apply(format_currency)
    emergency_display['indicator_short'] = emergency_display['indicator'].str[:80] + '...'
    emergency_display['rank'] = range(1, len(emergency_display) + 1)
    
    # Sort by value descending
    emergency_display = emergency_display.sort_values('value', ascending=False)
    
    # Create enhanced table
    table_df = emergency_display[['rank', 'indicator_short', 'value_formatted', 'date']].copy()
    table_df.columns = ['Rank', 'Contract Description', 'Value', 'Date']
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Rank': st.column_config.NumberColumn(
                'Rank',
                width='small',
                help='Contract rank by value'
            ),
            'Contract Description': st.column_config.TextColumn(
                'Contract Description',
                width='large',
                help='Click to see full description'
            ),
            'Value': st.column_config.TextColumn(
                'Value',
                width='medium'
            ),
            'Date': st.column_config.TextColumn(
                'Date',
                width='small'
            )
        }
    )
else:
    st.info("No emergency procurement data available.")

# Word Frequency Analysis
st.markdown('<div class="section-header"><h2>🔍 Procurement Terms Analysis</h2></div>', unsafe_allow_html=True)

if not word_frequency.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Enhanced word frequency chart - always show top 10
        top_words = word_frequency.head(10)
        
        fig_words = px.bar(
            top_words,
            x="frequency",
            y="word",
            orientation='h',
            title="Top 10 Most Frequent Procurement Terms",
            labels={"frequency": "Frequency", "word": "Term"},
            color_discrete_sequence=["#6f42c1"],
            template="plotly_white"
        )
        fig_words = apply_chart_styling(fig_words)
        fig_words.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_words, use_container_width=True)
    
    with col2:
        st.subheader("📝 Term Analysis")
        
        # Term statistics
        total_terms = word_frequency['frequency'].sum()
        unique_terms = len(word_frequency)
        avg_frequency = word_frequency['frequency'].mean()
        
        st.metric("Total Term Occurrences", f"{total_terms:,}")
        st.metric("Unique Terms", f"{unique_terms:,}")
        st.metric("Average Frequency", f"{avg_frequency:.1f}")
else:
    st.info("No word frequency data available.")

# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)

if gemini_insight and gemini_insight != "No AI insights found.":
    # Define insight sections
    insight_sections = {
        "Core Trends": ("### Core Trend", "### Hidden Effects"),
        "Hidden Effects": ("### Hidden Effects", "### Strategic Recommendations"),
        "Strategic Recommendations": ("### Strategic Recommendations", "### Risk Assessment"),
        "Risk Assessment": ("### Risk Assessment", "### Market Intelligence"),
        "Market Intelligence": ("### Market Intelligence", None)
    }
    
    # Extract sections
    sections = extract_insight_sections(gemini_insight, insight_sections)
    
    # Create tabs
    tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
    tabs = st.tabs(tab_labels)
    
    for tab, (label, content) in zip(tabs, sections.items()):
        with tab:
            if content:
                st.markdown(f"### {label}")
                st.markdown(content)
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

# SIPRI Insights
st.markdown('<div class="section-header"><h2>📊 SIPRI Defence Report Insights</h2></div>', unsafe_allow_html=True)

if sipri_insight and sipri_insight != "No SIPRI insights found.":
    with st.expander("🔍 View SIPRI Defence Analysis", expanded=False):
        formatted_sipri = format_sipri_text(sipri_insight)
        st.markdown(formatted_sipri, unsafe_allow_html=True)
        
        # SIPRI metrics
        st.subheader("📈 SIPRI Analysis Metrics")
        sipri_metrics = {
            "Analysis Length": len(sipri_insight),
            "Contains Recommendations": "Yes" if "recommend" in sipri_insight.lower() or "suggest" in sipri_insight.lower() else "No",
            "Contains Risk Assessment": "Yes" if "risk" in sipri_insight.lower() else "No",
            "Last Updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        col1, col2, col3, col4 = st.columns(4)
        for i, (key, value) in enumerate(sipri_metrics.items()):
            with [col1, col2, col3, col4][i]:
                st.metric(key, value)
else:
    st.info("No SIPRI insights available at the moment.")

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)

if not combined_analysis.empty:
    with st.expander("📊 Interactive Data Analysis", expanded=False):
        # Export functionality in top right corner
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col4:
            if st.button("📥 Export Data", type="primary"):
                csv = combined_analysis.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"defence_contracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        # Advanced filtering options
        st.subheader("🔍 Advanced Filters")
        
        col1, col2 = st.columns(2)
        

        
        with col1:
            # Value range filter with simplified numbers
            min_val_raw = combined_analysis['value'].min()
            max_val_raw = combined_analysis['value'].max()
            
            # Convert to millions/billions for display and round up
            min_val_m = round(min_val_raw / 1e6, 0)
            max_val_m = round(max_val_raw / 1e6, 0)
            
            min_val, max_val = st.slider(
                "Contract Value Range (Million KRW):",
                min_value=float(min_val_m),
                max_value=float(max_val_m),
                value=(float(min_val_m), float(max_val_m)),
                step=1.0
            )
            
            # Convert back to actual values
            min_val_actual = min_val * 1e6
            max_val_actual = max_val * 1e6
        
        with col2:
            # Date range filter
            date_min, date_max = st.date_input(
                "Date Range:",
                value=(combined_analysis['date'].min().date(), combined_analysis['date'].max().date()),
                min_value=combined_analysis['date'].min().date(),
                max_value=combined_analysis['date'].max().date()
            )
        
        # Apply filters
        filtered_data = combined_analysis[
            (combined_analysis['value'] >= min_val_actual) &
            (combined_analysis['value'] <= max_val_actual) &
            (combined_analysis['date'].dt.date >= date_min) &
            (combined_analysis['date'].dt.date <= date_max)
        ]
        
        # Search functionality
        search_term = st.text_input("🔍 Search in contract descriptions:", placeholder="Enter keywords...")
        
        if search_term:
            filtered_data = filtered_data[
                filtered_data.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
            ]
        
        # Display filtered data
        st.subheader(f"📊 Filtered Results ({len(filtered_data):,} contracts)")
        
        if not filtered_data.empty:
            # Pagination
            page_size = st.selectbox("Records per page:", [10, 25, 50, 100], index=1)
            total_records = len(filtered_data)
            total_pages = (total_records + page_size - 1) // page_size
            
            if total_pages > 1:
                page = st.selectbox("Page:", range(1, total_pages + 1), index=0) - 1
                start_idx = page * page_size
                end_idx = min(start_idx + page_size, total_records)
                display_data = filtered_data.iloc[start_idx:end_idx]
            else:
                display_data = filtered_data
            
            # Enhanced data display
            display_final = display_data.copy()
            display_final['date'] = pd.to_datetime(display_final['date']).dt.strftime('%Y-%m-%d')
            display_final['value_formatted'] = display_final['value'].apply(format_currency)
            display_final['indicator_display'] = display_final['indicator'].str[:80] + '...'
            
            st.dataframe(
                display_final[['indicator_display', 'value_formatted', 'date', 'category']], 
                use_container_width=True,
                column_config={
                    'indicator_display': 'Contract Description',
                    'value_formatted': 'Value',
                    'date': 'Date',
                    'category': 'Category'
                },
                hide_index=True
            )
            
            st.caption(f"Showing {len(display_data)} of {total_records} records")
        else:
            st.warning("No data matches your current filters.")
else:
    st.warning("No data available for exploration.")

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🛡️ Defence Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> Defence Acquisition Program Administration (DAPA) | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive defence procurement analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)