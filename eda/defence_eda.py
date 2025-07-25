import os
import re
import warnings
import pandas as pd
from collections import Counter, defaultdict
from sqlalchemy import create_engine
from dotenv import load_dotenv
import numpy as np

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "macro2025")
PG_DB = os.getenv("POSTGRES_DB", "macrodb")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connect to PostgreSQL
engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

# Load defence data
query = """
SELECT date, indicator, value, insight
FROM unified_macro_view
WHERE domain = 'defence'
ORDER BY date
"""
df = pd.read_sql(query, engine)
df['date'] = pd.to_datetime(df['date'])

def clean_texts(indicator):
    s = str(indicator)

    # Remove administrative prefixes
    if ' - ' in s:
        s = s.rsplit(' - ', 1)[-1]

    # Remove year patterns (including quoted years and ranges)
    s = re.sub(r"('?\d{2}년~'?\d{2}년)", '', s)  # 25년~27년
    s = re.sub(r"('?\d{2}~'?\d{2}년)", '', s)  # 25~27년
    s = re.sub(r"('?\d{2}~'?\d{2})", '', s)      # '25~'29
    s = re.sub(r"'?\d{2}년", '', s)               # '25년 or 25년
    s = re.sub(r"'?\d{2}\s", ' ', s)              # '25 (standalone)
    
    # Remove quotation marks
    s = re.sub(r'[\'"]', '', s)
    
    # Clean up remaining artifacts
    s = re.sub(r'\s*~\s*', ' ', s)  # Clean ~ with spaces
    s = re.sub(r'\s+', ' ', s).strip()  # Normalise whitespace
    
    return s

stop_words = [
    # Administrative/Generic terms
    '구매', '방산', '용역', '임차용역', '수송용역', '제조구매', '생산제조',
    '계룡대', '직장어린이집', '식자재', '급식', '민간위탁배송', '부대조달',
    'EA', 'Batch', '가구', '노트북', '얼음정수기', '프린터', '모니터',
    '스프레이부스', '리스자산', '폐기물', '호스', '교과서', '2학기', '정비',
    '설치용역', '원격검침',
    # Overly generic military terms
    '부품', '제조', '정비', '외주정비', '수리부속', '신축', '관급자재',
    '부품류', '관급', '교체', '제조설치', '일반', '전지', '기체', '조끼용',
    '창정비', '납품', '설치', '레미콘', '간부숙소', '노후', '항목', '트럭',
    '위탁관리', '작전수행능력', '개선', '통제소', '일반공구', '소모품',
    '여과기', '자재', '실린더', '적재용',
    # Numbering/classification systems
    '6종', '2종', '2차', '00부대', '20비', '31종', '리스물건',
    # Redundant technical terms
    '회로카드조립체', '유지부품', '조립체', '체계', '구성품', '민간위탁', '배송용역',
    # Location/event terms
    'Seoul', 'ADEX', '통합홍보관', '관사', '동원훈련장','취사식당'
]

# High-value contracts (value >= 10 billion KRW)
high_value_df = df[df['value'] >= 10000000000].copy()
high_value_df['category'] = 'High-Value (≥ 10B KRW)'

# Emergency procurement (value > 50 million KRW)
emergency_df = df[df['indicator'].str.contains('긴급', na=False) & (df['value'] > 50000000)].copy()
emergency_df['category'] = 'Emergency Procurement'

# Contracts ≥ 500 million KRW for frequent word analysis
value_500m_df = df[df['value'] >= 500000000].copy()
value_500m_df['category'] = 'Medium-Value (≥ 500M KRW)'

# Clean all indicators and tokenize for frequent word analysis
value_500m_df['indicator'] = value_500m_df['indicator'].apply(clean_texts)
all_tokens = []

for text in value_500m_df['indicator']:
    tokens = re.findall(r'[가-힣]{2,}|[A-Za-z]{2,}\d*[A-Za-z]*', text)
    filtered = [token for token in tokens 
                if token not in stop_words and not re.fullmatch(r'\d+', token)]
    all_tokens.extend(filtered)

# Count frequency and find meaningful words
word_counts = Counter(all_tokens)
meaningful_words = [word for word, count in word_counts.items() if count >= 3]

# Find matching rows for meaningful words and update category with frequency
matches = value_500m_df[
    value_500m_df['indicator'].apply(lambda x: any(word in x for word in meaningful_words))
].copy()

# Update category to show frequency for each matched item
for idx, indicator_text in matches['indicator'].items():
    matching_words = [word for word in meaningful_words if word in indicator_text]
    if matching_words:
        # Get the highest frequency among matching words
        max_freq = max(word_counts[word] for word in matching_words)
        matches.loc[idx, 'category'] = f"Frequent Items ({max_freq} times)"

# Clean indicators for other dataframes
high_value_df['indicator'] = high_value_df['indicator'].apply(clean_texts)
emergency_df['indicator'] = emergency_df['indicator'].apply(clean_texts)

# Combine all dataframes
combined_df = pd.concat([high_value_df, emergency_df, matches], ignore_index=True)
combined_df = combined_df.drop_duplicates()

# Sort by value in descending order
combined_df = combined_df.sort_values('value', ascending=False)
combined_df = combined_df.drop_duplicates(subset=['indicator','value'])

# Save combined results to single CSV file
combined_df.to_csv("defense_contracts_analysis.csv", index=False, encoding='utf-8-sig')

print(f"Found {len(meaningful_words)} meaningful words with frequency >= 3")
print(f"High-value contracts: {len(high_value_df)}")
print(f"Emergency contracts: {len(emergency_df)}")
print(f"Medium-value matches: {len(matches)}")
print(f"Total combined contracts: {len(combined_df)}")
