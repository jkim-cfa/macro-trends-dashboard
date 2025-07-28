import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_agriculture_data

# Page Config
st.set_page_config(
    page_title="Agriculture Production Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .section-header {
        background: linear-gradient(90deg, #6c757d, #495057);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>🌾 Agriculture Production Dashboard</h1>
    <p>Comprehensive analysis of crop production trends, growth rates, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

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
            # Make sure the bullet point is followed by a space and bold the label
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted.append(f"**{label}:** {content}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        # Handle emoji headers
        elif any(e in line for e in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']):
            formatted.append(line)
        # For other lines, add bullet points
        elif line and not line.startswith("-"):
            formatted.append(f"• {line}")
        else:
            formatted.append(line)
    
    return "\n\n".join(formatted)

def apply_chart_styling(fig, title_color="#2E8B57"):
    """Apply consistent styling to charts"""
    fig.update_layout(
        title_font_size=20,
        title_font_color=title_color,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white"
    )
    return fig

# Load and Format Data
data = load_agriculture_data()
trend_data = format_dates_for_display(data.get("trend", pd.DataFrame()))
yoy_data = format_dates_for_display(data.get("yoy", pd.DataFrame()))
growth_data = data.get("growth", pd.DataFrame())
corr_data = data.get("corr", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Performance Metrics</h2></div>', unsafe_allow_html=True)
if key_insights:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🏆 Top Performer</h3>
            <h2 style="color: #28a745;">{}</h2>
        </div>
        """.format(key_insights.get("highest_growth", "N/A")), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Peak Growth</h3>
            <h2 style="color: #007bff;">{}%</h2>
        </div>
        """.format(key_insights.get("highest_growth_rate", 0)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Average Growth</h3>
            <h2 style="color: #ffc107;">{}%</h2>
        </div>
        """.format(key_insights.get("average_growth", 0)), unsafe_allow_html=True)
    
    with col4:
        # Calculate additional metric
        if not growth_data.empty:
            total_commodities = len(growth_data)
            st.markdown("""
            <div class="metric-card">
                <h3>🌾 Total Commodities</h3>
                <h2 style="color: #6f42c1;">{}</h2>
            </div>
            """.format(total_commodities), unsafe_allow_html=True)
else:
    st.warning("No key insights data available.")

# Production Trends with enhanced visualization
st.markdown('<div class="section-header"><h2>📈 Production Trends Analysis</h2></div>', unsafe_allow_html=True)
if not trend_data.empty and len(trend_data.columns) > 1:
    # Add "All Commodities" option
    all_options = ["All Commodities"] + list(trend_data.columns[1:])
    selected_commodities = st.multiselect(
        "Select Commodities for Trend Analysis",
        options=all_options,
        default=["All Commodities"]
    )
    
    if selected_commodities:
        if "All Commodities" in selected_commodities:
            # Show all commodities
            commodities_to_plot = trend_data.columns[1:]
        else:
            # Show selected commodities
            commodities_to_plot = selected_commodities
        
        # Enhanced line chart with better styling
        fig_trend = px.line(
            trend_data,
            x="date",
            y=commodities_to_plot,
            title="Commodity Production Trends Over Time",
            labels={"value": "Production Volume", "date": "Year"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white"
        )
        
        fig_trend.update_layout(
            title_font_size=20,
            title_font_color="#2E8B57",
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Please select at least one commodity to view trends.")
else:
    st.warning("No trend data available.")

# Growth Rate Analysis with enhanced visualization
st.markdown('<div class="section-header"><h2>🚀 Growth Performance Analysis</h2></div>', unsafe_allow_html=True)
if not growth_data.empty:
    sorted_growth = growth_data.sort_values("CAGR (%)", ascending=False)
    
    # Enhanced bar chart
    fig_growth = px.bar(
        sorted_growth,
        x="Commodity",
        y="CAGR (%)",
        title="Compound Annual Growth Rate (CAGR) by Commodity",
        color="CAGR (%)",
        color_continuous_scale="RdYlGn",
        template="plotly_white"
    )
    
    fig_growth = apply_chart_styling(fig_growth, "#2E8B57")
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Enhanced data table
    st.subheader("📋 Detailed Growth Statistics")
    styled_growth = sorted_growth.style.background_gradient(subset=['CAGR (%)'], cmap='RdYlGn')
    st.dataframe(styled_growth, use_container_width=True)
else:
    st.warning("No growth rate data available.")

# YoY Changes with enhanced visualization
st.markdown('<div class="section-header"><h2>🔄 Year-over-Year Performance</h2></div>', unsafe_allow_html=True)
if not yoy_data.empty and 'commodity' in yoy_data.columns:
    commodity_options = ["All Commodities"] + list(yoy_data['commodity'].unique())
    selected_yoy_commodity = st.selectbox(
        "Select a commodity for YoY analysis",
        options=commodity_options
    )
    
    if selected_yoy_commodity == "All Commodities":
        # Enhanced multi-line chart
        fig_yoy = px.line(
            yoy_data,
            x="date",
            y="yoy_change",
            color="commodity",
            title="Year-over-Year Change for All Commodities",
            labels={"yoy_change": "YoY Change (%)", "date": "Year"},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white"
        )
        
        fig_yoy = apply_chart_styling(fig_yoy, "#2E8B57")
    else:
        yoy_filtered = yoy_data[yoy_data['commodity'] == selected_yoy_commodity]
        # Enhanced single line chart
        fig_yoy = px.line(
            yoy_filtered,
            x="date",
            y="yoy_change",
            title=f"Year-over-Year Change for {selected_yoy_commodity}",
            labels={"yoy_change": "YoY Change (%)", "date": "Year"},
            color_discrete_sequence=["#2E8B57"],
            template="plotly_white"
        )
        
        fig_yoy = apply_chart_styling(fig_yoy, "#2E8B57")
    
    st.plotly_chart(fig_yoy, use_container_width=True)
else:
    st.warning("No YoY data available.")

# Correlation Matrix with enhanced visualization
st.markdown('<div class="section-header"><h2>🔗 Commodity Correlation Analysis</h2></div>', unsafe_allow_html=True)
if not corr_data.empty:
    # Enhanced correlation heatmap
    fig_corr = px.imshow(
        corr_data,
        title="Correlation Matrix Between Commodities",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        template="plotly_white"
    )
    
    fig_corr = apply_chart_styling(fig_corr, "#2E8B57")
    
    fig_corr.update_layout(
        height=600
    )
    
    fig_corr.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Correlation insights
    st.info("💡 **Correlation Insights**: Values closer to 1 indicate strong positive correlation, while values closer to -1 indicate strong negative correlation.")
else:
    st.warning("No correlation data available.")

# Enhanced Raw Data Preview
st.header("📄 Data Explorer")
ready_data = data.get("ready", pd.DataFrame())

if not ready_data.empty:
    ready_data_display = format_dates_for_display(ready_data)
    with st.expander("📊 Click to preview agriculture production data", expanded=False):
        # Add search and filter capabilities
        search_term = st.text_input("🔍 Search data:", placeholder="Enter commodity name...")
        
        if search_term:
            filtered_data = ready_data_display[
                ready_data_display.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
            ]
        else:
            filtered_data = ready_data_display
        
        # Add pagination
        page_size = st.selectbox("📄 Records per page:", [10, 25, 50, 100], index=0)
        total_records = len(filtered_data)
        total_pages = (total_records + page_size - 1) // page_size
        
        if total_pages > 1:
            page = st.selectbox("📖 Page:", range(1, total_pages + 1), index=0) - 1
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, total_records)
            display_data = filtered_data.iloc[start_idx:end_idx]
        else:
            display_data = filtered_data
        
        st.dataframe(display_data, use_container_width=True)
        st.caption(f"Showing {len(display_data)} of {total_records} records")
else:
    st.warning("No raw data available for preview.")

# AI-Powered Strategic Analysis with enhanced styling
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
            st.subheader(label)
            if content:
                st.markdown(format_insight_text(content))
            else:
                st.info(f"No {label} insights available.")
else:
    # Enhanced no AI insight message
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("## 🌟")
    with col2:
        st.warning("No AI insights found for this dataset.")
        st.markdown("""
        - Ensure sufficient and clean data was provided  
        - Check Gemini API setup and prompt coverage  
        - Try re-generating insights if conditions improve  
        """)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; background: linear-gradient(90deg, #f8f9fa, #e9ecef); border-radius: 10px;">
    <p><strong>Data Source:</strong> U.S. Department of Agriculture | <strong>Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">🌾 Comprehensive Agriculture Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)
