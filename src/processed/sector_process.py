import pandas as pd
from pandas import to_datetime

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

    df_long = pd.melt(
        df,
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



