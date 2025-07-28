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
def load_economy_data():
    return {
        "fx_rates": load_csv("economy", "fx_rates.csv", parse_dates=["date"]),
        "confidence": load_csv("economy", "confidence_indices.csv", parse_dates=["date"]),
        "cycle": load_csv("economy", "economic_cycle.csv", parse_dates=["date"]),
        "insights": load_json("economy", "key_insights.json"),
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
def load_energy_data():
    return {
        "global": load_csv("energy", "global_energy_data.csv", parse_dates=["date"]),
        "monthly": load_csv("energy", "monthly_report.csv", parse_dates=["date"]),
        "oil_stocks": load_csv("energy", "oil_stocks.csv", parse_dates=["date"]),
        "petronet": load_csv("energy", "petronet_data.csv", parse_dates=["date"]),
        "insights": load_json("energy", "key_insights.json"),
    }

@lru_cache(maxsize=None)
def load_industry_data():
    return {
        "manufacturing": load_csv("industry", "manufacturing_data.csv", parse_dates=["date"]),
        "steel": load_csv("industry", "steel_data.csv", parse_dates=["date"]),
        "insights": load_json("industry", "key_insights.json"),
    }

@lru_cache(maxsize=None)
def load_global_trade_data():
    return {
        "bdi": load_csv("global_trade", "bdi_data.csv", parse_dates=["date"]),
        "trade": load_csv("global_trade", "trade_data.csv", parse_dates=["date"]),
        "semiconductor": load_csv("global_trade", "semiconductor_data.csv", parse_dates=["date"]),
        "insights": load_json("global_trade", "key_insights.json"),
    }

@lru_cache(maxsize=None)
def load_korea_trade_data():
    return {
        "exports": load_csv("korea_trade", "korea_exports.csv", parse_dates=["date"]),
        "kotra": load_csv("korea_trade", "kotra_data.csv", parse_dates=["date"]),
        "trade_items": load_csv("korea_trade", "trade_items.csv", parse_dates=["date"]),
        "insights": load_json("korea_trade", "key_insights.json"),
    }
