# Home.py
import streamlit as st
from datetime import datetime
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_economy_data

st.set_page_config(
    page_title="Global Macro Insight Engine", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for Home page
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        position: relative;
        z-index: 1;
        font-size: 1.3rem;
        max-width: 800px;
        margin: auto;
        opacity: 0.95;
        line-height: 1.6;
    }
    .stats-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
    }
    .dashboard-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        box-shadow: 0 6px 25px rgba(44,62,80,0.08);
        border: 1px solid #e9ecef;
        padding: 2.5rem 2rem 2rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
    }
    .dashboard-card:hover {
        box-shadow: 0 12px 40px rgba(44,62,80,0.15);
        transform: translateY(-6px) scale(1.02);
    }
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        color: #1e3c72;
    }
    .card-desc {
        font-size: 1rem;
        color: #495057;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .card-button {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(30,60,114,0.3);
    }
    .card-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(30,60,114,0.4);
        color: white;
        text-decoration: none;
    }
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 20px;
        margin-top: 3rem;
        color: #6c757d;
        font-size: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .feature-highlight {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        text-align: center;
    }
    .feature-highlight h3 {
        color: #155724;
        margin-bottom: 0.5rem;
    }
    .feature-highlight p {
        color: #155724;
        margin: 0;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header
st.markdown(f"""
<div class="main-header">
    <h1>🌐 Global Macro Insight Engine</h1>
    <p>
        Comprehensive cross-sector economic intelligence platform featuring real-time analytics, 
        AI-powered insights, and interactive data visualization across agriculture, defence, 
        economy, energy, trade, and industry sectors.
    </p>
</div>
""", unsafe_allow_html=True)

# Data Quality Overview Section
st.markdown("## 📊 Platform Overview")

# Load sample data for statistics (using economy data as example)
try:
    with st.spinner("Loading platform statistics..."):
        data = load_economy_data()
        
        # Calculate statistics
        total_indicators = 0
        total_records = 0
        date_range = "N/A"
        
        if data:
            # Economic indicators
            eco_data = data.get("economic_indicators_raw", [])
            if hasattr(eco_data, 'shape'):
                total_records += eco_data.shape[0]
                total_indicators += len(eco_data['indicator'].unique()) if 'indicator' in eco_data.columns else 0
            
            # FX data
            fx_data = data.get("fx_raw", [])
            if hasattr(fx_data, 'shape'):
                total_records += fx_data.shape[0]
            
            # Sentiment data
            sent_data = data.get("sentiment_raw", [])
            if hasattr(sent_data, 'shape'):
                total_records += sent_data.shape[0]
                total_indicators += len(sent_data['indicator'].unique()) if 'indicator' in sent_data.columns else 0
            
            # Get date range from economic data
            if hasattr(eco_data, 'shape') and not eco_data.empty and 'date' in eco_data.columns:
                try:
                    min_date = eco_data['date'].min()
                    max_date = eco_data['date'].max()
                    date_range = f"{min_date} to {max_date}"
                except:
                    date_range = "Available"
        
        # Display statistics
        st.markdown('<div class="stats-section">', unsafe_allow_html=True)
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">7</div>
                <div class="stat-label">Sector Dashboards</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_indicators:,}</div>
                <div class="stat-label">Economic Indicators</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_records:,}</div>
                <div class="stat-label">Data Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">AI</div>
                <div class="stat-label">Powered Insights</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
except Exception as e:
    st.info("Platform statistics loading...")

# Feature Highlight
st.markdown("""
<div class="feature-highlight">
    <h3>🚀 New Features Available</h3>
    <p>Enhanced Economy Dashboard with dual y-axis charts, normalized FX rates, universal date filtering, and AI-powered strategic insights</p>
</div>
""", unsafe_allow_html=True)


# Enhanced Dashboard Grid
st.markdown("## 🎯 Sector Dashboards")

# Updated Dashboard definitions with enhanced descriptions
DASHBOARDS = [
    {
        "icon": "🌾",
        "title": "Agriculture Production",
        "desc": "Comprehensive crop analysis, growth trends, yield predictions, and agricultural market intelligence with seasonal patterns and supply chain insights.",
        "page": "Agriculture_Dashboard",
        "features": ["Crop Trends", "Growth Analysis", "Market Intelligence"]
    },
    {
        "icon": "🛡️",
        "title": "Defence Procurement",
        "desc": "Advanced defence contract analytics, procurement trends, supplier analysis, and strategic defence sector intelligence with real-time monitoring.",
        "page": "Defence_Dashboard",
        "features": ["Contract Analytics", "Procurement Trends", "Supplier Intelligence"]
    },
    {
        "icon": "💹",
        "title": "Economy",
        "desc": "Real-time economic indicators, FX analysis with normalization, sentiment trends, and AI-powered strategic insights with dual-axis visualization.",
        "page": "Economy_Dashboard",
        "features": ["Economic Indicators", "FX Analysis", "AI Insights"]
    },
    {
        "icon": "⚡",
        "title": "Energy",
        "desc": "Comprehensive energy market analysis including oil stocks, import trends, OPEC insights, and energy supply chain intelligence.",
        "page": "Energy_Dashboard",
        "features": ["Oil Stocks", "Import Trends", "OPEC Insights"]
    },
    {
        "icon": "🌍",
        "title": "Global Trade",
        "desc": "Global shipping analytics, trade partner analysis, volatility trends, and international trade flow intelligence with BDI tracking.",
        "page": "Global_Trade_Dashboard",
        "features": ["Shipping Analytics", "Trade Partners", "Volatility Trends"]
    },
    {
        "icon": "🏭",
        "title": "Industry",
        "desc": "Manufacturing inventory analysis, steel production trends, industrial capacity utilization, and sector performance metrics.",
        "page": "Industry_Dashboard",
        "features": ["Manufacturing", "Steel Production", "Capacity Analysis"]
    },
    {
        "icon": "🇰🇷",
        "title": "Korea Trade",
        "desc": "Korea-specific trade analytics, semiconductor exports, import/export balance, and trade partner analysis with detailed breakdowns.",
        "page": "Korea_Trade_Dashboard",
        "features": ["Trade Analytics", "Semiconductors", "Export/Import"]
    },
]

st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)

for dash in DASHBOARDS:
    features_html = " • ".join(dash["features"])
    st.markdown(f'''
    <div class="dashboard-card">
        <div class="card-icon">{dash["icon"]}</div>
        <div class="card-title">{dash["title"]}</div>
        <div class="card-desc">{dash["desc"]}</div>
        <div style="font-size: 0.85rem; color: #6c757d; margin-bottom: 1.5rem; font-weight: 500;">
            {features_html}
        </div>
        <a href="/{dash["page"]}" target="_self" class="card-button">Open Dashboard</a>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Footer
st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 1rem;">
        <strong style="color: #1e3c72;">Data Sources:</strong> World Bank, IMF, Korea Customs Service, World Steel Association, OPEC, USDA, DAPA, Bank of Korea (ECOS), and more.
    </div>
    <div style="margin-bottom: 1rem;">
        <strong style="color: #1e3c72;">AI Powered by:</strong> Gemini AI | <span style="color:#888;">Advanced EDA and LLM-driven insights</span>
    </div>
    <div style="font-size: 0.9rem; color: #888;">
        Platform last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
        <span style="color: #28a745;">●</span> All systems operational
    </div>
</div>
""", unsafe_allow_html=True)
