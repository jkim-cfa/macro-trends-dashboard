# 🌐 Global Macro Insight Engine  
*A Data Pipeline for Second-Order Macroeconomic Intelligence*  
**Automates the collection, analysis, and interpretation of global economic data—revealing hidden trends and cascading effects.**  

---

## 📌 Key Features  
✔ **Automated Data Ingestion** – APIs, web scraping, and PDF parsing (IEA, IMF, Bank of Korea, USDA)  
✔ **Second-Order Insight Generation** – Identifies ripple effects across sectors (e.g., *steel production → shipping rates*)  
✔ **Structured Metadata & Cataloguing** – Standardised taxonomy for indicators (country, sector, unit, source)  
✔ **AI-Powered Analysis** *(Planned)* – NLP summarisation of central bank reports using LangChain/OpenAI  

---

## 🧠 Why Second-Order Thinking?  
Traditional macro tracking asks: *"What happened?"*  
This project answers: *"What will happen next?"*  

**Example:**  
```
↓ Chinese factory activity slows  
→ Reduced demand for Australian iron ore  
→ Dry bulk freight rates decline (BDI Index)  
→ Shipping companies defer new vessel orders  
→ Shipyard stocks underperform  
```
---

## 🛠️ Tech Stack  
| Layer                | Tools                                                                 |  
|----------------------|-----------------------------------------------------------------------|  
| **Data Extraction**  | `requests`, `BeautifulSoup`, `selenium`, `PyMuPDF` (PDFs)            |  
| **Data Processing**  | `pandas`, `numpy`, `openpyxl`                                        |  
| **AI/NLP**           | `LangChain`, `transformers`, OpenAI API *(Planned)*                  |  
| **Orchestration**    | Custom scripts → **Airflow** *(Planned)*                             |  
| **Visualisation**    | `Streamlit` *(Planned)*                                              |  

---

## 🔄 Pipeline Architecture  
```mermaid  
graph LR  
A[Raw Data] --> B(Extract: APIs/Scraping/PDFs)  
B --> C(Transform: Clean, Metadata, Normalise)  
C --> D[Structured CSV/DB]  
D --> E(Analyse: Second-Order Logic)  
E --> F[Insights Dashboard]  
```  

## 🔄 Pipeline Architecture  

1. **Extract**  
   - **Government/Institutional Sources**  
     - `ECOS` (Bank of Korea):  
       - Economy confidence indices  
       - Leading/coincident indicators  
       - FX rates  
       - Manufacturing inventories  
       - Trade statistics (YoY by country/item)  
     - `USDA`: Crop production data (wheat, corn, soybean, etc.)  
     - `IEA`: Monthly oil stock reports  
     - `Defense Acquisition Program Administration`: Bid information  

   - **Trade/Industry Reports**  
     - `KOTRA`:  
       - Global/Korean export/import trends  
       - Top commodity flows  
       - Trade partner variations  
     - `World Steel Association`: Regional steel production  
     - `WSTS`: Semiconductor billing statistics  

   - **Energy Markets**  
     - `PetroNet`: Korean oil imports by origin  
     - `OPEC`: Monthly Oil Market Reports (PDF)  

   - **Shipping/Logistics**  
     - `KCLA`: Daily shipping indices (CCFI, SCFI, BDI)  

2. **Transform**  
   - Standardise date formats and units  
   - Add metadata tags (sector, geography, frequency)  
   - Handle multi-language fields (Korean/English)  

3. **Analyse** *(Planned)*  
   - Cross-dataset correlations (e.g., steel production → shipping rates)  
   - NLP processing for PDF reports (OPEC, WSTS)  

4. **Visualise** *(Planned)*  
   - Commodity flow dashboards  
   - Leading indicator alerts  

---

## 🔭 Roadmap  
- [ ] **PDF Insight Extraction** 
- [ ] **Airflow Orchestration** 
- [ ] **Streamlit Dashboard**
- [ ] **Forecasting Module**

--- 
