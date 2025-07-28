import os
import warnings
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR")
eda_path = os.path.join(EDA_DIR, "outputs", "korea_trade")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Korea Export Trade
def load_korea_export_trade_data(engine):
    query = """
    SELECT date, country, partner, indicator, export_amount, trade_yoy, trade_share
    FROM trade_korea_export_country_variation_processed
    ORDER BY date DESC, trade_share DESC, export_amount DESC;
    """
    return pd.read_sql(query, engine)

# Korea Import Trade
def load_korea_import_trade_data(engine):
    query = """
    SELECT date, country, partner, indicator, import_amount, trade_yoy, trade_share
    FROM trade_korea_import_country_variation_processed
    ORDER BY date DESC, trade_share DESC, import_amount DESC;
    """
    return pd.read_sql(query, engine)

# mode must be 'export' or 'import'
def analyse_trade(df, mode='export'):
    assert mode in ['export', 'import']
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    amount_col = 'export_amount' if mode == 'export' else 'import_amount'

    # Latest month
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]

    # Exclude World
    df_latest_filtered = df_latest[df_latest['partner'] != 'World']
    top_partners = (
        df_latest_filtered.groupby(['country', 'partner'], as_index=False)
        .agg({amount_col: 'sum', 'trade_share': 'sum'})
        .sort_values(amount_col, ascending=False)
        .head(5)
    )

    # Partner share trends (filter by significant trade share)
    avg_share_by_partner = df.groupby('partner')['trade_share'].mean()
    significant_partners = avg_share_by_partner[avg_share_by_partner >= 0.1].index
    df_significant = df[df['partner'].isin(significant_partners)]

    share_trends = (
        df_significant.groupby(['date', 'country', 'partner'], as_index=False)
        .agg({'trade_share': 'sum'})
        .sort_values(['country', 'partner', 'date'])
    )

    # Summary statistics
    summary_stats = df[[amount_col, 'trade_yoy']].describe().round(2)

    # Trend analysis for top 3
    top3 = top_partners.head(3)[['country', 'partner']]
    df_filtered = df[df['partner'] != 'World']
    mask = df_filtered.set_index(['country', 'partner']).index.isin(top3.set_index(['country', 'partner']).index)
    top3_trend = df_filtered[mask][['date', 'country', 'partner', amount_col, 'trade_share']].sort_values(['country', 'partner', 'date'])

    return {
        'mode': mode,
        'top_partners': top_partners,
        'share_trends': share_trends,
        'summary_stats': summary_stats,
        'top3_trend': top3_trend
    }

# Map English Commodity Names
translation_map = {
# Electronics
"메모리": "Memory chips",
"프로세서와 컨트롤러[메모리ㆍ변환기ㆍ논리회로ㆍ증폭기ㆍ클록(clock)ㆍ타이밍(timing) 회로나 그 밖의 회로를 갖춘 것인지는 상관없다]": "Processors and controllers",
"솔리드 스테이트(solid-state)의 비휘발성 기억장치": "SSD storage",
"인쇄회로": "Printed circuits",
"반도체디바이스나 전자집적회로 제조용 기계와 기기": "Semiconductor manufacturing equipment",
"유기발광다이오드(오엘이디)의 것": "OLED displays",
# Vehicles
"실린더용량이 1,500시시 초과 3,000시시 이하인 것": "Vehicles (1.5-3L engine)",
"그 밖의 차량(불꽃점화식 피스톤 내연기관과 추진용 모터로서의 전동기를 둘 다 갖춘 것으로서, 외부 전원에 플러그를 꽂아 충전할 수 있는 방식의 것은 제외한다)": "Hybrid vehicles (non-plug-in)",
"승용자동차용[스테이션왜건(station wagon)과 경주 자동차용을 포함한다]": "Passenger vehicles",
"기어박스와 그 부분품": "Transmission parts",
"그 밖의 화물선과 화객선": "Other Cargo & Passenger Ships",
# Machinery
"제8471호에 해당하는 기계의 부분품과 부속품": "Machinery parts (HS8471)",
"360도 회전의 상부구조를 가진 기계": "Rotating machinery",
"파쇄기나 분쇄기": "Crushers/grinders",
"자체 중량이 2,000킬로그램을 초과하는 것": "Heavy equipment (>2T)",
"탱커(tanker)": "Tankers",
# Chemicals
"파라-크실렌": "Para-xylene",
"오르토인산수소 이암모늄(인산이암모늄)": "Ammonium phosphate",
"황산암모늄": "Ammonium sulfate",
"산화니켈과 수산화니켈": "Nickel compounds",
"경질유(輕質油)와 조제품": "Light oils",
"박하유[멘타 피페리타(Mentha piperita)]": "Peppermint oil",
"메틸디에탄올아민과 에틸디에탄올아민": "Methyldiethanolamine & Ethyldiethanolamine",
# Energy & Raw Materials
"유연탄": "Bituminous coal",
"석유와 역청유(瀝靑油)(원유로 한정한다)": "Crude petroleum oil",
"구리광과 그 정광(精鑛)": "Copper ores and concentrates",
"응결시키지 않은 것": "Uncondensed materials",
"우라늄 235를 농축한 우라늄과 그 화합물, 플루토늄과 그 화합물, 합금ㆍ분산물(分散物)[서멧(cermet)을 포함한다]ㆍ도자제품과 이들의 혼합물(우라늄 235를 농축한 우라늄ㆍ플루토늄이나 이들의 화합물을 함유하는 것으로 한정한다)": "Enriched uranium and plutonium compounds",
"아미노렉스(INN)ㆍ브로티졸람(INN)ㆍ클로티아제팜(INN)ㆍ클록사졸람(INN)ㆍ덱스트로모라마이드(INN)ㆍ할록사졸람(INN)ㆍ케타졸람(INN)ㆍ메소카브(INN)ㆍ옥사졸람(INN)ㆍ페몰린(INN)ㆍ펜디메트라진(INN)ㆍ펜메트라진(INN)ㆍ서펜타닐(INN)과 이들의 염": "Pharmaceutical compounds",
"탄화칼슘": "Calcium carbide",
"조유(粗油)": "Crude petroleum oil",
# Other
"크랜베리(cranberry)ㆍ빌베리(bilberry)와 그 밖의 박시니엄(Vaccinium)속의 과실": "Cranberries and bilberries",
"미생물성 지방과 기름 및 이들의 분획물": "Microbial fats and oils",
"리튬이온 축전지": "Lithium batteries",
"스마트폰": "Smartphones",
"테이블린넨(table linen)(메리야스 편물이나 뜨개질 편물로 한정한다)": "Table linen",
"주로 재생ㆍ반(半)합성 스테이플섬유와 혼방한 것": "Recycled fiber blends",
"테트라사이클린과 이들의 유도체, 이들의 염": "Tetracycline & Derivatives",
"곡물의 씨눈[원래 모양인 것ㆍ압착한 것ㆍ플레이크(flake) 모양인 것ㆍ잘게 부순 것으로 한정한다]": "Cereal Germs",
"어류의 지방과 기름 및 그 분획물[간유(肝油)는 제외한다]": "Fish Fats & Oils",
"제도판을 갖춘 제도기(자동식인지에 상관없다)": "Drawing Boards & Instruments",
"기타": "Others",
}

# Korea Increased Export Trade Items
def load_korea_export_increase_items_data(engine):
    query = """
    SELECT *
    FROM trade_korea_export_increase_items_processed
    WHERE commodity_name IS NOT NULL 
    AND export_amount > 0
    ORDER BY date DESC, export_amount DESC;
    """
    return pd.read_sql(query, engine)

# Korea Increased Import Trade Items
def load_korea_import_increase_items_data(engine):
    query = """
    SELECT *
    FROM trade_korea_import_increase_items_processed
    WHERE commodity_name IS NOT NULL 
    AND import_amount > 0
    ORDER BY date DESC, import_amount DESC;
    """
    return pd.read_sql(query, engine)

# Analyse Increase Export and Import Items
def analyse_increase_items(df, mode='export'):
    assert mode in ['export', 'import']

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['trade_yoy'] = pd.to_numeric(df['trade_yoy'], errors='coerce')

    value_col = 'export_amount' if mode == 'export' else 'import_amount'
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    df['commodity_name_en'] = df['commodity_name'].map(translation_map)

    # Rename duplicate 'Others'
    count = 1
    for idx in df[df['commodity_name_en'] == 'Others'].index:
        df.loc[idx, 'commodity_name_en'] = f'Others Type: {count}'
        count += 1

    # Latest snapshot
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]

    print(f"[{mode.upper()}] Analysis for latest date: {latest_date}")
    print(f"Total records in latest month: {len(df_latest)}")

    # Top YoY growth commodities
    top_yoy_growth = (
        df_latest[df_latest['trade_yoy'].notna()]
        .groupby(['commodity_name_en'], as_index=False)
        .agg({
            value_col: 'sum',
            'trade_yoy': 'mean',
        })
        .sort_values('trade_yoy', ascending=False)
        .head(10)
    )

    # Top by total amount
    top_amount = (
        df_latest.groupby(['commodity_name_en'], as_index=False)
        .agg({
            value_col: 'sum',
            'trade_yoy': 'mean',
        })
        .sort_values(value_col, ascending=False)
        .head(10)
    )

    # Monthly trend
    top5 = top_amount['commodity_name_en'].head(5).tolist()
    monthly_trend = (
        df[df['commodity_name_en'].isin(top5)]
        .groupby(['date', 'commodity_name_en'], as_index=False)
        .agg({
            value_col: 'sum',
            'trade_yoy': 'mean'
        })
        .sort_values(['commodity_name_en', 'date'])
    )

    # YoY stats
    yoy_stats = df_latest[df_latest['trade_yoy'].notna()]['trade_yoy'].describe()

    # Partner analysis
    partner_analysis = (
        df_latest[df_latest['commodity_name_en'].isin(top5)]
        .groupby(['commodity_name_en', 'partner'], as_index=False)
        .agg({value_col: 'sum'})
        .sort_values(['commodity_name_en', value_col], ascending=[True, False])
    )

    return {
        'mode': mode,
        'latest_date': latest_date,
        'total_records': len(df_latest),
        'top_yoy_growth': top_yoy_growth,
        'top_amount': top_amount,
        'monthly_trend': monthly_trend,
        'yoy_statistics': yoy_stats,
        'partner_analysis': partner_analysis
    }

# Export and Import Main Items Value Analysis
def load_korea_export_import_main_items_data(engine):
    query = """
    SELECT date, country, category as trade_type, indicator as item, value, yoy_change
    FROM trade_korea_trade_items_yoy_processed
    ORDER BY date, trade_type, item;
    """
    return pd.read_sql(query, engine)

def analyse_export_import_value_index(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['yoy_change'] = pd.to_numeric(df['yoy_change'], errors='coerce')

    # Translation
    translation_map = {
        "전지": "Battery",
        "변압기": "Transformer",
        "제트유": "Jet fuel",
        "휘발유": "Gasoline",
        "기초무기화합물": "Basic chemical",
        "천연가스(LNG)": "Natural gas (LNG)",
        "윤활유및그리스": "Lubricants and greases",
        "중후판(두께3mm이상)": "Thick plate (3mm or more)",
    }
    df['item_en'] = df['item'].map(translation_map).fillna(df['item'])

    # Latest snapshot
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date].dropna(subset=['yoy_change'])

    # Top ↑ and Bottom ↓ YoY Changes
    top_yoy = df_latest.sort_values('yoy_change', ascending=False).head(5)
    bottom_yoy = df_latest.sort_values('yoy_change', ascending=True).head(5)

    # Volatility: standard deviation of value index
    volatility = (
        df.groupby(['item_en', 'trade_type'])['value']
        .std()
        .sort_values(ascending=False)
    )

    # Trend pivot tables (for external plotting)
    pivot_yoy = df.pivot_table(index='date', columns=['item_en', 'trade_type'], values='yoy_change')
    pivot_value = df.pivot_table(index='date', columns=['item_en', 'trade_type'], values='value')

    return {
        'latest_date': latest_date,
        'top_yoy': top_yoy,
        'bottom_yoy': bottom_yoy,
        'volatility': volatility,
        'pivot_yoy': pivot_yoy,
        'pivot_value': pivot_value,
    }

# Load Korea Trade Data
def load_korea_trade_data(engine):
    query = """
    SELECT date, country, partner, category AS trade_type, value, yoy_change
    FROM trade_korea_trade_yoy_processed
    ORDER BY date, trade_type, partner;
    """
    return pd.read_sql(query, engine)

# Analyze Trade YoY Data
def analyse_trade_yoy(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['yoy_change'] = pd.to_numeric(df['yoy_change'], errors='coerce')

    # Latest snapshot
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]
    exports = df_latest[df_latest['trade_type'] == 'Total Exports']
    imports = df_latest[df_latest['trade_type'] == 'Total Imports']

    top_export_partners = exports.sort_values('value', ascending=False).head(10)
    top_import_partners = imports.sort_values('value', ascending=False).head(10)
    top_yoy = df_latest.sort_values('yoy_change', ascending=False).head(5)
    bottom_yoy = df_latest.sort_values('yoy_change', ascending=True).head(5)

    top_partners = (
        df.groupby('partner')['value'].sum()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    df_top = df[df['partner'].isin(top_partners)]
    trend = df_top.pivot_table(
        index='date',
        columns=['partner', 'trade_type'],
        values='value'
    )

    pivot = df.pivot_table(
        index=['date', 'partner'],
        columns='trade_type',
        values='value',
        aggfunc='sum'
    ).fillna(0)

    pivot['trade_balance'] = (
        pivot.get('Total Exports', 0) - pivot.get('Total Imports', 0)
    )

    return {
        'latest_date': latest_date,
        'top_export_partners': top_export_partners,
        'top_import_partners': top_import_partners,
        'top_yoy': top_yoy,
        'bottom_yoy': bottom_yoy,
        'trend': trend,
        'trade_balance': pivot.reset_index()
    }

# Semiconductors
def load_wsts_billings_data(engine):
    query = """
    SELECT date, country, value, unit, sector, indicator, period_type
    FROM trade_wsts_billings_latest_processed
    WHERE period_type IN ('month', 'annual')
    ORDER BY date, country;
    """
    return pd.read_sql(query, engine)

def analyse_wsts_billings(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Filter for semiconductors only
    df = df[(df['sector'] == 'semiconductors') & (df['indicator'] == 'billings')]

    # Split by period type
    df_month = df[df['period_type'] == 'month']
    df_annual = df[df['period_type'] == 'annual']

    # Latest Monthly Snapshot
    latest_month = df_month['date'].max()
    latest_month_df = df_month[df_month['date'] == latest_month]
    top_monthly_regions = latest_month_df.sort_values('value', ascending=False)

    # Monthly Time Series Trend
    trend_month = (
        df_month.groupby(['date', 'country'], as_index=False)
        .agg({'value': 'sum'})
        .sort_values(['country', 'date'])
    )
    trend_month_pivot = trend_month.pivot(index='date', columns='country', values='value')

    # Annual Time Series Trend
    trend_annual = (
        df_annual.groupby(['date', 'country'], as_index=False)
        .agg({'value': 'sum'})
        .sort_values(['country', 'date'])
    )
    trend_annual_pivot = trend_annual.pivot(index='date', columns='country', values='value')

    # Year-over-Year Change (Monthly)
    df_month = df_month.sort_values(['country', 'date'])
    df_month['yoy_change'] = (
        df_month.groupby('country')['value']
        .transform(lambda x: x.pct_change(periods=12) * 100)
    )

    # Annual Growth Rate
    df_annual = df_annual.sort_values(['country', 'date'])
    df_annual['yoy_change'] = (
        df_annual.groupby('country')['value']
        .transform(lambda x: x.pct_change(periods=1) * 100)
    )

    # Volatility (Standard Deviation)
    volatility = (
        df_month.groupby('country')['value']
        .std()
        .sort_values(ascending=False)
    )

    # Market Share (monthly, using World as denominator)
    monthly_world = df_month[df_month['country'] == 'World'][['date', 'value']].rename(columns={'value': 'world_total'})
    df_month = pd.merge(df_month, monthly_world, on='date', how='left')
    df_month['market_share'] = df_month['value'] / df_month['world_total']

    # Latest Annual Snapshot
    latest_annual = df_annual['date'].max()
    latest_annual_df = df_annual[df_annual['date'] == latest_annual]
    top_annual_regions = latest_annual_df.sort_values('value', ascending=False)

    return {
        'latest_month': latest_month,
        'latest_annual': latest_annual,
        'top_monthly_regions': top_monthly_regions,
        'top_annual_regions': top_annual_regions,
        'trend_monthly': trend_month_pivot,
        'trend_annual': trend_annual_pivot,
        'yoy_monthly': df_month[['date', 'country', 'yoy_change']],
        'yoy_annual': df_annual[['date', 'country', 'yoy_change']],
        'volatility': volatility,
        'market_share_monthly': df_month[['date', 'country', 'market_share']]
    }


# Save EDA outputs
def save_trade_eda_outputs(output_dir, engine):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Export/Import Trade Analysis
    print("📊 Analyzing export/import trade data...")
    export_df = load_korea_export_trade_data(engine)
    export_insights = analyse_trade(export_df, mode='export')
    
    import_df = load_korea_import_trade_data(engine)
    import_insights = analyse_trade(import_df, mode='import')
    
    # Save trade analysis results
    export_insights['top_partners'].to_csv(
        os.path.join(output_dir, "export_top_partners.csv"), index=False
    )
    import_insights['top_partners'].to_csv(
        os.path.join(output_dir, "import_top_partners.csv"), index=False
    )
    
    # 2. Export/Import Items Analysis
    print("📦 Analyzing trade items data...")
    df_export_items = load_korea_export_increase_items_data(engine)
    df_import_items = load_korea_import_increase_items_data(engine)
    
    result_export = analyse_increase_items(df_export_items, mode='export')
    result_import = analyse_increase_items(df_import_items, mode='import')
    
    # Save items analysis results
    result_export['top_amount'].to_csv(
        os.path.join(output_dir, "export_top_items_by_amount.csv"), index=False
    )
    result_export['top_yoy_growth'].to_csv(
        os.path.join(output_dir, "export_top_items_by_yoy.csv"), index=False
    )
    result_import['top_amount'].to_csv(
        os.path.join(output_dir, "import_top_items_by_amount.csv"), index=False
    )
    result_import['top_yoy_growth'].to_csv(
        os.path.join(output_dir, "import_top_items_by_yoy.csv"), index=False
    )
    
    # 3. Trade YoY Analysis
    print("📈 Analyzing trade YoY trends...")
    df_trade_yoy = load_korea_trade_data(engine)
    trade_yoy_insights = analyse_trade_yoy(df_trade_yoy)
    
    trade_yoy_insights['top_export_partners'].to_csv(
        os.path.join(output_dir, "trade_yoy_top_export_partners.csv"), index=False
    )
    trade_yoy_insights['top_import_partners'].to_csv(
        os.path.join(output_dir, "trade_yoy_top_import_partners.csv"), index=False
    )
    trade_yoy_insights['trade_balance'].to_csv(
        os.path.join(output_dir, "trade_balance.csv"), index=False
    )
    
    # 4. Export/Import Value Index Analysis
    print("💹 Analyzing value indices...")
    df_value_index = load_korea_export_import_main_items_data(engine)
    value_index_insights = analyse_export_import_value_index(df_value_index)
    
    value_index_insights['top_yoy'].to_csv(
        os.path.join(output_dir, "value_index_top_yoy.csv"), index=False
    )
    value_index_insights['bottom_yoy'].to_csv(
        os.path.join(output_dir, "value_index_bottom_yoy.csv"), index=False
    )
    value_index_insights['volatility'].to_csv(
        os.path.join(output_dir, "value_index_volatility.csv")
    )
    
    # 5. Semiconductor Billings Analysis
    print("🔌 Analyzing semiconductor billings...")
    df_wsts = load_wsts_billings_data(engine)
    wsts_insights = analyse_wsts_billings(df_wsts)
    
    wsts_insights['top_monthly_regions'].to_csv(
        os.path.join(output_dir, "wsts_top_monthly_regions.csv"), index=False
    )
    wsts_insights['top_annual_regions'].to_csv(
        os.path.join(output_dir, "wsts_top_annual_regions.csv"), index=False
    )
    wsts_insights['volatility'].to_csv(
        os.path.join(output_dir, "wsts_volatility.csv")
    )
    
    # Save trend and YoY data
    wsts_insights['trend_monthly'].to_csv(
        os.path.join(output_dir, "wsts_trend_monthly.csv")
    )
    wsts_insights['trend_annual'].to_csv(
        os.path.join(output_dir, "wsts_trend_annual.csv")
    )
    wsts_insights['yoy_monthly'].to_csv(
        os.path.join(output_dir, "wsts_yoy_monthly.csv"), index=False
    )
    wsts_insights['yoy_annual'].to_csv(
        os.path.join(output_dir, "wsts_yoy_annual.csv"), index=False
    )
    wsts_insights['market_share_monthly'].to_csv(
        os.path.join(output_dir, "wsts_market_share_monthly.csv"), index=False
    )
    
     # Key insights
    key_insights = {
        "analysis_timestamp": pd.Timestamp.now().isoformat(),
        "export_analysis": {
            "latest_date": str(result_export['latest_date']),
            "total_records": result_export['total_records'],
            "top_commodity": result_export['top_amount'].iloc[0]['commodity_name_en'] if len(result_export['top_amount']) > 0 else "N/A",
            "top_yoy_growth": float(result_export['top_yoy_growth'].iloc[0]['trade_yoy']) if len(result_export['top_yoy_growth']) > 0 else "N/A"
        },
        "import_analysis": {
            "latest_date": str(result_import['latest_date']),
            "total_records": result_import['total_records'],
            "top_commodity": result_import['top_amount'].iloc[0]['commodity_name_en'] if len(result_import['top_amount']) > 0 else "N/A",
            "top_yoy_growth": float(result_import['top_yoy_growth'].iloc[0]['trade_yoy']) if len(result_import['top_yoy_growth']) > 0 else "N/A"
        },
        "trade_yoy_analysis": {
            "latest_date": str(trade_yoy_insights['latest_date']),
            "top_export_partner": trade_yoy_insights['top_export_partners'].iloc[0]['partner'] if len(trade_yoy_insights['top_export_partners']) > 0 else "N/A",
            "top_import_partner": trade_yoy_insights['top_import_partners'].iloc[0]['partner'] if len(trade_yoy_insights['top_import_partners']) > 0 else "N/A"
        },
        "semiconductor_analysis": {
            "latest_month": str(wsts_insights['latest_month']),
            "latest_annual": str(wsts_insights['latest_annual']),
            "top_monthly_region": wsts_insights['top_monthly_regions'].iloc[0]['country'] if len(wsts_insights['top_monthly_regions']) > 0 else "N/A"
        }
    }
    
    with open(os.path.join(output_dir, "key_insights.json"), "w", encoding='utf-8') as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False)
    
    print(f"✅ All EDA outputs saved to: {output_dir}")
    print(f"📁 Generated {len(os.listdir(output_dir))} files")
    
    return {
        "export_insights": export_insights,
        "import_insights": import_insights,
        "export_items": result_export,
        "import_items": result_import,
        "trade_yoy": trade_yoy_insights,
        "value_index": value_index_insights,
        "semiconductor": wsts_insights,
        "key_insights": key_insights
    }

# Gemini Insight
def generate_gemini_insights(eda_results, output_dir):
    try:   
        # Extract key data points
        export_data = {
            "latest_date": str(eda_results['export_items']['latest_date']),
            "total_records": eda_results['export_items']['total_records'],
            "top_commodity": eda_results['export_items']['top_amount'].iloc[0]['commodity_name_en'] if len(eda_results['export_items']['top_amount']) > 0 else "N/A",
            "top_yoy_growth": float(eda_results['export_items']['top_yoy_growth'].iloc[0]['trade_yoy']) if len(eda_results['export_items']['top_yoy_growth']) > 0 else "N/A",
            "top_commodity_amount": float(eda_results['export_items']['top_amount'].iloc[0]['export_amount']) if len(eda_results['export_items']['top_amount']) > 0 else 0
        }
        
        import_data = {
            "latest_date": str(eda_results['import_items']['latest_date']),
            "total_records": eda_results['import_items']['total_records'],
            "top_commodity": eda_results['import_items']['top_amount'].iloc[0]['commodity_name_en'] if len(eda_results['import_items']['top_amount']) > 0 else "N/A",
            "top_yoy_growth": float(eda_results['import_items']['top_yoy_growth'].iloc[0]['trade_yoy']) if len(eda_results['import_items']['top_yoy_growth']) > 0 else "N/A",
            "top_commodity_amount": float(eda_results['import_items']['top_amount'].iloc[0]['import_amount']) if len(eda_results['import_items']['top_amount']) > 0 else 0
        }
        
        semiconductor_data = {
            "latest_month": str(eda_results['semiconductor']['latest_month']),
            "top_region": eda_results['semiconductor']['top_monthly_regions'].iloc[0]['country'] if len(eda_results['semiconductor']['top_monthly_regions']) > 0 else "N/A",
            "top_region_value": float(eda_results['semiconductor']['top_monthly_regions'].iloc[0]['value']) if len(eda_results['semiconductor']['top_monthly_regions']) > 0 else 0
        }
        
        trade_balance_data = {
            "latest_date": str(eda_results['trade_yoy']['latest_date']),
            "top_export_partner": eda_results['trade_yoy']['top_export_partners'].iloc[0]['partner'] if len(eda_results['trade_yoy']['top_export_partners']) > 0 else "N/A",
            "top_import_partner": eda_results['trade_yoy']['top_import_partners'].iloc[0]['partner'] if len(eda_results['trade_yoy']['top_import_partners']) > 0 else "N/A"
        }

        prompt = f"""
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects. Extract non-obvious implications from the data below.

**Data Context**:
- Analysis Period: {export_data['latest_date']}
- Data Scope: Korea's export/import trade, semiconductor industry, and trade partnerships

**Key Data Points**:

1. **Export Performance**:
   - Top Export Commodity: {export_data['top_commodity']} (${export_data['top_commodity_amount']:,.0f})
   - Highest YoY Growth: {export_data['top_yoy_growth']:.1f}%
   - Total Records Analyzed: {export_data['total_records']}

2. **Import Trends**:
   - Top Import Commodity: {import_data['top_commodity']} (${import_data['top_commodity_amount']:,.0f})
   - Highest YoY Growth: {import_data['top_yoy_growth']:.1f}%
   - Total Records Analyzed: {import_data['total_records']}

3. **Semiconductor Industry**:
   - Latest Data: {semiconductor_data['latest_month']}
   - Top Region: {semiconductor_data['top_region']} (${semiconductor_data['top_region_value']:,.0f})

4. **Trade Partnerships**:
   - Top Export Partner: {trade_balance_data['top_export_partner']}
   - Top Import Partner: {trade_balance_data['top_import_partner']}


### **Required Output Format**
## Korea Trade Sector Second-Order Effect Analysis

### Core Trend
• Korea Trade: [TREND SUMMARY IN 5–10 WORDS]  
• **Direct Impact**: [IMMEDIATE OUTCOME IN 1 SENTENCE]

### Hidden Effects
1. **[EFFECT 1 NAME]**
   - *Catalyst*: [PRIMARY DRIVER]
   - *Transmission*: [HOW IT SPREADS THROUGH SYSTEM]
   - *Evidence*: [DATA POINT OR HISTORICAL PRECEDENT]

2. **[EFFECT 2 NAME]**
   - *Catalyst*: [PRIMARY DRIVER]
   - *Transmission*: [HOW IT SPREADS THROUGH SYSTEM]
   - *Evidence*: [DATA POINT OR HISTORICAL PRECEDENT]

### Strategic Recommendations
🛠 **Immediate Actions**: [CONCRETE STEPS]
📊 **Monitoring Metrics**: [KEY INDICATORS]
🎯 **Long-term Strategy**: [STRATEGIC DIRECTION]

### Risk Assessment
⚠️ **High Risk**: [CRITICAL CONCERN]
⚠️ **Medium Risk**: [MODERATE CONCERN]
⚠️ **Low Risk**: [MINOR CONCERN]

### Market Intelligence
📈 **Bullish Signals**: [POSITIVE INDICATORS]
📉 **Bearish Signals**: [NEGATIVE INDICATORS]
🔄 **Neutral Factors**: [BALANCED ELEMENTS]

**Analysis Guidelines**:
- Focus on actionable intelligence
- Consider global geopolitical dynamics
- Assess Korea's competitive positioning
- Identify emerging trends and risks
- Provide specific, measurable recommendations
"""

        response = MODEL.generate_content(prompt)
        gemini_insight = response.text.strip()

        # Save insights
        with open(os.path.join(output_dir, "gemini_insights_korea_trade.txt"), "w", encoding="utf-8") as f:
            f.write(gemini_insight)

        # JSON for programmatic access
        insight_data = {
            "generated_at": pd.Timestamp.now().isoformat(),
            "analysis_period": str(export_data['latest_date']),
            "key_metrics": {
                "export": export_data,
                "import": import_data,
                "semiconductor": semiconductor_data,
                "trade_balance": trade_balance_data
            },
            "insights": gemini_insight
        }
        
        with open(os.path.join(output_dir, "gemini_insights_data.json"), "w", encoding="utf-8") as f:
            json.dump(insight_data, f, indent=2, ensure_ascii=False)

        print("✅ Gemini strategic insights generated and saved.")
        print(f"📄 Markdown: gemini_strategic_insights.md")
        print(f"📊 Data: gemini_insights_data.json")
        
        return insight_data

    except Exception as e:
        print(f"❌ Gemini insight generation failed: {e}")
        return None


if __name__ == "__main__":
    # Run comprehensive EDA analysis and save all outputs
    print("🚀 Starting Korea Trade EDA Analysis...")
    
    # Create output directory
    os.makedirs(eda_path, exist_ok=True)
    
    # Run complete analysis
    results = save_trade_eda_outputs(eda_path, engine)
    
    print("\n" + "="*50)
    print("📊 ANALYSIS COMPLETE!")
    print("="*50)
    
    # Display key insights
    print(f"\n📈 Export Analysis:")
    print(f"   • Latest Date: {results['export_items']['latest_date']}")
    print(f"   • Total Records: {results['export_items']['total_records']}")
    print(f"   • Top Commodity: {results['export_items']['top_amount'].iloc[0]['commodity_name_en'] if len(results['export_items']['top_amount']) > 0 else 'N/A'}")
    
    print(f"\n📉 Import Analysis:")
    print(f"   • Latest Date: {results['import_items']['latest_date']}")
    print(f"   • Total Records: {results['import_items']['total_records']}")
    print(f"   • Top Commodity: {results['import_items']['top_amount'].iloc[0]['commodity_name_en'] if len(results['import_items']['top_amount']) > 0 else 'N/A'}")
    
    print(f"\n🔌 Semiconductor Analysis:")
    print(f"   • Latest Month: {results['semiconductor']['latest_month']}")
    print(f"   • Top Region: {results['semiconductor']['top_monthly_regions'].iloc[0]['country'] if len(results['semiconductor']['top_monthly_regions']) > 0 else 'N/A'}")
    
    # Generate AI-powered insights
    print(f"\n🤖 Generating AI-powered strategic insights...")
    gemini_results = generate_gemini_insights(results, eda_path)
    
    if gemini_results:
        print(f"\n📄 Strategic insights saved:")
        print(f"   • Markdown: gemini_insights_korea_trade.txt")
        print(f"   • Data: gemini_insights_data.json")
    
    print(f"\n📁 All outputs saved to: {eda_path}")
    print("="*50)