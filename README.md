![Landing Page](https://github.com/user-attachments/assets/5e288bfa-a94b-4681-921e-1261a9856b9b)

# 🛰️ Global Macro Insight Engine
[![Streamlit App](https://img.shields.io/badge/Live--Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://globalengine.streamlit.app/)
[![GitHub](https://img.shields.io/badge/Code--Repo-GitHub-181717?logo=github)](https://github.com/emailoneid/Global_Macro_Insight_Engine)
[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jaeha-kim16)

An AI-powered macroeconomic intelligence platform that integrates structured datasets and routinely updated sector insights to reveal second-order effects, uncover strategic signals, and guide economic, trade, and defense analysis through interactive dashboards and LLM-driven interpretation.

---

## 🚀 Project Summary

**Global Macro Insight Engine** is a full-stack data intelligence system designed to:

* Ingest and normalize macroeconomic, trade, defense, and energy data from authoritative global sources.
* Generate sector-level insights using large language models (LLMs) tuned for economic reasoning.
* Visualize patterns, anomalies, and trends via interactive dashboards.
* Enable data-driven decision-making in strategic analysis and policy contexts.

---

## 🧱 Architecture

### 1. **Data Pipeline**

* **Sources**: World Bank, IMF, OPEC, USDA, Korea Customs, ECOS, DAPA, World Steel, SIPRI, and more.
* **Methods**: API calls, web scraping, PDF parsing, and CSV ingestion using Python.
* **Processing Flow**:

  * Clean and normalize input data.
  * Load into **PostgreSQL** under the `unified_macro_view` schema.
  * Use standard fields: `date`, `sector`, `indicator`, `country`, `partner`, `value`, `unit`, `domain`, etc.

### 2. **Insight Engine**

* Powered by **Google Gemini LLM** to produce:

  * 📊 Trend Summaries
  * 🔍 Second-Order Implications
  * 🎯 Strategic Recommendations
  * ⚠️ Risk Flags
  * 📈 Market Signals
* Each prompt is auto-generated using metadata, summaries, and multi-period performance features.

### 3. **Interactive Dashboards**

* Built with **Streamlit** + **Plotly** for flexible exploration:

  * Dual-axis time series
  * Top movers and volatility filters
  * Sectoral decomposition
  * Downloadable filtered tables and visuals

---

## 🛠️ Tech Stack

| Layer         | Tools                                            |
| ------------- | ------------------------------------------------ |
| Backend       | Python, PostgreSQL, SQLAlchemy, Docker           |
| ETL           | Pandas, NumPy, scraping modules                  |
| AI & Insights | Gemini LLM, Google Generative AI API             |
| Frontend      | Streamlit, Plotly, enhanced with HTML/CSS        |
| Deployment    | Streamlit Cloud (production), Docker (local dev) |

---

## 🎯 Core Skills Demonstrated

| Domain        | Focus                                              |
| ------------- | -------------------------------------------------- |
| Data & AI     | ETL automation, prompt engineering for LLMs        |
| Visualization | Recruiter-facing UI/UX, modular layouts            |
| Strategy      | Economic signal analysis, policy relevance mapping |
| Engineering   | Modular codebase, containerized deployment         |

---

## 📊 Coverage

* ✅ **7 Sector Dashboards**:

  * 🌾 Agriculture
  * 🛡 Defence
  * 💹 Economy
  * ⚡ Energy
  * 🌍 Global Trade
  * 🇰🇷 Korea Trade
  * 🏭 Industry

* ✅ **92 Harmonized Indicators**

* ✅ **160,000+ Records in Unified View**

* ✅ Sector-level Gemini AI Insight Generation

---

## 📸 Screenshots

### 🗂️ Sector Summary Page

<img src="https://github.com/user-attachments/assets/1f4a19b0-c579-477b-8b8b-ece6a98eab6d" width="700"/>
<p><em>Sector summaries, database stats, and navigation entry point.</em></p>

---

### 🌍 Sector Dashboards

<img src="https://github.com/user-attachments/assets/6c684410-8d4d-42fc-9728-a600cb6c6be1" width="700"/>
<img src="https://github.com/user-attachments/assets/5377587a-d6eb-43e7-b4d4-d0877507c6cc" width="700"/>
<img src="https://github.com/user-attachments/assets/c87ad141-d4bf-4427-8819-ca68b97b9b81" width="700"/>
<p><em>Sector-specific dashboards with dynamic filters, dual-axis time series, and category breakdowns to surface key trends and top contributors.</em></p>

---

### 📈 Economic Indicators & Searchable Tables

<img src="https://github.com/user-attachments/assets/4e587d35-9289-4c17-affa-58387f7fed11" width="700"/>
<img src="https://github.com/user-attachments/assets/cbba2346-d2ab-402c-a8a4-d4143175d782" width="700"/>
<p><em>Drill-down views with downloadable tables and keyword search filters.</em></p>

---

### 🧠 Gemini AI Insight Panel

<img src="https://github.com/user-attachments/assets/a8f2a6f8-08a9-4564-94ea-34a634260829" width="700"/>
<p><em>Automatically generated strategic insights based on LLM reasoning.</em></p>

---

## 📌 Why It Matters

This project demonstrates the convergence of:

* Data engineering and AI analysis
* Domain-specific signal detection
* High-impact storytelling via dashboards

Ideal for roles in:

* Strategic Data Analysis
* Economic/Policy Intelligence
* AI or Data Product Management

---

## 📎 Contact

For questions, feedback, or opportunities:

* 📧 [LinkedIn – Jaeha Kim](https://www.linkedin.com/in/jaeha-kim16)
* 🔗 [GitHub – emailoneid](https://github.com/emailoneid)

---

## ✅ To Run Locally

```bash
# Clone the repo
git clone https://github.com/emailoneid/Global_Macro_Insight_Engine
cd global-macro-engine

# Setup environment variables
cp .env.example .env
# (Add your DB credentials and Gemini API key)

# Launch the app
streamlit run app/Home.py
```
