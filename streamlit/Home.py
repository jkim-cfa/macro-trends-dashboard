import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd
from functools import lru_cache

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_loader import (
    load_agriculture_data,
    load_defence_data,
    load_economy_data,
    load_energy_data,
    load_industry_data,
    load_global_trade_data,
    load_korea_trade_data,
)

# --- Data Loading and Preprocessing ---
# Manually set total records and indicators (adjust if you want these dynamic)
total_records = 160721
total_indicators = 92

# Remove the old sector_dates global and broken function
# sector_dates = []

@lru_cache
def get_all_sector_data():
    sector_dates = []
    all_data = {}
    for df_loader in [
        load_agriculture_data,
        load_defence_data,
        load_economy_data,
        load_energy_data,
        load_industry_data,
        load_global_trade_data,
        load_korea_trade_data,
    ]:
        data = df_loader()
        for key in data:
            df = data[key]
            all_data[key] = df
            if isinstance(df, pd.DataFrame) and not df.empty and "date" in df.columns:
                try:
                    df["date"] = pd.to_datetime(df["date"])
                    sector_dates.append(df["date"].max())
                except Exception as e:
                    st.warning(f"Could not convert 'date' column to datetime for a dataframe from {df_loader.__name__}: {e}")
                    pass

    if sector_dates:
        last_update = max(sector_dates)
        if hasattr(last_update, 'strftime'):
            last_update = last_update.strftime('%Y-%m-%d')
        else:
            last_update = str(last_update)
    else:
        last_update = "N/A"

    return all_data, last_update

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Global Macro Insight Engine",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---
def create_metric_card(title, value, subtitle="", color="#007bff"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """

def extract_section(text, start, end=None):
    """Extract section between start and end markers from AI insight text."""
    if start not in text:
        return ""
    section = text.split(start)[1]
    if end and end in section:
        section = section.split(end)[0]
    return section.strip()

def format_insight_text(text):
    """Clean AI text for better markdown rendering in Streamlit, including custom bullet formatting."""
    if not text:
        return ""
    lines = text.strip().split('\n')
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Priority 1: Handle lines that start with a bullet point (•)
        if line.startswith("•"):
            content_after_bullet = line[1:].strip()
            # Check for "Label: Content" pattern after the bullet
            if ":" in content_after_bullet:
                parts = content_after_bullet.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    # Reconstruct with bold label and retain original bullet type
                    formatted.append(f"• **{label}:** {content}")
                else:
                    formatted.append(f"• {content_after_bullet}") # Fallback if colon is present but not "Label: Content"
            else:
                formatted.append(f"• {content_after_bullet}") # Regular bullet point
        
        # Priority 2: Handle emoji headers (e.g., 🛠, 📊) when they are standalone headers
        # This means they contain an emoji but NOT a colon (which would indicate content within a section)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            formatted.append(f"\n**{line}**")
        
        # Priority 3: Handle numbered lists (e.g., "1. Item")
        # Ensure it starts with a digit, has a period, and is not just a single digit
        elif len(line) > 1 and line[0].isdigit() and line[1] == '.':
            formatted.append(line)
        
        # Priority 4: Handle other lines that might need a default bullet point,
        # ensuring we don't double-bullet or modify existing markdown list syntax.
        elif not line.startswith(("- ", "* ", "+ ")) and not line.startswith("#"):
            formatted.append(f"• {line}")
        
        # Fallback for any other cases, though the above should cover most common scenarios
        else:
            formatted.append(line)
    
    return "\n\n".join(formatted)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* Main Header Styling */
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
        z-index: 0; /* Ensure it's behind text */
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
        font-size: 1.05rem;      /* Smaller font */
        max-width: 100%;         /* Use full width */
        margin: 0 auto 0 auto;   /* Remove extra margin */
        opacity: 0.95;
        line-height: 1.4;        /* Slightly tighter lines */
    }

    /* Metric Card Styling */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
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

    /* Dashboard Card Styling */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(220px, 1fr));
        gap: 1.2rem;
        margin-bottom: 3rem;
        justify-items: center;
    }
    @media (min-width: 900px) {
        .dashboard-grid {
            grid-template-columns: repeat(4, minmax(220px, 1fr));
        }
    }
    .dashboard-card {
        max-width: 260px;
        min-width: 180px;
        padding: 1.2rem 1rem 1rem 1rem;
        margin: 0.5rem auto;
        font-size: 0.98rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 420px;
        height: 100%;
        box-sizing: border-box;
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(30,60,114,0.10), 0 1.5px 6px rgba(44,62,80,0.06);
        border: 1.5px solid #e3e8f0;
        position: relative;
        transition: transform 0.18s cubic-bezier(.4,2,.6,1), box-shadow 0.18s cubic-bezier(.4,2,.6,1);
        overflow: hidden;
    }
    .dashboard-card::before {
        content: '';
        display: block;
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 6px;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        border-top-left-radius: 18px;
        border-top-right-radius: 18px;
    }
    .dashboard-card:hover {
        transform: translateY(-7px) scale(1.035);
        box-shadow: 0 12px 40px rgba(30,60,114,0.18), 0 2px 8px rgba(44,62,80,0.10);
        border-color: #1e3c72;
    }
    .card-icon {
        font-size: 2.7rem;
        margin-bottom: 0.7rem;
        margin-top: 0.7rem;
        text-align: center;
    }
    .card-title {
        font-size: 1.18rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
        color: #1e3c72;
        text-align: center;
    }
    .card-desc {
        font-size: 0.98rem;
        color: #495057;
        margin-bottom: 1.1rem;
        line-height: 1.5;
        text-align: center;
        flex: 1 1 auto;
    }
    .card-button {
        display: block;
        width: 100%;
        padding: 0.85rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.05rem;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(30,60,114,0.10);
        margin-top: 1.2rem;
        transition: background 0.18s, box-shadow 0.18s;
        text-align: center;
    }
    .card-button:hover {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        color: #fff;
        box-shadow: 0 6px 18px rgba(30,60,114,0.18);
        text-decoration: none;
    }

    /* Footer Styling */
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

    /* Section Header Styling */
    .section-header {
        margin-top: 3rem; /* Add some space above the section */
        margin-bottom: 2rem; /* Add space below the section header */
    }
    .section-header h2 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3c72; /* Dark blue from your gradient */
        padding-left: 15px; /* Indent the text slightly */
        border-left: 8px solid #2a5298; /* A prominent left border */
        position: relative;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    .section-header h2::after {
        content: '';
        display: block;
        width: 60px; /* Short underline */
        height: 3px;
        background: linear-gradient(90deg, #2a5298 0%, #a8c0ff 100%); /* Gradient underline */
        margin-top: 8px;
        border-radius: 5px;
    }

    /* Highlight Box (Why This Project Stands Out) Styling */
    .highlight-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%);
        border-radius: 16px; /* Slightly more rounded */
        padding: 2.5rem 2rem; /* More padding */
        margin: 3.5rem 0; /* More margin top/bottom */
        box-shadow: 0 8px 30px rgba(30, 60, 114, 0.12), 0 3px 10px rgba(42, 82, 152, 0.08); /* Stronger, layered shadow */
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(220, 230, 255, 0.8); /* Subtle light border */
        transition: transform 0.2s ease-in-out; /* Smooth transition for hover */
        background-image: url('data:image/svg+xml;charset=utf8,%3Csvg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noise" x="0" y="0"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="3" stitchTiles="stitch"%3E%3C/feTurbulence%3E%3C/filter%3E%3Crect width="100" height="100" filter="url(%23noise)" opacity="0.05"%3E%3C/rect%3E%3C/svg%3E'); /* Subtle noise */
        background-size: cover;
        background-blend-mode: overlay;
    }
    .highlight-box:hover {
        transform: translateY(-5px); /* Lift effect on hover */
    }
    .highlight-box::before {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 80px;
        height: 80px;
        background: radial-gradient(circle at 100% 100%, rgba(172, 204, 255, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        opacity: 0.7;
        z-index: 0;
    }
    .highlight-box h3 {
        color: #1e3c72;
        font-weight: 800;
        font-size: 1.9rem; /* Slightly larger heading */
        margin-bottom: 1.5rem; /* More space below heading */
        text-align: center;
        position: relative;
        z-index: 1; /* Ensure text is above pseudo-element */
        text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .highlight-box ul {
        color: #333;
        font-size: 1.1rem; /* Slightly larger text */
        line-height: 1.8; /* More comfortable line spacing */
        max-width: 750px; /* Slightly wider max-width for content */
        margin: auto;
        padding-left: 25px; /* Adjust padding for list */
        list-style: none; /* Remove default bullets */
        position: relative;
        z-index: 1;
    }
    .highlight-box ul li {
        margin-bottom: 0.8rem; /* Space between list items */
        position: relative;
        padding-left: 1.8rem; /* Space for custom bullet */
    }
    .highlight-box ul li::before {
        content: '✨'; /* Custom bullet point */
        position: absolute;
        left: 0;
        top: 0;
        font-size: 1.2rem;
        color: #ffd700; /* Gold color for sparkle */
    }
    .highlight-box ul li b {
        color: #1e3c72; /* Make bold text match header color */
    }
</style>
""", unsafe_allow_html=True)

# --- Streamlit App Layout ---

# Enhanced Header
st.markdown(f"""
<div class="main-header">
    <h1>🌐 Global Macro Insight Engine</h1>
    <p>
        A unified data intelligence platform for macroeconomic, trade, and geopolitical analysis.<br>
        Combines structured ETL pipelines, AI-powered insight generation, and interactive dashboards.<br>
        Designed to surface second-order effects and strategic trends across 7 global sectors.
    </p>
</div>

""", unsafe_allow_html=True)

# Display manually typed summary metrics
st.markdown('<div class="section-header"><h2>📊 Platform Overview</h2></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(create_metric_card(
        "📂 Sector Dashboards",
        "7",
        "",
        "#1e3c72"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card(
        "📈 Economic Indicators",
        f"{total_indicators}",
        "",
        "#1e3c72"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card(
        "🧾 Data Records",
        f"{total_records:,}", # Format with commas
        "",
        "#1e3c72"
    ), unsafe_allow_html=True)

# Before using last_update in the metric card, get it from the function:
_, last_update = get_all_sector_data()

with col4:
    st.markdown(create_metric_card(
        "📅 Last Update",
        last_update,
        "",
        "#1e3c72"
    ), unsafe_allow_html=True)

# Architecture, Stack & Skills
st.markdown("""
<div class="section-header"><h2>🛠️ Architecture, Stack & Skills</h2></div>

<p style="font-size: 1rem; color: #444; margin-bottom: 2rem;">
A lightweight, AI-integrated macroeconomic platform engineered for insight delivery and sector-wide intelligence.
</p>

<div class="tech-skill-grid">
    <div class="column">
        <h4>🛠 Tech Stack</h4>
        <table>
            <tr><th>Area</th><th>Tools</th></tr>
            <tr><td>Backend</td><td>Python, PostgreSQL, Docker</td></tr>
            <tr><td>AI & Viz</td><td>Gemini LLM, Plotly, Streamlit</td></tr>
            <tr><td>ETL</td><td>Pandas, NumPy, batch loaders</td></tr>
            <tr><td>Deployment</td><td>Docker Compose, Streamlit Cloud</td></tr>
        </table>
    </div>
    <div class="column">
        <h4>🎯 Core Skills</h4>
        <table>
            <tr><th>Domain</th><th>Focus</th></tr>
            <tr><td>Data & AI</td><td>ETL pipelines, LLM integration</td></tr>
            <tr><td>Strategy</td><td>Economic & trade intelligence</td></tr>
            <tr><td>Engineering</td><td>Containerization, modular pipelines</td></tr>
            <tr><td>Visualization</td><td>UX design, interactive dashboards</td></tr>
        </table>
    </div>
</div>

<style>
.tech-skill-grid {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.column {
    flex: 1;
    min-width: 300px;
}
.column h4 {
    margin-bottom: 0.6rem;
    color: #1e3c72;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
th {
    background: #1e3c72;
    color: white;
    padding: 0.6rem 1rem;
    text-align: left;
}
td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #e0e0e0;
}
tr:nth-child(even) {
    background: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)


# AI-Powered Strategic Analysis (Dynamic Content from Data Loaders)
st.markdown('<div class="section-header"><h2>🌟 AI Insights</h2></div>', unsafe_allow_html=True)

# Load all Gemini insights for display in tabs
tagri_gemini = load_agriculture_data().get("gemini_insight", "No AI insights found for Agriculture.")
defence_gemini = load_defence_data().get("gemini_insight", "No AI insights found for Defence.")
economy_gemini = load_economy_data().get("gemini_insight", "No AI insights found for Economy.")
energy_gemini = load_energy_data().get("gemini_insight", "No AI insights found for Energy.")
industry_gemini = load_industry_data().get("gemini_insight", "No AI insights found for Industry.")
global_trade_gemini = load_global_trade_data().get("gemini_insight", "No AI insights found for Global Trade.")
korea_trade_gemini = load_korea_trade_data().get("gemini_insight", "No AI insights found for Korea Trade.")

# Define insights mapping to tab labels with emojis
all_sector_insights = {
    "🌾 Agriculture": tagri_gemini,
    "🛡️ Defence": defence_gemini,
    "💹 Economy": economy_gemini,
    "⚡ Energy": energy_gemini,
    "🏭 Industry": industry_gemini,
    "🌍 Global Trade": global_trade_gemini,
    "🇰🇷 Korea Trade": korea_trade_gemini,
}

# Create tabs for each sector's AI insights
# Using a list comprehension to create labels for st.tabs
sector_tab_labels = [sector for sector in all_sector_insights.keys()]
sector_tabs = st.tabs(sector_tab_labels)

# Iterate through tabs and display content
for i, sector_name in enumerate(all_sector_insights.keys()):
    with sector_tabs[i]:
        gemini_insight_for_sector = all_sector_insights[sector_name]
        
        if gemini_insight_for_sector and "No AI insights found" not in gemini_insight_for_sector:
            # Extract and format sections for the current sector's insight
            sections = {
                "Core Trend": extract_section(gemini_insight_for_sector, "### Core Trend", "### Hidden Effects"),
                "Hidden Effects": extract_section(gemini_insight_for_sector, "### Hidden Effects", "### Strategic Recommendations"),
                "Strategic Recommendations": extract_section(gemini_insight_for_sector, "### Strategic Recommendations", "### Risk Assessment"),
                "Risk Assessment": extract_section(gemini_insight_for_sector, "### Risk Assessment", "### Market Intelligence"),
                "Market Intelligence": extract_section(gemini_insight_for_sector, "### Market Intelligence")
            }

            # Display sub-tabs within each sector tab for detailed insights
            insight_sub_tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
            insight_sub_tabs = st.tabs(insight_sub_tab_labels)

            for tab_idx, (label, content) in enumerate(sections.items()):
                with insight_sub_tabs[tab_idx]:
                    if content:
                        # Ensure the section title is prominently displayed within its sub-tab
                        st.markdown(f"**{label}**") 
                        st.markdown(format_insight_text(content))
                    else:
                        # Extract the sector name without emoji for the error message
                        sector_name_clean = sector_name.split(' ', 1)[1] if ' ' in sector_name else sector_name
                        st.info(f"No {label} insights available for {sector_name_clean}.")
        else:
            # Extract the sector name without emoji for the error message
            sector_name_clean = sector_name.split(' ', 1)[1] if ' ' in sector_name else sector_name
            st.info(f"No AI insights found for {sector_name_clean}.")


st.markdown("---") # Separator

# Sector Dashboards Section
st.markdown('<div class="section-header"><h2>🎯 Sector Dashboards</h2></div>', unsafe_allow_html=True)

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
        "desc": "In-depth analysis of military contracts, procurement patterns, supplier dynamics, and strategic defense signals — powered by structured data and AI-generated insights.",
        "page": "Defence_Dashboard",
        "features": ["Contract Analytics", "Procurement Trends", "Supplier Intelligence"]
    },
    {
        "icon": "💹",
        "title": "Economy",
        "desc": "Latest economic indicators, FX analysis with normalization, sentiment trends, inflation tracking, leading index tracking, and AI-powered strategic insights with dual-axis visualization.",
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

# Create a grid for dashboard cards
# Using 3 columns for larger screens, auto-fitting for smaller
dashboard_cols = st.columns(3)

for idx, dash in enumerate(DASHBOARDS):
    features_html = " • ".join(dash["features"])
    with dashboard_cols[idx % 3]: # Distribute cards across the 3 columns
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

# Footer
st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 1rem;">
        <strong style="color: #1e3c72;">Data Sources:</strong> World Bank, IMF, Korea Customs Service, World Steel Association, OPEC, USDA, DAPA, Bank of Korea (ECOS), and more.
    </div>
    <div style="margin-bottom: 1rem;">
        <strong style="color: #1e3c72;">AI Powered by:</strong> Gemini AI | <span style="color:#888;">Advanced EDA and LLM-driven insights</span>
    </div>
    <div style="font-size: 0.9rem; color: #888; margin-bottom: 1rem;">
        Platform last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
        <span style="color: #28a745;">●</span> All systems operational
    </div>
    <div style="font-size: 0.9rem; color: #888; margin-top: 1rem;">
        🔗 <a href="https://github.com/emailoneid/Global_Macro_Insight_Engine" target="_blank" style="color: #1e3c72; text-decoration: none; font-weight: 600;">View on GitHub</a> &nbsp; | &nbsp;
        💼 <a href="https://www.linkedin.com/in/jaeha-kim16/" target="_blank" style="color: #1e3c72; text-decoration: none; font-weight: 600;">Connect on LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)
