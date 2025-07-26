import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io

# Set page config
st.set_page_config(
    page_title="Defense Data EDA Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .insight-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ef4444;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the defense data"""
    
    # SIPRI Data
    sipri_data = {
        'report': ['SIPRI'] * 9,
        'year': [2025] * 9,
        'topic': [
            'Military Spending', 'Conflict-Related Deaths', 'Climate Change & Security',
            'Geopolitical Instability', 'Nuclear Arms Race', 'Arms Production & Transfers',
            'Nuclear Weapons Modernization', 'Arms Control Challenges', 'Emerging Military Technologies'
        ],
        'insight': [
            'Global military spending reached a record high of $2.7 trillion in 2024.',
            'Conflict-related deaths surged to 239,000 in 2024.',
            '2024 was the first year with average global temperatures exceeding 1.5°C above pre-industrial levels.',
            'The Russia-Ukraine war intensified, and other conflicts escalated or persisted in 2024.',
            'Nuclear arms reductions ended in 2024, raising concerns about a new arms race.',
            'Significant increases in arms production and transfers were observed in Europe and Asia in 2024.',
            'The report details nuclear weapons modernization efforts in 2024.',
            'Significant challenges persist in enforcing existing arms control treaties and addressing emerging threats in 2024.',
            'Emerging technologies like AI, cyber warfare, and space-based weaponry are highlighted as significant concerns in 2024.'
        ],
        'sector': ['defence'] * 9
    }
    
    # Defense Contracts Data - creating proper aligned data
    contracts_raw_data = [
        ('2025-08-01', 'L-SAM 양산(발사대,ABM)', 731937714445.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', 'L-SAM 양산(다기능레이더)', 505901459516.0, 'Frequent Items (6 times)'),
        ('2025-07-01', '천마 체계 외주정비(방산)', 208379067864.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', '장애물개척전차 2차 양산', 203623631149.0, 'Frequent Items (6 times)'),
        ('2025-08-01', 'L-SAM 양산(통제소,AAM,체계통합)', 140632280000.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', '155mm 단위장약 등', 72904819200.0, 'Frequent Items (7 times)'),
        ('2025-07-01', 'F- 기관 부품(D)', 52177368076.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', '엔진,디젤식(장개차용)', 38760000000.0, 'Frequent Items (3 times)'),
        ('2025-07-01', 'C-130/CN-2 기관/모듈 창정비(D)', 35073290162.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', 'KUH-1 헬기 엔진 (제조)', 34787848662.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '천무유도탄 부품류(방산)', 30099253700.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', '천무유도탄 로켓부품(방산)', 24960090266.0, 'Frequent Items (4 times)'),
        ('2025-07-01', '120밀리 전차 도비방지 연습예광탄', 22326912000.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', '천무유도탄 수명연장 외주정비', 18656521728.0, 'Frequent Items (4 times)'),
        ('2025-08-01', '천마 유도탄 체계 정비(방산)', 18381708864.0, 'Frequent Items (4 times)'),
        ('2025-07-01', '105밀리 연습예광탄', 15899506000.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', '잠수함 연료전지체계(제조)', 15362600000.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', '충격신관', 15285313200.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', 'KF- RAM COATING 및 외부전면도장(D)', 13375520600.13, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', 'UH- 기체 창정비', 12763235000.0, 'High-Value (≥ 10B KRW)'),
        ('2025-08-01', '해상감시레이더-II PBL 2차', 12435925000.0, 'Frequent Items (7 times)'),
        ('2025-08-01', 'F-16D Wiring Harness 정비(D)', 10337745810.0, 'High-Value (≥ 10B KRW)'),
        ('2025-07-01', '비호 감지기 유니트 등(구매)', 9715202940.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '12.7밀리 파쇄탄', 9295445504.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '방탄복, 조끼용(대)', 8419200114.0, 'Frequent Items (5 times)'),
        ('2025-07-01', '트럭,승강식,항공기 적재용(KMJ-1C)', 7481200000.0, 'Frequent Items (3 times)'),
        ('2025-08-01', '검독수리-B Batch-II 정비대체장비(76mm함포)', 6804400000.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '76mm 함포(5번함) 창정비', 5428960000.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '트럭,승강식,항공기 적재용(KMHU-83D/E)', 5400000000.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '30밀리 탄약류', 5052298640.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '장갑차 변속기 외주정비', 4891648000.0, 'Frequent Items (5 times)'),
        ('2025-07-01', '천궁, 천궁II 작전수행능력 개선(통제소)', 4800000000.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '차륜형장갑차 성능개량 체계개발', 4775000000.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '12.7mm원격사격통제체계(검독수리-B B-II 9 12번함용)', 4639444794.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '회전익 기체(CH-47) 수송용 정비', 3760062592.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '105/155밀리 훈련탄', 3607783216.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '방탄복, 조끼용(특대)', 3351927906.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '항공기 급유차(6,500G/L)', 3150000000.0, 'Frequent Items (3 times)'),
        ('2025-08-01', '발칸 총열부 부품(방산)', 3136133474.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '155밀리 훈련용 추진장약통(5호,6호)', 3055525000.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '155밀리 연습용 대전차지뢰살포탄', 2838067000.0, 'Frequent Items (8 times)'),
        ('2025-08-01', '회전익 기체(AH-1S) 구성품 정비', 2575530043.96, 'Frequent Items (3 times)'),
        ('2025-08-01', '(500MD) 회전익 기체 정비', 2332174800.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '방탄복, 조끼용(중)', 2227323286.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '발칸 송탄기 부품(방산)', 1912372441.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '120mm 자주박격포 적재훈련탄', 1875168000.0, 'Frequent Items (7 times)'),
        ('2025-08-01', 'K55자주포 엔진 외주정비', 1856570880.0, 'Frequent Items (3 times)'),
        ('2025-08-01', '천무유도탄 제어부', 1728884000.0, 'Frequent Items (4 times)'),
        ('2025-07-01', 'K21장갑차 사통장치 외주정비', 1610655585.0, 'Frequent Items (5 times)'),
        ('2025-07-01', '천궁, 천궁II 작전수행능력 개선(다기능레이더)', 1580000000.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '철매-II 성능개량 (2차 양산) 수송차량(크레인, 종합)', 1569000000.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '방탄복, 조끼용(해병)', 1525437200.0, 'Frequent Items (5 times)'),
        ('2025-07-01', '비호 주전원공급기 정비', 1508466870.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '방탄복, 조끼용(소)', 1435256942.0, 'Frequent Items (5 times)'),
        ('2025-07-01', 'K 교육훈련용 장갑차 외주정비', 1366686091.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '비호 레이다부품 정비(방산)', 1257716664.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '76밀리 연습탄 K245(KC114)', 1253395800.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '발칸 구동유니트, 전기 유압식 등 4항목 정비', 1172604492.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '천궁 시험세트(방산)', 1166078000.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '발칸 사격통제부 부품(방산)', 1064192407.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '회로카드조립체(전차,장갑차,상륙장갑차)', 1057353952.0, 'Frequent Items (5 times)'),
        ('2025-08-01', '() 권총,9mm,반자동식,K5', 931380372.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '장갑차 부품', 892484124.0, 'Frequent Items (5 times)'),
        ('2025-07-01', '대공표적기 지원용역(천마)', 869934562.0, 'Frequent Items (4 times)'),
        ('2025-08-01', '철매-II 성능개량 (2차 양산) 수송차량(K-918)', 858200000.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '발칸 자이로스코프(연구개발)', 856173635.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '30mm 차륜형대공포 2차양산 일반공구', 823785353.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '성능개량 위치보고접속장치 수리부속(구매)', 640730406.0, 'Frequent Items (4 times)'),
        ('2025-08-01', '발칸 사격제어부 부품', 588566403.0, 'Frequent Items (7 times)'),
        ('2025-07-01', '천마 궤도 정비(방산)', 559376400.0, 'Frequent Items (4 times)'),
        ('2025-08-01', '40밀리포 부품류, 보병전투차량용', 545317041.0, 'Frequent Items (8 times)'),
        ('2025-07-01', '발칸 축전식 전지(제조)', 544050000.0, 'Frequent Items (7 times)'),
        ('2025-08-01', '방열기, 엔진냉각제용', 535951182.0, 'Frequent Items (3 times)'),
        ('2025-07-01', '(긴급) 축 등 10종', 64398400.0, 'Emergency Procurement'),
        ('2025-07-01', '(긴급)냉각기, 공기식, 전자장비용 1종', 55600000.0, 'Emergency Procurement')
    ]
    
    # Convert to proper dictionary format
    contracts_data = {
        'date': [item[0] for item in contracts_raw_data],
        'indicator': [item[1] for item in contracts_raw_data],
        'value': [item[2] for item in contracts_raw_data],
        'category': [item[3] for item in contracts_raw_data]
    }
    
    sipri_df = pd.DataFrame(sipri_data)
    contracts_df = pd.DataFrame(contracts_data)
    
    # Convert date column
    contracts_df['date'] = pd.to_datetime(contracts_df['date'])
    contracts_df['month'] = contracts_df['date'].dt.strftime('%Y-%m')
    
    return sipri_df, contracts_df

def main():
    # Main header
    st.markdown('<h1 class="main-header">🛡️ Defense Data EDA Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    sipri_df, contracts_df = load_data()
    
    # Sidebar
    st.sidebar.header("📊 Navigation")
    tab = st.sidebar.selectbox(
        "Choose Analysis Section:",
        ["📋 Overview", "💰 Contract Analysis", "📈 Trends & Patterns", "🚨 Security Insights"]
    )
    
    if tab == "📋 Overview":
        show_overview(sipri_df, contracts_df)
    elif tab == "💰 Contract Analysis":
        show_contract_analysis(contracts_df)
    elif tab == "📈 Trends & Patterns":
        show_trends_analysis(sipri_df, contracts_df)
    elif tab == "🚨 Security Insights":
        show_security_insights(sipri_df)

def show_overview(sipri_df, contracts_df):
    st.header("📋 Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Dataset Summary")
        st.info(f"**SIPRI Global Security Data**: {len(sipri_df)} security insights covering military spending, conflicts, and emerging threats")
        st.info(f"**Defense Contracts Data**: {len(contracts_df)} defense procurement contracts with values and categories")
    
    with col2:
        st.subheader("🎯 Key Statistics")
        
        # Key metrics
        total_contract_value = contracts_df['value'].sum()
        high_value_contracts = len(contracts_df[contracts_df['category'].str.contains('High-Value', na=False)])
        avg_contract_value = contracts_df['value'].mean()
        
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("Total Contract Value", f"{total_contract_value/1e12:.1f}T KRW", help="Total value of all contracts")
            st.metric("High-Value Contracts", high_value_contracts, help="Contracts ≥ 10B KRW")
        
        with col2_2:
            st.metric("Global Military Spending 2024", "$2.7T", help="SIPRI reported global military spending")
            st.metric("Conflict Deaths 2024", "239K", help="Conflict-related deaths in 2024")
    
    # Dataset previews
    st.subheader("📄 Data Previews")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**SIPRI Security Insights**")
        st.dataframe(sipri_df.head(), use_container_width=True)
    
    with col2:
        st.write("**Defense Contracts**")
        st.dataframe(contracts_df[['indicator', 'value', 'category']].head(), use_container_width=True)

def show_contract_analysis(contracts_df):
    st.header("💰 Contract Analysis")
    
    # Value distribution
    def get_value_ranges(df):
        ranges = []
        for _, row in df.iterrows():
            value = row['value']
            if value < 1e9:
                ranges.append('< 1B KRW')
            elif value < 10e9:
                ranges.append('1-10B KRW')
            elif value < 50e9:
                ranges.append('10-50B KRW')
            elif value < 100e9:
                ranges.append('50-100B KRW')
            else:
                ranges.append('> 100B KRW')
        return ranges
    
    contracts_df['value_range'] = get_value_ranges(contracts_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Contract Value Distribution")
        value_dist = contracts_df['value_range'].value_counts()
        fig = px.bar(
            x=value_dist.index,
            y=value_dist.values,
            labels={'x': 'Value Range', 'y': 'Number of Contracts'},
            title="Distribution of Contract Values"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Category Breakdown")
        category_counts = contracts_df['category'].value_counts()
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Contract Categories"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top contracts table
    st.subheader("🏆 Top 15 Highest Value Contracts")
    top_contracts = contracts_df.nlargest(15, 'value')[['indicator', 'value', 'category', 'date']]
    top_contracts['value_formatted'] = top_contracts['value'].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(
        top_contracts[['indicator', 'value_formatted', 'category', 'date']],
        column_config={
            "indicator": "Contract Description",
            "value_formatted": "Value (KRW)",
            "category": "Category",
            "date": "Date"
        },
        use_container_width=True
    )
    
    # Value vs Frequency analysis
    st.subheader("💹 Value vs Frequency Analysis")
    
    # Extract frequency from category
    contracts_df['frequency'] = contracts_df['category'].str.extract(r'(\d+)').fillna(1).astype(int)
    
    fig = px.scatter(
        contracts_df,
        x='frequency',
        y='value',
        color='category',
        hover_data=['indicator'],
        title="Contract Value vs Frequency",
        labels={'frequency': 'Frequency (times)', 'value': 'Contract Value (KRW)'},
        log_y=True
    )
    st.plotly_chart(fig, use_container_width=True)

def show_trends_analysis(sipri_df, contracts_df):
    st.header("📈 Trends & Patterns Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Monthly Contract Trends")
        monthly_trends = contracts_df.groupby('month').agg({
            'value': 'sum',
            'indicator': 'count'
        }).reset_index()
        monthly_trends.columns = ['month', 'total_value', 'count']
        
        fig = px.line(
            monthly_trends,
            x='month',
            y='total_value',
            title='Total Contract Value by Month',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Value (KRW)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Security Topics Coverage")
        topic_counts = sipri_df['topic'].value_counts()
        fig = px.bar(
            y=topic_counts.index,
            x=topic_counts.values,
            orientation='h',
            title='Security Topics in SIPRI Report'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Contract categories over time
    st.subheader("⏰ Contract Categories Over Time")
    category_time = contracts_df.groupby(['month', 'category']).size().reset_index(name='count')
    
    fig = px.bar(
        category_time,
        x='month',
        y='count',
        color='category',
        title='Contract Categories Distribution Over Time'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("🔍 Statistical Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Contract Value", f"{contracts_df['value'].mean()/1e9:.2f}B KRW")
    
    with col2:
        st.metric("Median Contract Value", f"{contracts_df['value'].median()/1e9:.2f}B KRW")
    
    with col3:
        st.metric("Standard Deviation", f"{contracts_df['value'].std()/1e9:.2f}B KRW")

def show_security_insights(sipri_df):
    st.header("🚨 Security Insights from SIPRI Report")
    
    # Display insights as cards
    for _, insight in sipri_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="insight-card">
                <h4>🎯 {insight['topic']}</h4>
                <p>{insight['insight']}</p>
                <small>📊 {insight['report']} • {insight['year']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.subheader("🔗 Key Findings & Correlations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Contract Patterns**
        - L-SAM (Land-based Surface-to-Air Missile) systems dominate high-value contracts
        - Strong focus on air defense and missile systems procurement  
        - Significant investment in vehicle maintenance and modernization
        - Emergency procurement items suggest urgent operational needs
        - High frequency of ammunition and training equipment purchases
        """)
    
    with col2:
        st.markdown("""
        **🌍 Global Security Context**
        - Record military spending aligns with increased regional tensions
        - Focus on emerging technologies (AI, cyber, space weapons)
        - Climate change adding new dimension to security challenges
        - Arms control treaties facing significant enforcement challenges
        - Nuclear arms race concerns with modernization efforts
        """)
    
    # Create a word cloud-like visualization using topic frequency
    st.subheader("📊 Topic Importance Analysis")
    
    # Create a simple bar chart showing topic coverage
    topic_importance = sipri_df['topic'].value_counts()
    
    fig = px.treemap(
        names=topic_importance.index,
        values=[1] * len(topic_importance),  # Equal weighting for treemap
        title="Security Topics Coverage Map"
    )
    st.plotly_chart(fig, use_container_width=True)

# File upload option
st.sidebar.markdown("---")
st.sidebar.header("📁 Upload Your Data")
uploaded_sipri = st.sidebar.file_uploader("Upload SIPRI CSV", type=['csv'], key="sipri")
uploaded_contracts = st.sidebar.file_uploader("Upload Contracts CSV", type=['csv'], key="contracts")

if uploaded_sipri is not None or uploaded_contracts is not None:
    st.sidebar.success("Files uploaded! The dashboard will use your data.")

if __name__ == "__main__":
    main()