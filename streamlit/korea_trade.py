import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Korea Trade EDA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data loading functions
@st.cache_data
def load_csv(filename):
    """Load CSV files from the EDA outputs directory"""
    base_path = "eda/outputs/korea_trade/"
    try:
        return pd.read_csv(base_path + filename)
    except FileNotFoundError:
        st.error(f"File not found: {filename}")
        return pd.DataFrame()

@st.cache_data
def load_json(filename):
    """Load JSON files from the EDA outputs directory"""
    base_path = "eda/outputs/korea_trade/"
    try:
        with open(base_path + filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: {filename}")
        return {}

@st.cache_data
def load_gemini_insights():
    """Load Gemini AI insights text file"""
    base_path = "eda/outputs/korea_trade/"
    try:
        with open(base_path + "gemini_insights_korea_trade.txt", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "AI insights not available"

# Load all data
def load_all_data():
    """Load all data files"""
    data = {}
    
    # Trade data
    data['export_top_amount'] = load_csv("export_top_items_by_amount.csv")
    data['export_top_yoy'] = load_csv("export_top_items_by_yoy.csv")
    data['import_top_amount'] = load_csv("import_top_items_by_amount.csv")
    data['import_top_yoy'] = load_csv("import_top_items_by_yoy.csv")
    
    # Partner data
    data['export_partners'] = load_csv("export_top_partners.csv")
    data['import_partners'] = load_csv("import_top_partners.csv")
    data['trade_yoy_export'] = load_csv("trade_yoy_top_export_partners.csv")
    data['trade_yoy_import'] = load_csv("trade_yoy_top_import_partners.csv")
    data['trade_balance'] = load_csv("trade_balance.csv")
    
    # Value index data
    data['value_index_top'] = load_csv("value_index_top_yoy.csv")
    data['value_index_bottom'] = load_csv("value_index_bottom_yoy.csv")
    
    # Semiconductor data
    data['wsts_monthly'] = load_csv("wsts_top_monthly_regions.csv")
    data['wsts_annual'] = load_csv("wsts_top_annual_regions.csv")
    data['wsts_volatility'] = load_csv("wsts_volatility.csv")
    data['wsts_trend_monthly'] = load_csv("wsts_trend_monthly.csv")
    data['wsts_yoy_monthly'] = load_csv("wsts_yoy_monthly.csv")
    data['wsts_market_share'] = load_csv("wsts_market_share_monthly.csv")
    
    # Insights
    data['key_insights'] = load_json("key_insights.json")
    data['gemini_insights'] = load_gemini_insights()
    
    return data

# Main app
def main():
    st.title("🇰🇷 Korea Trade EDA Dashboard")
    st.markdown("---")
    
    # Load data
    data = load_all_data()
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis Section",
        [
            "🏠 Overview",
            "📈 Export Analysis", 
            "📉 Import Analysis",
            "🤝 Trade Partners",
            "💹 Value Indices",
            "🔌 Semiconductor",
            "🤖 AI Insights"
        ]
    )
    
    # Display selected page
    if page == "🏠 Overview":
        show_overview(data)
    elif page == "📈 Export Analysis":
        show_export_analysis(data)
    elif page == "📉 Import Analysis":
        show_import_analysis(data)
    elif page == "🤝 Trade Partners":
        show_trade_partners(data)
    elif page == "💹 Value Indices":
        show_value_indices(data)
    elif page == "🔌 Semiconductor":
        show_semiconductor(data)
    elif page == "🤖 AI Insights":
        show_ai_insights(data)

def show_overview(data):
    """Overview page with key metrics and summary"""
    st.header("🏠 Overview")
    
    # Key insights summary
    if data['key_insights']:
        insights = data['key_insights']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Latest Export Date", 
                insights.get('export_analysis', {}).get('latest_date', 'N/A')
            )
        
        with col2:
            st.metric(
                "Latest Import Date", 
                insights.get('import_analysis', {}).get('latest_date', 'N/A')
            )
        
        with col3:
            st.metric(
                "Top Export Commodity", 
                insights.get('export_analysis', {}).get('top_commodity', 'N/A')
            )
        
        with col4:
            st.metric(
                "Top Import Commodity", 
                insights.get('import_analysis', {}).get('top_commodity', 'N/A')
            )
    
    # Top commodities comparison
    st.subheader("📊 Top Commodities Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not data['export_top_amount'].empty:
            st.write("**Top Export Commodities by Amount**")
            fig = px.bar(
                data['export_top_amount'].head(10),
                x='commodity_name_en',
                y='export_amount',
                title="Top 10 Export Commodities"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not data['import_top_amount'].empty:
            st.write("**Top Import Commodities by Amount**")
            fig = px.bar(
                data['import_top_amount'].head(10),
                x='commodity_name_en',
                y='import_amount',
                title="Top 10 Import Commodities"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def show_export_analysis(data):
    """Export analysis page"""
    st.header("📈 Export Analysis")
    
    # Top export commodities by amount
    if not data['export_top_amount'].empty:
        st.subheader("Top Export Commodities by Amount")
        
        fig = px.bar(
            data['export_top_amount'].head(15),
            x='commodity_name_en',
            y='export_amount',
            color='trade_yoy',
            title="Top 15 Export Commodities (Size = Amount, Color = YoY Growth)",
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(
            data['export_top_amount'].head(15)[['commodity_name_en', 'export_amount', 'trade_yoy']],
            use_container_width=True
        )
    
    # Top export commodities by YoY growth
    if not data['export_top_yoy'].empty:
        st.subheader("Top Export Commodities by YoY Growth")
        
        fig = px.bar(
            data['export_top_yoy'].head(15),
            x='commodity_name_en',
            y='trade_yoy',
            color='export_amount',
            title="Top 15 Export Commodities by YoY Growth (Size = Amount, Color = Growth Rate)",
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(
            data['export_top_yoy'].head(15)[['commodity_name_en', 'trade_yoy', 'export_amount']],
            use_container_width=True
        )

def show_import_analysis(data):
    """Import analysis page"""
    st.header("📉 Import Analysis")
    
    # Top import commodities by amount
    if not data['import_top_amount'].empty:
        st.subheader("Top Import Commodities by Amount")
        
        fig = px.bar(
            data['import_top_amount'].head(15),
            x='commodity_name_en',
            y='import_amount',
            color='trade_yoy',
            title="Top 15 Import Commodities (Size = Amount, Color = YoY Growth)",
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(
            data['import_top_amount'].head(15)[['commodity_name_en', 'import_amount', 'trade_yoy']],
            use_container_width=True
        )
    
    # Top import commodities by YoY growth
    if not data['import_top_yoy'].empty:
        st.subheader("Top Import Commodities by YoY Growth")
        
        fig = px.bar(
            data['import_top_yoy'].head(15),
            x='commodity_name_en',
            y='trade_yoy',
            color='import_amount',
            title="Top 15 Import Commodities by YoY Growth (Size = Amount, Color = Growth Rate)",
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(
            data['import_top_yoy'].head(15)[['commodity_name_en', 'trade_yoy', 'import_amount']],
            use_container_width=True
        )

def show_trade_partners(data):
    """Trade partners analysis page"""
    st.header("🤝 Trade Partners Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not data['export_partners'].empty:
            st.subheader("Top Export Partners")
            fig = px.bar(
                data['export_partners'].head(10),
                x='partner',
                y='export_amount',
                title="Top 10 Export Partners"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                data['export_partners'].head(10)[['partner', 'export_amount', 'trade_share']],
                use_container_width=True
            )
    
    with col2:
        if not data['import_partners'].empty:
            st.subheader("Top Import Partners")
            fig = px.bar(
                data['import_partners'].head(10),
                x='partner',
                y='import_amount',
                title="Top 10 Import Partners"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                data['import_partners'].head(10)[['partner', 'import_amount', 'trade_share']],
                use_container_width=True
            )
    
    # Trade balance
    if not data['trade_balance'].empty:
        st.subheader("Trade Balance by Partner")
        
        # Filter for latest date
        latest_date = data['trade_balance']['date'].max()
        latest_balance = data['trade_balance'][data['trade_balance']['date'] == latest_date]
        
        if not latest_balance.empty:
            fig = px.bar(
                latest_balance.head(15),
                x='partner',
                y='trade_balance',
                title=f"Trade Balance by Partner ({latest_date})",
                color='trade_balance',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)

def show_value_indices(data):
    """Value indices analysis page"""
    st.header("💹 Value Indices Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not data['value_index_top'].empty:
            st.subheader("Top Performers (YoY Growth)")
            fig = px.bar(
                data['value_index_top'].head(10),
                x='item_en',
                y='yoy_change',
                title="Top 10 Items by YoY Growth"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                data['value_index_top'].head(10)[['item_en', 'yoy_change', 'trade_type']],
                use_container_width=True
            )
    
    with col2:
        if not data['value_index_bottom'].empty:
            st.subheader("Bottom Performers (YoY Growth)")
            fig = px.bar(
                data['value_index_bottom'].head(10),
                x='item_en',
                y='yoy_change',
                title="Bottom 10 Items by YoY Growth"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                data['value_index_bottom'].head(10)[['item_en', 'yoy_change', 'trade_type']],
                use_container_width=True
            )

def show_semiconductor(data):
    """Semiconductor analysis page"""
    st.header("🔌 Semiconductor Industry Analysis")
    
    # Top regions
    if not data['wsts_monthly'].empty:
        st.subheader("Top Semiconductor Regions (Monthly)")
        fig = px.bar(
            data['wsts_monthly'].head(15),
            x='country',
            y='value',
            title="Top 15 Semiconductor Regions by Monthly Billings"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            data['wsts_monthly'].head(15)[['country', 'value', 'unit']],
            use_container_width=True
        )
    
    # Annual comparison
    if not data['wsts_annual'].empty:
        st.subheader("Top Semiconductor Regions (Annual)")
        fig = px.bar(
            data['wsts_annual'].head(15),
            x='country',
            y='value',
            title="Top 15 Semiconductor Regions by Annual Billings"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Volatility analysis
    if not data['wsts_volatility'].empty:
        st.subheader("Semiconductor Market Volatility")
        fig = px.bar(
            data['wsts_volatility'].head(15),
            x='country',
            y='volatility',
            title="Top 15 Regions by Market Volatility"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Market share trends
    if not data['wsts_market_share'].empty:
        st.subheader("Market Share Trends")
        
        # Select countries to display
        countries = data['wsts_market_share']['country'].unique()
        selected_countries = st.multiselect(
            "Select countries to display:",
            countries,
            default=countries[:5] if len(countries) > 5 else countries
        )
        
        if selected_countries:
            filtered_data = data['wsts_market_share'][
                data['wsts_market_share']['country'].isin(selected_countries)
            ]
            
            fig = px.line(
                filtered_data,
                x='date',
                y='market_share',
                color='country',
                title="Market Share Trends Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_ai_insights(data):
    """AI insights page"""
    st.header("🤖 AI-Generated Strategic Insights")
    
    # Key insights summary
    if data['key_insights']:
        st.subheader("📊 Key Metrics Summary")
        
        insights = data['key_insights']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Analysis**")
            export_data = insights.get('export_analysis', {})
            st.write(f"- Latest Date: {export_data.get('latest_date', 'N/A')}")
            st.write(f"- Total Records: {export_data.get('total_records', 'N/A')}")
            st.write(f"- Top Commodity: {export_data.get('top_commodity', 'N/A')}")
            st.write(f"- Top YoY Growth: {export_data.get('top_yoy_growth', 'N/A')}%")
        
        with col2:
            st.write("**Import Analysis**")
            import_data = insights.get('import_analysis', {})
            st.write(f"- Latest Date: {import_data.get('latest_date', 'N/A')}")
            st.write(f"- Total Records: {import_data.get('total_records', 'N/A')}")
            st.write(f"- Top Commodity: {import_data.get('top_commodity', 'N/A')}")
            st.write(f"- Top YoY Growth: {import_data.get('top_yoy_growth', 'N/A')}%")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Trade Partnerships**")
            trade_data = insights.get('trade_yoy_analysis', {})
            st.write(f"- Top Export Partner: {trade_data.get('top_export_partner', 'N/A')}")
            st.write(f"- Top Import Partner: {trade_data.get('top_import_partner', 'N/A')}")
        
        with col4:
            st.write("**Semiconductor Industry**")
            semi_data = insights.get('semiconductor_analysis', {})
            st.write(f"- Latest Month: {semi_data.get('latest_month', 'N/A')}")
            st.write(f"- Top Region: {semi_data.get('top_monthly_region', 'N/A')}")
    
    # Gemini AI insights
    st.subheader("🧠 Strategic Analysis")
    
    if data['gemini_insights'] and data['gemini_insights'] != "AI insights not available":
        st.markdown(data['gemini_insights'])
    else:
        st.warning("AI insights not available. Please run the EDA script first to generate insights.")
    
    # Analysis timestamp
    if data['key_insights'] and 'analysis_timestamp' in data['key_insights']:
        st.caption(f"Analysis generated on: {data['key_insights']['analysis_timestamp']}")

if __name__ == "__main__":
    main() 