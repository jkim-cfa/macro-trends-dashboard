from processed.sector_process import crop_production, bid_info, confidence, fxrate, economic_indicator, \
    iea_oil_stocks, oil_import_summary, manufacture_inventory, steel_combined, KOTRA_global_trade_variation_top5

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
    (KOTRA_global_trade_variation_top5, "trade", "global_trade_variation_top5")
]

def run_all():
    for func, sector, name in TASKS:
        input_path = f"C:/Users/va26/Desktop/global event/data/{sector}/{name}.csv"
        output_path = f"C:/Users/va26/Desktop/global event/data/processed/{sector}/{name}_processed.csv"
        func(input_path, output_path)

if __name__ == "__main__":
    run_all()
