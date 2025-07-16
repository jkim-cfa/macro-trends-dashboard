import pandas as pd
from datetime import datetime
import pycountry

## Agriculture Sector
def crop_production(input_path, output_path):
    df = pd.read_csv(input_path)

    # standardise columns
    df['date'] = pd.to_datetime(df['marketYear'].astype(str) + '-' + df['report_month'].astype(str).str.zfill(2) + '-01')
    df['country'] = df['countryCode']
    df['sector'] = 'agriculture'
    df['indicator'] = df['attributeId']
    df['commodity'] = df['commodityName']
    df['unit'] = df['unitId']
    df['source'] = 'USDA PSD'

    # reorder columns
    final_df = (df[['date', 'country', 'sector', 'indicator', 'commodity', 'value', 'unit', 'source']]
        .sort_values(by=['commodity', 'country', 'date']))

    # save
    final_df.to_csv(output_path, index=False)
    print(f'Saved cleaned data to {output_path}')

## Defence Sector
def bid_info(input_path, output_path):
    df = pd.read_csv(input_path, encoding='utf-8-sig')

    # standardise columns
    df['date'] = pd.to_datetime(df['orderPrearngeMt'].astype(str) + '01', format='%Y%m%d')
    df['country'] = 'South Korea'
    df['sector'] = 'defence'
    df['indicator'] = df['progrsSttus']
    df['category'] = df['excutTy']
    df['value'] = pd.to_numeric(df['budgetAmount'], errors='coerce')
    df['unit'] = 'KRW'
    df['agency'] = df['ornt']
    df['item'] = df['reprsntPrdlstNm']
    df['source'] = 'DAPA KOREA'

    # reorder columns
    final_df = df[[
        'date', 'country', 'sector', 'indicator',
        'category', 'item','value', 'unit', 'agency', 'source'
    ]].sort_values(by=['date', 'agency', 'value'])

    # save
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

## Economy Sector
def confidence(input_path, output_path):
    df = pd.read_csv(input_path)

    # standardise columns
    df = df.rename(columns={
        'STAT_CODE': 'category',
        'ITEM_NAME1': 'indicator',
        'DATA_VALUE': 'value'
    })

    df['date'] = pd.to_datetime(df['TIME'].astype(str) + '01', format='%Y%m%d')
    df['country'] = 'South Korea'
    df['sector'] = 'economy'
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['unit'] = 'index'
    df['source'] = 'ECOS'

    # reorder columns
    final_df = (df[['date', 'country', 'sector', 'category', 'indicator', 'value', 'unit', 'source']]
                .sort_values(by=['date', 'category','indicator']))

    # save
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

def fxrate(input_path, output_path):
    df = pd.read_csv(input_path)

    # standardise columns
    df = df.rename(columns={
        'DATE': 'date',
        'EXCHANGE_RATE': 'exchange_rate',
        'UNIT_NAME': 'unit'
    })

    df[['quote', 'currency']] = df['CURRENCY'].apply(
        lambda x: pd.Series(x.split('/') if '/' in x else ['KRW', x])
    )

    df['date'] = pd.to_datetime(df['date'])
    df['country'] = 'South Korea'
    df['sector'] = 'economy'
    df['source'] = 'ECOS'

    # reorder columns
    final_df = (df[[ 'date', 'country','sector', 'currency', 'quote', 'exchange_rate', 'unit', 'source']]
                .sort_values(by=['date', 'currency']))

    # save
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

def economic_indicator(input_path, output_path):
    df = pd.read_csv(input_path)

    # Standardise columns
    df = df.rename(columns={'datetime' : 'date'})
    df['date'] = pd.to_datetime(df['date'])

    df['country'] = 'South Korea'
    df['sector'] = 'economy'
    df['source'] = 'ECOS'
    df['unit'] = 'index'

    df_long = df.melt(
        id_vars=['date', 'country', 'sector', 'source', 'unit'],
        var_name='indicator',
        value_name='value'
    )

    df_long['indicator'] = pd.Categorical(
        df_long['indicator'],
        categories=['KOSPI', '동행지수순환변동치', '선행지수순환변동치', '선행-동행'],
        ordered=True
    )

    final_df = (df_long[['date', 'country', 'sector', 'indicator', 'value', 'unit', 'source']].sort_values(by=['date', 'indicator']))

    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

## Energy Sector
def iea_oil_stocks(input_path, output_path):
    df = pd.read_csv(input_path)

    # standardise columns
    df['date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'] + '-01')

    df = df.rename(columns={'countryName': 'country'})
    df = df[df['total'] != 'Net Exporter']

    df['value'] = pd.to_numeric(df['total'], errors='coerce')
    df['sector'] = 'energy'
    df['source'] = 'IEA'
    df['unit'] = 'kb/d'

    final_df = df[['date', 'country', 'sector', 'source', 'value', 'unit']].sort_values(by=['date', 'country', 'value'])

    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

def oil_import_summary(input_path, output_path):
    df = pd.read_csv(input_path)

    # date
    df = df[df['Month'] != 'Total']
    df['date'] = pd.to_datetime(df['Month'].astype(str) + '-01')

    df_long = df.melt(
        id_vars=['date'],
        var_name='country_unit',
        value_name='value'
    )

    df_long[['country', 'unit']] = df_long['country_unit'].str.extract(r'^(.*?)\s*\((.*?)\)$')

    # region mapping
    region_map = {
        'Asia': ['필리핀', '말레이시아', '인도네시아', '호주', '뉴질랜드', '파푸아뉴기니', '카자흐스탄'],
        'Africa': ['알제리', '콩고', '나이지리아', '적도기니', '모잠비크'],
        'America': ['캐나다', '미국', '멕시코', '브라질', '에콰도르'],
        'MiddleEast': ['이라크', '쿠웨이트', '카타르', '아랍에미레이트', '사우디아라비아', '오만', '중립지대'],
        'Europe': ['노르웨이', '영국']
    }
    country_to_region = {country: region for region, countries in region_map.items() for country in countries}
    df_long['region'] = df_long['country'].map(country_to_region).fillna(df_long['country'])

    # English
    country_name_map = {'필리핀': 'Philippines','말레이시아': 'Malaysia','인도네시아': 'Indonesia',
        '호주': 'Australia','뉴질랜드': 'New Zealand','파푸아뉴기니': 'Papua New Guinea',
        '카자흐스탄': 'Kazakhstan','알제리': 'Algeria','콩고': 'Congo','나이지리아': 'Nigeria','적도기니': 'Equatorial Guinea',
        '모잠비크': 'Mozambique','캐나다': 'Canada','미국': 'United States','멕시코': 'Mexico','브라질': 'Brazil',
        '에콰도르': 'Ecuador','이라크': 'Iraq','쿠웨이트': 'Kuwait','카타르': 'Qatar','아랍에미레이트': 'UAE',
        '사우디아라비아': 'Saudi Arabia','오만': 'Oman','중립지대': 'Neutral Zone',
        '노르웨이': 'Norway','영국': 'United Kingdom'
    }
    df_long['country'] = df_long['country'].map(country_name_map).fillna(df_long['country'])

    # convert % strings to float
    mask_percent = df_long['unit'] == '%'
    df_long.loc[mask_percent, 'value'] = (df_long.loc[mask_percent, 'value']
                                          .astype(str).str.replace('%', '', regex=False)
                                          .astype(float))

    df_long['sector'] = 'energy'
    df_long['source'] = 'PETRONET'

    df_long['unit'] = pd.Categorical(
        df_long['unit'],
        categories=['%', 'Value', 'Vol', 'Price'],
        ordered=True
    )
    unit_map = {
        'Value': 'thousand USD',
        'Price': 'USD/bbl',
        'Vol': 'thousand bbl',
        '%': 'percentage'
    }
    df_long['unit'] = df_long['unit'].map(unit_map)

    df_long = df_long[['date', 'region', 'country', 'value', 'unit', 'sector', 'source']].sort_values(by=['date', 'country', 'unit'])

    df_long.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to: {output_path}')

# Industry Sector
def manufacture_inventory(input_path, output_path):
    df = pd.read_csv(input_path)

    # standardise columns
    df = df.rename(columns={
        'STAT_NAME': 'category',
        'DATA_VALUE': 'value'
    })
    rename_map = {
        '8.1.3. 설비투자지수': '설비투자지수',
        '8.3.5. 제조업 재고율': '제조업 재고율'
    }
    df['category'] = df['category'].map(rename_map)


    df['date'] = pd.to_datetime(df['TIME'].astype(str) + '01', format='%Y%m%d')
    df['country'] = 'South Korea'
    df['sector'] = 'industry'
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['unit'] = 'index'
    df['source'] = 'ECOS'

    # reorder columns
    final_df = (df[['date', 'country', 'sector', 'category', 'value', 'source']]
                .sort_values(by=['date', 'category']))

    # save
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to {output_path}')

def steel_combined(input_path, output_path):
    df = pd.read_csv(input_path)

    # Drop and standardize
    df.drop(columns=['Scope'], inplace=True)
    df['sector'] = 'trade'
    df['source'] = 'World Steel Association'
    df['unit'] = 'percentage'
    df['region'] = df['Region']

    # Rename Turkey
    df['region'] = df['region'].replace('Türkiye', 'Turkey')

    # Melt the DataFrame first
    yoy_cols = [col for col in df.columns if 'YoY' in col]

    df_long = df.melt(
        id_vars=['region', 'sector', 'unit', 'source'],
        value_vars=yoy_cols,
        var_name='indicator',
        value_name='value'
    )

    # Now extract date from melted 'indicator' column
    month_strs = df_long['indicator'].str.split().str[0]
    year_strs = df_long['indicator'].str.split().str[1]
    month_nums = month_strs.str[:3].apply(lambda x: datetime.strptime(x, '%b').month)

    df_long['date'] = pd.to_datetime(year_strs + '-' + month_nums.astype(str).str.zfill(2) + '-01', errors='coerce')

    # Final cleanup and save
    final_df = df_long[['date', 'region', 'sector', 'indicator', 'value', 'unit', 'source']]
    final_df = final_df.sort_values(by=['date', 'region'])

    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f'Saved cleaned data to: {output_path}')

# Trade Sector
# KOTRA Global Trade Variation Top 5
def KOTRA_global_trade_variation_top5(input_path, output_path):
    df = pd.read_csv(input_path)

    # Date
    df['date'] = pd.to_datetime(df['baseYr'].astype(str) + '-01-01')

    # Drop
    df.drop(columns=['expItcNatCd', 'impItcNatCd', 'expCountryNm', 'impCountryNm', 'hscd', 'cmdltDisplayNm', 'rank'], inplace=True)

    # Convert ISO codes to country names
    ISO2_TO_COUNTRY = {c.alpha_2: c.name for c in pycountry.countries}
    df['country'] = df['expIsoWd2NatCd'].map(ISO2_TO_COUNTRY).fillna(df['expIsoWd2NatCd'])
    df['partner'] = df['impIsoWd2NatCd'].map(ISO2_TO_COUNTRY).fillna(df['impIsoWd2NatCd'])

    # Rename indicators
    indicator_rename = {
        'expAmt': 'export_amount',
        'expVaritnRate': 'export_yoy',
        'expMkshRate': 'export_share',
        'impMkshRate': 'import_share'
    }
    df = df.rename(columns=indicator_rename)

    # Melt indicators
    melt_cols = list(indicator_rename.values())

    df_long = df.melt(
        id_vars=['date', 'country', 'partner'],
        value_vars=melt_cols,
        var_name='indicator',
        value_name='value'
    )

    # Assign units based on indicator
    unit_map = {
        'export_amount': 'USD',
        'export_yoy': '%',
        'export_share': '%',
        'import_share': '%'
    }
    df_long['unit'] = df_long['indicator'].map(unit_map)

    # Add static columns
    df_long['sector'] = 'trade'
    df_long['source'] = 'KOTRA'

    # Sort and save
    df_long = df_long.sort_values(by=['date', 'country', 'partner', 'indicator'])
    df_long.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved cleaned file to: {output_path}")