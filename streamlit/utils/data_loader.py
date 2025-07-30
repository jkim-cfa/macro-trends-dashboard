# utils/data_loader.py
import pandas as pd
import json
import os
from functools import lru_cache

BASE_PATH = "eda/outputs"

def load_csv(sector, filename, **kwargs):
    path = os.path.join(BASE_PATH, sector, filename)
    try:
        return pd.read_csv(path, **kwargs)
    except FileNotFoundError:
        print(f"Warning: {path} not found. Returning empty DataFrame.")
        return pd.DataFrame()

def load_json(sector, filename):
    path = os.path.join(BASE_PATH, sector, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found. Returning empty dict.")
        return {}

def load_text(sector, filename):
    path = os.path.join(BASE_PATH, sector, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {path} not found. Returning empty string.")
        return ""

@lru_cache(maxsize=None)
def load_agriculture_data():
    return {
        "ready": load_csv("agriculture", "streamlit_ready_data.csv", parse_dates=["date"]),
        "trend": load_csv("agriculture", "production_trends.csv", parse_dates=["date"]),
        "yoy": load_csv("agriculture", "production_yoy_change.csv", parse_dates=["date"]),
        "growth": load_csv("agriculture", "growth_rates.csv"),
        "stats": load_csv("agriculture", "production_stats.csv"),
        "corr": load_csv("agriculture", "correlation_matrix.csv").set_index("commodity"),
        "insights": load_json("agriculture", "key_insights.json"),
        "gemini_insight": load_text("agriculture", "gemini_insight.txt"),
    }

@lru_cache(maxsize=None)
def load_defence_data():
    return {
        "high_value": load_csv("defence", "high_value_contracts.csv", parse_dates=["date"]),
        "emergency": load_csv("defence", "emergency_contracts.csv", parse_dates=["date"]),
        "frequent": load_csv("defence", "frequent_items.csv", parse_dates=["date"]),
        "combined": load_csv("defence", "defense_contracts_analysis.csv", parse_dates=["date"]),
        "word_freq": load_csv("defence", "word_frequency_analysis.csv"),
        "insights": load_json("defence", "comprehensive_insights.json"),
        "gemini_insight": load_text("defence", "gemini_insight.txt"),
        "sipri_insight": load_text("defence", "sipri_insight.txt"),
    }

@lru_cache(maxsize=None)
def load_economy_data():
    return {
        # Raw data files
        "sentiment_raw": load_csv("economy", "sentiment_raw.csv", parse_dates=["date"]),
        "fx_raw": load_csv("economy", "fx_raw.csv", parse_dates=["date"]),
        "economic_indicators_raw": load_csv("economy", "economic_indicators_raw.csv", parse_dates=["date"]),
        
        # Processed data files
        "sentiment_processed": load_csv("economy", "sentiment_processed.csv", parse_dates=["date"]),
        "key_indicators_processed": load_csv("economy", "key_indicators_processed.csv", parse_dates=["date"]),
        "cross_correlations": load_csv("economy", "cross_correlations.csv"),
        
        # Insights and AI analysis
        "insights": load_json("economy", "key_insights.json"),
        "gemini_insight": load_text("economy", "gemini_insights.txt"),
    }

@lru_cache(maxsize=None)
def load_energy_data():
    return {
        # Raw data
        "iea_stocks_raw": load_csv("energy", "iea_stocks_raw.csv", parse_dates=["date"]),
        "oil_imports_raw": load_csv("energy", "oil_imports_raw.csv", parse_dates=["date"]),
        "opec_summary_raw": load_csv("energy", "opec_summary_raw.csv"),

        # Processed/analysis data
        "stock_country_ranking": load_csv("energy", "stock_country_ranking.csv"),
        "stock_volatility_analysis": load_csv("energy", "stock_volatility_analysis.csv"),
        "stock_seasonality_patterns": load_csv("energy", "stock_seasonality_patterns.csv"),
        "stock_stockpile_statistics": load_csv("energy", "stock_stockpile_statistics.csv"),
        "import_regional_share_trends": load_csv("energy", "import_regional_share_trends.csv"),
        "import_volume_by_region": load_csv("energy", "import_volume_by_region.csv"),
        "import_value_by_region": load_csv("energy", "import_value_by_region.csv"),
        "import_price_by_region": load_csv("energy", "import_price_by_region.csv"),
        "import_dominant_supplier_trend": load_csv("energy", "import_dominant_supplier_trend.csv"),
        "import_metric_breakdown": load_csv("energy", "import_metric_breakdown.csv"),

        # Insights and AI analysis
        "insights": load_json("energy", "key_insights.json"),
        "gemini_insight": load_text("energy", "gemini_insight.txt"),
    }

@lru_cache(maxsize=None)
def load_industry_data():
    return {
        # Raw data
        "manufacturing_inventory_raw": load_csv("industry", "manufacturing_inventory_raw.csv", parse_dates=["date"]),
        "steel_production_raw": load_csv("industry", "steel_production_raw.csv", parse_dates=["date"]),
        # Processed/analysis data
        "manufacturing_inventory_processed": load_csv("industry", "manufacturing_inventory_processed.csv", parse_dates=["date"]),
        "inventory_volatility_analysis": load_csv("industry", "inventory_volatility_analysis.csv"),
        "inventory_trend_statistics": load_csv("industry", "inventory_trend_statistics.csv"),
        # Steel analysis data
        "steel_top_current": load_csv("industry", "steel_top_current.csv"),
        "steel_bottom_current": load_csv("industry", "steel_bottom_current.csv"),
        "steel_top_jan_current": load_csv("industry", "steel_top_jan_current.csv"),
        "steel_bottom_jan_current": load_csv("industry", "steel_bottom_jan_current.csv"),
        "steel_vs_world_current": load_csv("industry", "steel_vs_world_current.csv", parse_dates=["date"]),
        "steel_vs_world_jan_current": load_csv("industry", "steel_vs_world_jan_current.csv", parse_dates=["date"]),
        "steel_major_economies_current": load_csv("industry", "steel_major_economies_current.csv"),
        "steel_major_economies_jan_current": load_csv("industry", "steel_major_economies_jan_current.csv"),
        # Insights and AI analysis
        "insights": load_json("industry", "key_insights.json"),
        "gemini_insight": load_text("industry", "gemini_insight.txt"),
    }

@lru_cache(maxsize=None)
def load_global_trade_data():
    return {
        # Processed data
        "export_decrease_items_top5": load_csv("global_trade", "export_decrease_items_top5.csv"),
        "export_increase_items_top5": load_csv("global_trade", "export_increase_items_top5.csv"),
        "export_increase_countries_top5": load_csv("global_trade", "export_increase_countries_top5.csv"),
        "trade_partners_top5": load_csv("global_trade", "trade_partners_top5.csv"),
        "shipping_index_pivoted": load_csv("global_trade", "shipping_index_pivoted.csv", parse_dates=["date"]),
        "shipping_index_correlation": load_csv("global_trade", "shipping_index_correlation.csv"),
        "shipping_index_3m_volatility": load_csv("global_trade", "shipping_index_3m_volatility.csv", parse_dates=["date"]),
        # Insights and AI analysis
        "insights": load_json("global_trade", "key_insights.json"),
        "gemini_insight": load_text("global_trade", "gemini_insight_gloal_trade.txt"),
    }

@lru_cache(maxsize=None)
def load_korea_trade_data():
    return {
        # Export/Import Trade Analysis
        "export_top_partners": load_csv("korea_trade", "export_top_partners.csv"),
        "import_top_partners": load_csv("korea_trade", "import_top_partners.csv"),
        
        # Export/Import Items Analysis
        "export_top_items_by_amount": load_csv("korea_trade", "export_top_items_by_amount.csv"),
        "export_top_items_by_yoy": load_csv("korea_trade", "export_top_items_by_yoy.csv"),
        "import_top_items_by_amount": load_csv("korea_trade", "import_top_items_by_amount.csv"),
        "import_top_items_by_yoy": load_csv("korea_trade", "import_top_items_by_yoy.csv"),
        
        # Trade YoY Analysis
        "trade_yoy_top_export_partners": load_csv("korea_trade", "trade_yoy_top_export_partners.csv"),
        "trade_yoy_top_import_partners": load_csv("korea_trade", "trade_yoy_top_import_partners.csv"),
        "trade_balance": load_csv("korea_trade", "trade_balance.csv", parse_dates=["date"]),
        
        # Value Index Analysis
        "value_index_top_yoy": load_csv("korea_trade", "value_index_top_yoy.csv"),
        "value_index_bottom_yoy": load_csv("korea_trade", "value_index_bottom_yoy.csv"),
        "value_index_volatility": load_csv("korea_trade", "value_index_volatility.csv"),
        
        # Semiconductor Billings Analysis
        "wsts_top_monthly_regions": load_csv("korea_trade", "wsts_top_monthly_regions.csv"),
        "wsts_top_annual_regions": load_csv("korea_trade", "wsts_top_annual_regions.csv"),
        "wsts_volatility": load_csv("korea_trade", "wsts_volatility.csv"),
        "wsts_trend_monthly": load_csv("korea_trade", "wsts_trend_monthly.csv", parse_dates=["date"]),
        "wsts_trend_annual": load_csv("korea_trade", "wsts_trend_annual.csv", parse_dates=["date"]),
        "wsts_yoy_monthly": load_csv("korea_trade", "wsts_yoy_monthly.csv", parse_dates=["date"]),
        "wsts_yoy_annual": load_csv("korea_trade", "wsts_yoy_annual.csv", parse_dates=["date"]),
        "wsts_market_share_monthly": load_csv("korea_trade", "wsts_market_share_monthly.csv", parse_dates=["date"]),
        
        # Insights and AI analysis
        "insights": load_json("korea_trade", "key_insights.json"),
        "gemini_insight": load_text("korea_trade", "gemini_insights_korea_trade.txt"),
        "gemini_insights_data": load_json("korea_trade", "gemini_insights_data.json"),
    }
