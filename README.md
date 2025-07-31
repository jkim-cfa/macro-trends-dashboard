# 🌐 Global Macro Insight Engine

A modular, AI-powered macroeconomic intelligence platform that integrates structured datasets, real-time insights, and generative AI to surface second-order effects, track strategic trends, and support economic, trade, and defense analysis.

---

## 🚀 Project Summary

**Global Macro Insight Engine** is a full-stack data platform designed to:
- Ingest and standardize macroeconomic, trade, defense, and energy datasets.
- Generate LLM-based insights for each sector across multiple analytical dimensions.
- Visualize key signals with interactive, recruiter-friendly dashboards.
- Support economic intelligence, policy foresight, and global risk monitoring use cases.

---

## 🧱 Architecture

### 1. **Data Pipeline**
- **Sources**: World Bank, IMF, OPEC, USDA, Korea Customs, ECOS, DAPA, World Steel, SIPRI, etc.
- **Methods**: REST APIs, BeautifulSoup/Selenium scraping, PDF parsing, CSV ingestion.
- **Processing**:
  - Clean, normalize, standardize all inputs.
  - Load to **PostgreSQL** under a unified schema `unified_macro_view`.
  - Key columns: `date`, `sector`, `indicator`, `country`, `partner`, `value`, `unit`, `domain`, etc.

### 2. **Insight Engine**
- Uses **Google Gemini LLM** to analyze:
  - 📊 Core Trends
  - 🔍 Hidden Effects
  - 🎯 Strategic Recommendations
  - ⚠️ Risk Assessments
  - 📈 Market Intelligence
- Prompts are engineered with sector-specific metadata, summaries, and trend descriptors.

### 3. **Interactive Dashboards**
- Built using **Streamlit** + **Plotly**
- Features:
  - Dual-axis trends
  - Volatility rankings
  - Growth analysis
  - Sector-specific layouts
- Fully responsive and visually optimized for recruiters and decision-makers.

---

## 🛠️ Tech Stack

| Area         | Tools                                          |
|--------------|------------------------------------------------|
| Backend      | Python, PostgreSQL, SQLAlchemy, Docker         |
| ETL          | Pandas, NumPy, batch loaders                   |
| AI & Insight | Gemini LLM, Google Generative AI API           |
| Frontend     | Streamlit, Plotly, custom HTML/CSS             |
| Deployment   | Streamlit Cloud, Docker Compose (local dev)    |

---

## 🎯 Core Skills Demonstrated

| Domain        | Focus                                         |
|---------------|-----------------------------------------------|
| Data & AI     | ETL pipelines, LLM prompt engineering          |
| Visualization | UI/UX design, dynamic dashboards               |
| Strategy      | Economic signal detection, trade intelligence  |
| Engineering   | Containerization, modular pipelines            |

---

## 📊 Coverage

- ✅ **7 Sector Dashboards**:
  - 🌾 Agriculture
  - 🛡 Defence
  - 💹 Economy
  - ⚡ Energy
  - 🌍 Global Trade
  - 🇰🇷 Korea Trade
  - 🏭 Industry

- ✅ **92 Standardized Indicators**
- ✅ **160K+ Data Records**
- ✅ Real-time AI insight generation with sector sub-tabs

---

## 📌 Why It Matters

This platform bridges the gap between raw data and strategic understanding by combining:
- Full-stack engineering
- Economic logic
- Generative AI

It is tailored for roles in:
- Strategic Data Analysis
- Economic Intelligence
- AI Product or Data Product Management

---

## 📎 Contact

For questions, feedback, or opportunities:
- 📧 [https://www.linkedin.com/in/jaeha-kim16]
- 🔗 [LinkedIn/GitHub](https://github.com/emailoneid)

---

## ✅ To Run Locally

```bash
# Clone the repo
git clone https://github.com/emailoneid/Global_Macro_Insight_Engine
cd global-macro-engine

# Setup environment variables
cp .env.example .env
# (Fill in your DB credentials, Gemini API key, etc.)

# Run Streamlit
streamlit run app/Home.py
