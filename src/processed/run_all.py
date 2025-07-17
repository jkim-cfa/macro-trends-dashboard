from processed.sector_process import crop_production, bid_info, confidence, fxrate, economic_indicator, \
    iea_oil_stocks, oil_import_summary, manufacture_inventory, steel_combined, global_trade_variation_top5, global_trade_trend, \
    global_export, korea_trade_trend, korea_export_import_items, ecos_trade_detail, ecos_trade_items, shipping_indices

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
    (global_trade_variation_top5, "trade", "global_trade_variation_top5"),
    (global_trade_trend, "trade", "global_trade"),
    (ecos_trade_detail, "trade", "korea_trade_yoy"),
    (ecos_trade_items, "trade", "korea_trade_items_yoy"),
    (shipping_indices, "trade", "shipping_indices")
]

GLOBAL_EXPORT_ITEMS = [
    ("global_export_increase_items_top5", "increase"),
    ("global_export_decrease_items_top5", "decrease")
]

KOREA_TRADE_TREND = [
    ("korea_export_country_variation", "export"),
    ("korea_import_country_variation", "import")
]

KOREA_EXPORT_IMPORT_ITEMS = [
    ("korea_export_increase_items", "export"),
    ("korea_import_increase_items", "import")
]

def run_all():
    for func, sector, name in TASKS:
        input_path = f"C:/Users/va26/Desktop/global event/data/{sector}/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/{sector}/{name}_processed.csv"
        func(input_path, output_path)

    for name, direction in GLOBAL_EXPORT_ITEMS:
        input_path = f"C:/Users/va26/Desktop/global event/data/trade/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/trade/{name}_processed.csv"
        global_export(input_path, output_path, direction)

    for name, direction in KOREA_TRADE_TREND:
        input_path = f"C:/Users/va26/Desktop/global event/data/trade/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/trade/{name}_processed.csv"
        korea_trade_trend(input_path, output_path, direction)

    for name, direction in KOREA_EXPORT_IMPORT_ITEMS:
        input_path = f"C:/Users/va26/Desktop/global event/data/trade/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/trade/{name}_processed.csv"
        korea_export_import_items(input_path, output_path, direction)

if __name__ == "__main__":
    run_all()
