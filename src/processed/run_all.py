from processed.sector_process import crop_production, bid_info, confidence, fxrate, economic_indicator, \
    iea_oil_stocks, oil_import_summary, manufacture_inventory, steel_combined, KOTRA_global_trade_variation_top5, KOTRA_global_trade, \
    KOTRA_global_export, korea_trade_trend

TASKS = [
    (crop_production, "agriculture", "crop_production"),
    (bid_info, "defence", "bid_info"),
    (confidence, "economy", "economy_confidence"),
    (fxrate, "economy", "fx_rates"),
    (economic_indicator, "economy", "leading_vs_coincident_kospi"),
    (iea_oil_stocks, "energy", "iea_oil_stocks"),
    (oil_import_summary, "energy", "oil_imports_with_continents"),
    (manufacture_inventory, "industry", "manufacture_inventory"),
    (steel_combined, "industry", "steel_combined"),
    (KOTRA_global_trade_variation_top5, "trade", "global_trade_variation_top5"),
    (KOTRA_global_trade, "trade", "global_trade")
]

KOTRA_EXPORT_ITEMS = [
    ("global_export_increase_items_top5", "increase"),
    ("global_export_decrease_items_top5", "decrease")
]

KOTRA_KOREA_TRADE_TREND = [
    ("korea_export_country_variation", "export"),
    ("korea_import_country_variation", "import")
]

def run_all():
    for func, sector, name in TASKS:
        input_path = f"C:/Users/va26/Desktop/global event/data/{sector}/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/{sector}/{name}_processed.csv"
        func(input_path, output_path)

    for name, direction in KOTRA_EXPORT_ITEMS:
        input_path = f"C:/Users/va26/Desktop/global event/data/trade/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/trade/{name}_processed.csv"
        KOTRA_global_export(input_path, output_path, direction)

    for name, direction in KOTRA_KOREA_TRADE_TREND:
        input_path = f"C:/Users/va26/Desktop/global event/data/trade/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/trade/{name}_processed.csv"
        KOTRA_global_export(input_path, output_path, direction)

if __name__ == "__main__":
    run_all()
