CREATE OR REPLACE VIEW unified_macro_view as
-- Agriculture: crop production
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  CONCAT(indicator, ' - ', commodity) AS indicator, 
  CAST(value AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM agriculture_crop_production_processed
UNION all
-- Defence: bid info
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  CONCAT(indicator, ' - ', category, ' - ', item) AS indicator, 
  CAST(value AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM defence_bid_info_processed
UNION all
-- Defence: SIPRI insights
SELECT 
  CAST(year || '-01-01' AS DATE) AS date, 
  'World' AS country, 
  sector, 
  topic AS indicator, 
  NULL::DOUBLE PRECISION AS value, 
  NULL::TEXT AS unit, 
  report AS source, 
  'defence' AS domain, 
  'sipri_insight' AS file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  insight
FROM defence_sipri_insights
UNION all
-- Economy: confidence indices
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  CONCAT(category, ' - ', indicator) AS indicator, 
  CAST(value AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM economy_economy_confidence_processed
UNION ALL
-- Economy: FX rates
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  CONCAT(currency, ' to ', quote) AS indicator, 
  CAST(exchange_rate AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM economy_fx_rates_processed
UNION ALL
-- Economy: Leading vs Coincident Indicators and KOSPI
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  indicator, 
  CAST(value AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM economy_leading_vs_coincident_kospi_processed
UNION ALL
-- Energy: IEA oil stocks
SELECT 
  CAST(date AS DATE) AS date, 
  country, 
  sector, 
  'IEA Oil Stocks' AS indicator, 
  CAST(value AS DOUBLE PRECISION) AS value, 
  unit, 
  source, 
  domain, 
  file_source, 
  NULL::TEXT AS partner, 
  NULL::TEXT AS period, 
  NULL::TEXT AS period_type, 
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM energy_iea_oil_stocks_processed
UNION ALL
-- Energy: Oil imports with continents
SELECT 
  CAST(date AS DATE) AS date,
  country,
  sector,
  unit AS indicator,  -- Using 'unit' to differentiate the metric (e.g., USD/bbl, thousand bbl)
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM energy_oil_imports_with_continents_processed
UNION ALL
-- Energy: OPEC insights
SELECT 
  CAST(year || '-01-01' AS DATE) AS date,
  'World' AS country,
  sector,
  topic AS indicator,
  NULL::DOUBLE PRECISION AS value,
  NULL::TEXT AS unit,
  report AS source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  insight
FROM energy_opec_insights
UNION ALL
-- Industry: manufacturing inventory
SELECT 
  CAST(date AS DATE) AS date,
  country,
  sector,
  category AS indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  NULL::TEXT AS unit,
  source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM industry_manufacture_inventory_processed
UNION ALL
-- Industry: steel combined
SELECT 
  CAST(date AS DATE) AS date,
  region AS country,
  sector,
  indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM industry_steel_combined_processed
UNION ALL
-- Trade: global export decrease items top 5
SELECT 
  CAST(date AS DATE) AS date,
  country,
  domain AS sector,
  CONCAT(commodity_name, ' - ', indicator) AS indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  'KOTRA' AS source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_global_export_decrease_items_top5_processed
UNION ALL
-- Trade: global export increase items top 5
SELECT 
  CAST(date AS DATE) AS date,
  country,
  domain AS sector,
  CONCAT(commodity_name, ' - ', indicator) AS indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  'KOTRA' AS source,
  domain,
  file_source,
  NULL::TEXT AS partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_global_export_increase_items_top5_processed
UNION ALL
-- Trade: Global bilateral trade indicators
SELECT 
  CAST(date AS DATE) AS date,
  country,
  'trade' AS sector,
  indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_global_trade_processed
UNION ALL
-- Trade: Global bilateral trade variation top 5
SELECT 
  CAST(date AS DATE) AS date,
  country,
  'trade' AS sector,
  indicator,
  CAST(value AS DOUBLE PRECISION) AS value,
  unit,
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_global_trade_variation_top5_processed
UNION ALL
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  'Export YoY (%)',
  CAST(trade_yoy AS DOUBLE PRECISION),
  '%'::TEXT,
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_export_country_variation_processed
WHERE trade_yoy IS NOT NULL
UNION ALL
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  'Export Share (%)',
  CAST(trade_share AS DOUBLE PRECISION),
  '%'::TEXT,
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_export_country_variation_processed
WHERE trade_share IS NOT NULL
UNION ALL
-- Trade: Export Amount by Item
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  CONCAT('Export Amount - ', commodity_name),
  CAST(export_amount AS DOUBLE PRECISION),
  'thousand USD',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_export_increase_items_processed
UNION ALL
-- Trade: Export YoY by Item
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  CONCAT('Export YoY (%) - ', commodity_name),
  CAST(trade_yoy AS DOUBLE PRECISION),
  '%'::TEXT,
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_export_increase_items_processed
WHERE trade_yoy IS NOT NULL
UNION ALL
-- Korea Import Amount by Country
SELECT
  CAST(date AS DATE),
  country,
  'trade' AS sector,
  CONCAT('Import Amount - ', partner) AS indicator,
  CAST(import_amount AS DOUBLE PRECISION),
  'thousand USD',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_import_country_variation_processed
UNION ALL
-- Korea Import YoY by Country
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  CONCAT('Import YoY (%) - ', partner),
  CAST(trade_yoy AS DOUBLE PRECISION),
  '%',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_import_country_variation_processed
WHERE trade_yoy IS NOT NULL
UNION ALL
-- Korea Import Share by Country
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  CONCAT('Import Share (%) - ', partner),
  CAST(trade_share AS DOUBLE PRECISION),
  '%',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_import_country_variation_processed
WHERE trade_share IS NOT NULL
UNION ALL
-- Korea Import Amount by Commodity (Increasing Items)
SELECT
  CAST(date AS DATE),
  country,
  'trade' AS sector,
  CONCAT('Import Amount - ', commodity_name) AS indicator,
  CAST(import_amount AS DOUBLE PRECISION),
  'thousand USD',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_import_increase_items_processed
UNION ALL
-- Korea Import YoY by Commodity (Increasing Items)
SELECT
  CAST(date AS DATE),
  country,
  'trade',
  CONCAT('Import YoY (%) - ', commodity_name),
  CAST(trade_yoy AS DOUBLE PRECISION),
  '%',
  source,
  domain,
  file_source,
  partner,
  NULL::TEXT AS period,
  NULL::TEXT AS period_type,
  NULL::TEXT AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_import_increase_items_processed
WHERE trade_yoy IS NOT NULL
UNION all
--Korea_trade_items_yoy_processed
SELECT
  CAST(date AS DATE),
  country,
  sector,
  CONCAT(category, ' - ', indicator) AS indicator,
  CAST(value AS DOUBLE PRECISION),
  unit,
  source,
  domain,
  file_source,
  NULL AS partner,
  NULL AS period,
  NULL AS period_type,
  NULL AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_trade_items_yoy_processed
UNION all
--Korea_trade_yoy_processed
SELECT
  CAST(date AS DATE),
  country,
  sector,
  CONCAT(category, ' - ', indicator) AS indicator,
  CAST(value AS DOUBLE PRECISION),
  unit,
  source,
  domain,
  file_source,
  partner,
  NULL AS period,
  NULL AS period_type,
  NULL AS frequency,
  NULL::TEXT AS insight
FROM trade_korea_trade_yoy_processed
UNION all
-- shipping_indices_processed
SELECT
  CAST(date AS DATE),
  country,
  sector,
  indicator,
  CAST(value AS DOUBLE PRECISION),
  unit,
  source,
  domain,
  file_source,
  null as partner,
  NULL AS period,
  NULL AS period_type,
  NULL AS frequency,
  NULL::TEXT AS insight
FROM trade_shipping_indices_processed
UNION all
-- wsts_billings_latest_processed
SELECT
  CAST(date AS DATE),
  country,
  sector,
  indicator,
  CAST(value AS DOUBLE PRECISION),
  unit,
  source,
  domain,
  file_source,
  null as partner,
  NULL AS period,
  NULL AS period_type,
  NULL AS frequency,
  NULL::TEXT AS insight
from trade_wsts_billings_latest_processed