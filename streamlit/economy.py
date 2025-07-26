import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="Korean Economic Indicators EDA", layout="wide")

st.title("🇰🇷 South Korean Economic Indicators - Exploratory Data Analysis")
st.markdown("*Analysis of Exchange Rates, Economic Indices, and Sentiment Indicators*")

# Load and prepare data
@st.cache_data
def load_data():
    # FX Rates data
    fx_data = """2024-01-01	South Korea	economy	EUR	KRW	1444.12	원	ECOS
2024-01-01	South Korea	economy	EUR	USD	1.09113	달러	ECOS
2024-01-01	South Korea	economy	JPY	KRW	906.71	원	ECOS
2024-01-01	South Korea	economy	USD	KRW	1323.57	원	ECOS
2024-02-01	South Korea	economy	CNY	KRW	184.82	원	ECOS
2024-02-01	South Korea	economy	EUR	KRW	1437.52	원	ECOS
2024-02-01	South Korea	economy	EUR	USD	1.07943	달러	ECOS
2024-02-01	South Korea	economy	JPY	KRW	891.08	원	ECOS
2024-02-01	South Korea	economy	USD	KRW	1331.74	원	ECOS
2024-03-01	South Korea	economy	CNY	KRW	184.48	원	ECOS
2024-03-01	South Korea	economy	EUR	KRW	1447.27	원	ECOS
2024-03-01	South Korea	economy	EUR	USD	1.08763	달러	ECOS
2024-03-01	South Korea	economy	JPY	KRW	889.12	원	ECOS
2024-03-01	South Korea	economy	USD	KRW	1330.69	원	ECOS
2024-04-01	South Korea	economy	CNY	KRW	188.52	원	ECOS
2024-04-01	South Korea	economy	EUR	KRW	1466.77	원	ECOS
2024-04-01	South Korea	economy	EUR	USD	1.0724	달러	ECOS
2024-04-01	South Korea	economy	JPY	KRW	889.97	원	ECOS
2024-04-01	South Korea	economy	USD	KRW	1367.83	원	ECOS
2024-05-01	South Korea	economy	CNY	KRW	188.54	원	ECOS
2024-05-01	South Korea	economy	EUR	KRW	1476.24	원	ECOS
2024-05-01	South Korea	economy	EUR	USD	1.0812	달러	ECOS
2024-05-01	South Korea	economy	JPY	KRW	875.88	원	ECOS
2024-05-01	South Korea	economy	USD	KRW	1365.39	원	ECOS
2024-06-01	South Korea	economy	CNY	KRW	189.8	원	ECOS
2024-06-01	South Korea	economy	EUR	KRW	1485.57	원	ECOS
2024-06-01	South Korea	economy	EUR	USD	1.07642	달러	ECOS
2024-06-01	South Korea	economy	JPY	KRW	874.32	원	ECOS
2024-06-01	South Korea	economy	USD	KRW	1380.13	원	ECOS
2024-07-01	South Korea	economy	CNY	KRW	189.91	원	ECOS
2024-07-01	South Korea	economy	EUR	KRW	1499.68	원	ECOS
2024-07-01	South Korea	economy	EUR	USD	1.08407	달러	ECOS
2024-07-01	South Korea	economy	JPY	KRW	875.3	원	ECOS
2024-07-01	South Korea	economy	USD	KRW	1383.38	원	ECOS
2024-08-01	South Korea	economy	CNY	KRW	189.07	원	ECOS
2024-08-01	South Korea	economy	EUR	KRW	1491.48	원	ECOS
2024-08-01	South Korea	economy	EUR	USD	1.10156	달러	ECOS
2024-08-01	South Korea	economy	JPY	KRW	925.99	원	ECOS
2024-08-01	South Korea	economy	USD	KRW	1354.15	원	ECOS
2024-09-01	South Korea	economy	CNY	KRW	188.53	원	ECOS
2024-09-01	South Korea	economy	EUR	KRW	1481.6	원	ECOS
2024-09-01	South Korea	economy	EUR	USD	1.10998	달러	ECOS
2024-09-01	South Korea	economy	JPY	KRW	929.25	원	ECOS
2024-09-01	South Korea	economy	USD	KRW	1334.82	원	ECOS
2024-10-01	South Korea	economy	CNY	KRW	191.63	원	ECOS
2024-10-01	South Korea	economy	EUR	KRW	1481.35	원	ECOS
2024-10-01	South Korea	economy	EUR	USD	1.08856	달러	ECOS
2024-10-01	South Korea	economy	JPY	KRW	906.77	원	ECOS
2024-10-01	South Korea	economy	USD	KRW	1361	원	ECOS
2024-11-01	South Korea	economy	CNY	KRW	193.27	원	ECOS
2024-11-01	South Korea	economy	EUR	KRW	1482.93	원	ECOS
2024-11-01	South Korea	economy	EUR	USD	1.06435	달러	ECOS
2024-11-01	South Korea	economy	JPY	KRW	907.16	원	ECOS
2024-11-01	South Korea	economy	USD	KRW	1393.38	원	ECOS
2024-12-01	South Korea	economy	CNY	KRW	196.93	원	ECOS
2024-12-01	South Korea	economy	EUR	KRW	1502.63	원	ECOS
2024-12-01	South Korea	economy	EUR	USD	1.04762	달러	ECOS
2024-12-01	South Korea	economy	JPY	KRW	934.25	원	ECOS
2024-12-01	South Korea	economy	USD	KRW	1434.42	원	ECOS
2025-01-01	South Korea	economy	CNY	KRW	198.71	원	ECOS
2025-01-01	South Korea	economy	EUR	KRW	1504.11	원	ECOS
2025-01-01	South Korea	economy	EUR	USD	1.03322	달러	ECOS
2025-01-01	South Korea	economy	JPY	KRW	927.97	원	ECOS
2025-01-01	South Korea	economy	USD	KRW	1455.79	원	ECOS
2025-02-01	South Korea	economy	CNY	KRW	198.43	원	ECOS
2025-02-01	South Korea	economy	EUR	KRW	1505.44	원	ECOS
2025-02-01	South Korea	economy	EUR	USD	1.04146	달러	ECOS
2025-02-01	South Korea	economy	JPY	KRW	952.59	원	ECOS
2025-02-01	South Korea	economy	USD	KRW	1445.56	원	ECOS
2025-03-01	South Korea	economy	CNY	KRW	200.79	원	ECOS
2025-03-01	South Korea	economy	EUR	KRW	1575.91	원	ECOS
2025-03-01	South Korea	economy	EUR	USD	1.08167	달러	ECOS
2025-03-01	South Korea	economy	JPY	KRW	977.77	원	ECOS
2025-03-01	South Korea	economy	USD	KRW	1456.95	원	ECOS
2025-04-01	South Korea	economy	CNY	KRW	197.7	원	ECOS
2025-04-01	South Korea	economy	EUR	KRW	1617.71	원	ECOS
2025-04-01	South Korea	economy	EUR	USD	1.12034	달러	ECOS
2025-04-01	South Korea	economy	JPY	KRW	999.96	원	ECOS
2025-04-01	South Korea	economy	USD	KRW	1444.31	원	ECOS
2025-05-01	South Korea	economy	CNY	KRW	193.37	원	ECOS
2025-05-01	South Korea	economy	EUR	KRW	1571.45	원	ECOS
2025-05-01	South Korea	economy	EUR	USD	1.12694	달러	ECOS
2025-05-01	South Korea	economy	JPY	KRW	962.28	원	ECOS
2025-05-01	South Korea	economy	USD	KRW	1394.49	원	ECOS
2025-06-01	South Korea	economy	CNY	KRW	190.3	원	ECOS
2025-06-01	South Korea	economy	EUR	KRW	1574.56	원	ECOS
2025-06-01	South Korea	economy	EUR	USD	1.15191	달러	ECOS
2025-06-01	South Korea	economy	JPY	KRW	944.94	원	ECOS
2025-06-01	South Korea	economy	USD	KRW	1366.95	원	ECOS"""
    
    # Leading indicators data
    leading_data = """2023-08-01	South Korea	economy	선행-동행	-0.6	index	ECOS
2023-09-01	South Korea	economy	KOSPI	2465.070068	index	ECOS
2023-09-01	South Korea	economy	동행지수순환변동치	100.3	index	ECOS
2023-09-01	South Korea	economy	선행지수순환변동치	99.8	index	ECOS
2023-09-01	South Korea	economy	선행-동행	-0.5	index	ECOS
2023-10-01	South Korea	economy	KOSPI	2277.98999	index	ECOS
2023-10-01	South Korea	economy	동행지수순환변동치	100.3	index	ECOS
2023-10-01	South Korea	economy	선행지수순환변동치	100	index	ECOS
2023-10-01	South Korea	economy	선행-동행	-0.3	index	ECOS
2023-11-01	South Korea	economy	KOSPI	2535.290039	index	ECOS
2023-11-01	South Korea	economy	동행지수순환변동치	100.4	index	ECOS
2023-11-01	South Korea	economy	선행지수순환변동치	100.2	index	ECOS
2023-11-01	South Korea	economy	선행-동행	-0.2	index	ECOS
2023-12-01	South Korea	economy	KOSPI	2655.280029	index	ECOS
2023-12-01	South Korea	economy	동행지수순환변동치	100.2	index	ECOS
2023-12-01	South Korea	economy	선행지수순환변동치	100.4	index	ECOS
2023-12-01	South Korea	economy	선행-동행	0.2	index	ECOS
2024-01-01	South Korea	economy	KOSPI	2497.090088	index	ECOS
2024-01-01	South Korea	economy	동행지수순환변동치	100.3	index	ECOS
2024-01-01	South Korea	economy	선행지수순환변동치	100.4	index	ECOS
2024-01-01	South Korea	economy	선행-동행	0.1	index	ECOS
2024-02-01	South Korea	economy	KOSPI	2642.360107	index	ECOS
2024-02-01	South Korea	economy	동행지수순환변동치	100.3	index	ECOS
2024-02-01	South Korea	economy	선행지수순환변동치	100.6	index	ECOS
2024-02-01	South Korea	economy	선행-동행	0.3	index	ECOS
2024-03-01	South Korea	economy	KOSPI	2746.629883	index	ECOS
2024-03-01	South Korea	economy	동행지수순환변동치	100.1	index	ECOS
2024-03-01	South Korea	economy	선행지수순환변동치	100.5	index	ECOS
2024-03-01	South Korea	economy	선행-동행	0.4	index	ECOS
2024-04-01	South Korea	economy	KOSPI	2692.060059	index	ECOS
2024-04-01	South Korea	economy	동행지수순환변동치	100	index	ECOS
2024-04-01	South Korea	economy	선행지수순환변동치	100.7	index	ECOS
2024-04-01	South Korea	economy	선행-동행	0.7	index	ECOS
2024-05-01	South Korea	economy	KOSPI	2636.52002	index	ECOS
2024-05-01	South Korea	economy	동행지수순환변동치	99.7	index	ECOS
2024-05-01	South Korea	economy	선행지수순환변동치	100.8	index	ECOS
2024-05-01	South Korea	economy	선행-동행	1.1	index	ECOS
2024-06-01	South Korea	economy	KOSPI	2797.820068	index	ECOS
2024-06-01	South Korea	economy	동행지수순환변동치	99.6	index	ECOS
2024-06-01	South Korea	economy	선행지수순환변동치	100.9	index	ECOS
2024-06-01	South Korea	economy	선행-동행	1.3	index	ECOS
2024-07-01	South Korea	economy	KOSPI	2770.689941	index	ECOS
2024-07-01	South Korea	economy	동행지수순환변동치	99.1	index	ECOS
2024-07-01	South Korea	economy	선행지수순환변동치	100.9	index	ECOS
2024-07-01	South Korea	economy	선행-동행	1.8	index	ECOS
2024-08-01	South Korea	economy	KOSPI	2674.310059	index	ECOS
2024-08-01	South Korea	economy	동행지수순환변동치	99	index	ECOS
2024-08-01	South Korea	economy	선행지수순환변동치	100.8	index	ECOS
2024-08-01	South Korea	economy	선행-동행	1.8	index	ECOS
2024-09-01	South Korea	economy	KOSPI	2593.27002	index	ECOS
2024-09-01	South Korea	economy	동행지수순환변동치	99	index	ECOS
2024-09-01	South Korea	economy	선행지수순환변동치	100.8	index	ECOS
2024-09-01	South Korea	economy	선행-동행	1.8	index	ECOS
2024-10-01	South Korea	economy	KOSPI	2556.149902	index	ECOS
2024-10-01	South Korea	economy	동행지수순환변동치	99.3	index	ECOS
2024-10-01	South Korea	economy	선행지수순환변동치	100.8	index	ECOS
2024-10-01	South Korea	economy	선행-동행	1.5	index	ECOS
2024-11-01	South Korea	economy	KOSPI	2455.909912	index	ECOS
2024-11-01	South Korea	economy	동행지수순환변동치	98.9	index	ECOS
2024-11-01	South Korea	economy	선행지수순환변동치	100.8	index	ECOS
2024-11-01	South Korea	economy	선행-동행	1.9	index	ECOS
2024-12-01	South Korea	economy	KOSPI	2399.48999	index	ECOS
2024-12-01	South Korea	economy	동행지수순환변동치	98.8	index	ECOS
2024-12-01	South Korea	economy	선행지수순환변동치	100.7	index	ECOS
2024-12-01	South Korea	economy	선행-동행	1.9	index	ECOS
2025-01-01	South Korea	economy	KOSPI	2517.370117	index	ECOS
2025-01-01	South Korea	economy	동행지수순환변동치	98.4	index	ECOS
2025-01-01	South Korea	economy	선행지수순환변동치	100.3	index	ECOS
2025-01-01	South Korea	economy	선행-동행	1.9	index	ECOS
2025-02-01	South Korea	economy	KOSPI	2532.780029	index	ECOS
2025-02-01	South Korea	economy	동행지수순환변동치	98.5	index	ECOS
2025-02-01	South Korea	economy	선행지수순환변동치	100.4	index	ECOS
2025-02-01	South Korea	economy	선행-동행	1.9	index	ECOS
2025-03-01	South Korea	economy	KOSPI	2481.120117	index	ECOS
2025-03-01	South Korea	economy	동행지수순환변동치	98.7	index	ECOS
2025-03-01	South Korea	economy	선행지수순환변동치	100.6	index	ECOS
2025-03-01	South Korea	economy	선행-동행	1.9	index	ECOS
2025-04-01	South Korea	economy	KOSPI	2556.610107	index	ECOS
2025-04-01	South Korea	economy	동행지수순환변동치	98.9	index	ECOS
2025-04-01	South Korea	economy	선행지수순환변동치	101	index	ECOS
2025-04-01	South Korea	economy	선행-동행	2.1	index	ECOS
2025-05-01	South Korea	economy	KOSPI	2697.669922	index	ECOS
2025-05-01	South Korea	economy	동행지수순환변동치	98.5	index	ECOS
2025-05-01	South Korea	economy	선행지수순환변동치	100.9	index	ECOS
2025-05-01	South Korea	economy	선행-동행	2.4	index	ECOS"""
    
    # Sentiment data
    sentiment_data = """2024-11-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	93	index	ECOS
2024-11-01	South Korea	economy	뉴스심리지수	뉴스심리지수	100.47	index	ECOS
2024-12-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	90.1	index	ECOS
2024-12-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	83.3	index	ECOS
2024-12-01	South Korea	economy	뉴스심리지수	뉴스심리지수	85.75	index	ECOS
2025-01-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	89.5	index	ECOS
2025-01-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	86.7	index	ECOS
2025-01-01	South Korea	economy	뉴스심리지수	뉴스심리지수	99.32	index	ECOS
2025-02-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	89.1	index	ECOS
2025-02-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	90.2	index	ECOS
2025-02-01	South Korea	economy	뉴스심리지수	뉴스심리지수	99.85	index	ECOS
2025-03-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	89	index	ECOS
2025-03-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	87.2	index	ECOS
2025-03-01	South Korea	economy	뉴스심리지수	뉴스심리지수	93.73	index	ECOS
2025-04-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	88.9	index	ECOS
2025-04-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	87.5	index	ECOS
2025-04-01	South Korea	economy	뉴스심리지수	뉴스심리지수	97.94	index	ECOS
2025-05-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	89.1	index	ECOS
2025-05-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	92.2	index	ECOS
2025-05-01	South Korea	economy	뉴스심리지수	뉴스심리지수	101.71	index	ECOS
2025-06-01	South Korea	economy	경제심리지수	경제심리지수(순환변동치)	89.3	index	ECOS
2025-06-01	South Korea	economy	경제심리지수	경제심리지수(원계열)	92.8	index	ECOS
2025-06-01	South Korea	economy	뉴스심리지수	뉴스심리지수	107.96	index	ECOS
2025-07-01	South Korea	economy	뉴스심리지수	뉴스심리지수	107.29	index	ECOS"""
    
    # Parse FX data
    fx_lines = fx_data.strip().split('\n')
    fx_df = pd.DataFrame([line.split('\t') for line in fx_lines], 
                        columns=['date', 'country', 'sector', 'currency', 'quote', 'exchange_rate', 'unit', 'source'])
    fx_df['date'] = pd.to_datetime(fx_df['date'])
    fx_df['exchange_rate'] = pd.to_numeric(fx_df['exchange_rate'])
    fx_df['pair'] = fx_df['currency'] + '/' + fx_df['quote']
    
    # Parse leading indicators data
    leading_lines = leading_data.strip().split('\n')
    leading_df = pd.DataFrame([line.split('\t') for line in leading_lines], 
                             columns=['date', 'country', 'sector', 'indicator', 'value', 'unit', 'source'])
    leading_df['date'] = pd.to_datetime(leading_df['date'])
    leading_df['value'] = pd.to_numeric(leading_df['value'])
    
    # Parse sentiment data
    sentiment_lines = sentiment_data.strip().split('\n')
    sentiment_df = pd.DataFrame([line.split('\t') for line in sentiment_lines], 
                               columns=['date', 'country', 'sector', 'category', 'indicator', 'value', 'unit', 'source'])
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df['value'] = pd.to_numeric(sentiment_df['value'])
    
    return fx_df, leading_df, sentiment_df

fx_df, leading_df, sentiment_df = load_data()

# Sidebar for navigation
st.sidebar.title("📊 Analysis Sections")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis Type:",
    ["📈 Overview & Summary", "💱 Exchange Rate Analysis", "📊 Leading Indicators", "🎭 Sentiment Analysis", "🔗 Cross-Correlation Analysis"]
)

if analysis_type == "📈 Overview & Summary":
    st.header("📈 Data Overview & Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("FX Pairs", len(fx_df['pair'].unique()))
        st.metric("Leading Indicators", len(leading_df['indicator'].unique()))
    
    with col2:
        st.metric("Date Range", f"{fx_df['date'].min().strftime('%Y-%m')} to {fx_df['date'].max().strftime('%Y-%m')}")
        st.metric("Sentiment Indicators", len(sentiment_df['indicator'].unique()))
    
    with col3:
        st.metric("Total Data Points", len(fx_df) + len(leading_df) + len(sentiment_df))
        st.metric("Data Sources", "ECOS")
    
    st.subheader("📋 Data Structure Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Exchange Rates**")
        st.dataframe(fx_df.head(), use_container_width=True)
        
    with col2:
        st.write("**Leading Indicators**")
        st.dataframe(leading_df.head(), use_container_width=True)
        
    with col3:
        st.write("**Sentiment Indicators**")
        st.dataframe(sentiment_df.head(), use_container_width=True)

elif analysis_type == "💱 Exchange Rate Analysis":
    st.header("💱 Exchange Rate Analysis")
    
    # Time series of all exchange rates
    fig = make_subplots(rows=2, cols=2, 
                       subplot_titles=('USD/KRW', 'EUR/KRW', 'JPY/KRW', 'CNY/KRW'),
                       vertical_spacing=0.1)
    
    pairs = ['USD/KRW', 'EUR/KRW', 'JPY/KRW', 'CNY/KRW']
    colors = ['blue', 'green', 'red', 'orange']
    
    for i, (pair, color) in enumerate(zip(pairs, colors)):
        data = fx_df[fx_df['pair'] == pair].sort_values('date')
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['exchange_rate'], 
                      name=pair, line=dict(color=color)),
            row=row, col=col
        )
    
    fig.update_layout(height=600, title_text="Exchange Rate Trends (2024-2025)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Volatility analysis
    st.subheader("📊 Exchange Rate Volatility")
    
    volatility_data = []
    for pair in pairs:
        data = fx_df[fx_df['pair'] == pair].sort_values('date')
        if len(data) > 1:
            returns = data['exchange_rate'].pct_change().dropna()
            volatility = returns.std() * 100
            min_rate = data['exchange_rate'].min()
            max_rate = data['exchange_rate'].max()
            current_rate = data['exchange_rate'].iloc[-1]
            
            volatility_data.append({
                'Currency Pair': pair,
                'Volatility (%)': round(volatility, 2),
                'Min Rate': round(min_rate, 2),
                'Max Rate': round(max_rate, 2),
                'Current Rate': round(current_rate, 2),
                'Range (%)': round(((max_rate - min_rate) / min_rate) * 100, 2)
            })
    
    volatility_df = pd.DataFrame(volatility_data)
    st.dataframe(volatility_df, use_container_width=True)
    
    # EUR/USD special analysis
    st.subheader("🌍 EUR/USD Analysis")
    eur_usd_data = fx_df[fx_df['pair'] == 'EUR/USD'].sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=eur_usd_data['date'], y=eur_usd_data['exchange_rate'],
                            mode='lines+markers', name='EUR/USD',
                            line=dict(color='purple', width=3)))
    fig.update_layout(title='EUR/USD Exchange Rate (2024-2025)',
                      xaxis_title='Date',
                      yaxis_title='Exchange Rate',
                      height=400)
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "📊 Leading Indicators":
    st.header("📊 Leading & Coincident Indicators")
    
    indicators = leading_df['indicator'].unique()
    selected = st.selectbox("Select an Indicator", indicators)
    
    fig = px.line(
        leading_df[leading_df['indicator'] == selected].sort_values("date"),
        x='date', y='value',
        title=f"{selected} Trend",
        markers=True
    )
    fig.update_layout(height=500, yaxis_title="Index", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 All Indicators Comparison")
    pivot_df = leading_df.pivot(index='date', columns='indicator', values='value')
    st.line_chart(pivot_df)

elif analysis_type == "🎭 Sentiment Analysis":
    st.header("🎭 Economic Sentiment Indicators")
    
    selected_sent = st.selectbox("Select a Sentiment Indicator", sentiment_df['indicator'].unique())
    fig = px.line(
        sentiment_df[sentiment_df['indicator'] == selected_sent].sort_values("date"),
        x='date', y='value',
        title=f"{selected_sent} Trend",
        markers=True
    )
    fig.update_layout(height=500, yaxis_title="Index", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Indicator Overview")
    pivot_sentiment = sentiment_df.pivot(index='date', columns='indicator', values='value')
    st.line_chart(pivot_sentiment)

elif analysis_type == "🔗 Cross-Correlation Analysis":
    st.header("🔗 Cross-Correlation: Exchange Rates vs. KOSPI")
    
    # Merge KOSPI with USD/KRW
    kospi = leading_df[leading_df['indicator'] == 'KOSPI'][['date', 'value']].rename(columns={'value': 'KOSPI'})
    usdkrw = fx_df[fx_df['pair'] == 'USD/KRW'][['date', 'exchange_rate']].rename(columns={'exchange_rate': 'USD/KRW'})
    
    merged = pd.merge(kospi, usdkrw, on='date')
    corr = merged.corr().iloc[0, 1]
    
    st.metric("📈 Correlation (USD/KRW ↔ KOSPI)", f"{corr:.2f}")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=merged['date'], y=merged['KOSPI'], name='KOSPI', line=dict(color='blue')), secondary_y=False)
    fig.add_trace(go.Scatter(x=merged['date'], y=merged['USD/KRW'], name='USD/KRW', line=dict(color='orange')), secondary_y=True)
    
    fig.update_layout(title="KOSPI vs. USD/KRW", height=500)
    fig.update_yaxes(title_text="KOSPI", secondary_y=False)
    fig.update_yaxes(title_text="USD/KRW", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
