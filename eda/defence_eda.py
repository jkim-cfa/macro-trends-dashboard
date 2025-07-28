import os
import re
import warnings
import pandas as pd
import json
from collections import Counter
from sqlalchemy import create_engine
from dotenv import load_dotenv
import google.generativeai as genai

# Configuration
warnings.filterwarnings('ignore')
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)

EDA_DIR = os.getenv("EDA_DIR")
eda_path = os.path.join(EDA_DIR, "outputs", "defence")

# DB connection
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")

engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Load defence data
query = """
SELECT date, indicator, value, insight, file_source
FROM unified_macro_view
WHERE domain = 'defence'
ORDER BY date
"""
df = pd.read_sql(query, engine)
df['date'] = pd.to_datetime(df['date'])

# Stop words
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

# High-value contracts (value >= 10 billion KRW)
def high_value_contracts(df):
    bid_df = df[df['file_source'] == 'bid_info_processed'].copy()
    high_value_df = bid_df[bid_df['value'] >= 10000000000].copy()
    high_value_df['category'] = 'High-Value (≥ 10B KRW)'
    high_value_df['indicator'] = high_value_df['indicator'].apply(clean_texts)
    return high_value_df

# Emergency procurement (value > 50 million KRW)
def emergency_procurement(df):
    bid_df = df[df['file_source'] == 'bid_info_processed'].copy()
    emergency_df = bid_df[bid_df['indicator'].str.contains('긴급', na=False) & (bid_df['value'] > 50000000)].copy()
    emergency_df['category'] = 'Emergency Procurement'
    emergency_df['indicator'] = emergency_df['indicator'].apply(clean_texts)
    return emergency_df

# Frequent word analysis (value >= 500 million KRW)
def frequent_word_analysis(df):
    bid_df = df[df['file_source'] == 'bid_info_processed'].copy()
    value_500m_df = bid_df[bid_df['value'] >= 500000000].copy()
    value_500m_df['category'] = 'Medium-Value (≥ 500M KRW)'

    # Clean and tokenise
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
    frequent_df = value_500m_df[
        value_500m_df['indicator'].apply(lambda x: any(word in x for word in meaningful_words))
    ].copy()

    # Update category to show frequency for each matched item
    for idx, indicator_text in frequent_df['indicator'].items():
        matching_words = [word for word in meaningful_words if word in indicator_text]
        if matching_words:
            # Get the highest frequency among matching words
            max_freq = max(word_counts[word] for word in matching_words)
            frequent_df.loc[idx, 'category'] = f"Frequent Items ({max_freq} times)"
    
    return frequent_df, meaningful_words, word_counts

def save_eda_data(df, output_dir=eda_path):
    os.makedirs(output_dir, exist_ok=True)

    high_value_df = high_value_contracts(df).drop_duplicates(subset=['indicator', 'value', 'date'])
    high_value_df.to_csv(f'{output_dir}/high_value_contracts.csv', index=False, encoding='utf-8-sig')
 
    emergency_df = emergency_procurement(df).drop_duplicates(subset=['indicator', 'value', 'date'])
    emergency_df.to_csv(f'{output_dir}/emergency_contracts.csv', index=False, encoding='utf-8-sig')
    
    frequent_items_df, meaningful_words, word_counts = frequent_word_analysis(df)
    frequent_items_df.to_csv(f'{output_dir}/frequent_items.csv', index=False, encoding='utf-8-sig')
    
    # Combined results
    combined_df = pd.concat([high_value_df, emergency_df, frequent_items_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['indicator', 'value', 'date'])
    combined_df = combined_df.sort_values('value', ascending=False)
    combined_df.to_csv(f'{output_dir}/defense_contracts_analysis.csv', index=False, encoding='utf-8-sig')

    # Word frequency analysis
    ammunition_keywords = {"mm", "밀리"}

    # Word frequency analysis with annotation
    word_frequency_df = pd.DataFrame([
        {
            'word': f"{word} (탄약)" if word in ammunition_keywords else word,
            'frequency': count
        }
        for word, count in word_counts.most_common(10)
    ])

    # Save the output
    word_frequency_df.to_csv(f'{output_dir}/word_frequency_analysis.csv', index=False, encoding='utf-8-sig')

    # Comprehensive insights
    key_insights = {
        "summary_statistics": {
            "total_contracts_analysed": len(combined_df),
            "total_contract_value": float(combined_df['value'].sum()),
            "average_contract_value": float(combined_df['value'].mean()),
        },
        "category_breakdown": {
            "high_value_contracts": len(high_value_df),
            "emergency_contracts": len(emergency_df),
            "frequent_items": len(frequent_items_df),
        },
        "value_analysis": {
            "contract_value_distribution": combined_df['value'].describe().to_dict(),
            "category_value_stats": combined_df.groupby('category')['value'].agg(['count', 'mean', 'median', 'sum']).round(2).to_dict(orient='index'),
        },
        "frequency_analysis": {
            "top_10_frequent_words": meaningful_words[:10],
            "total_unique_words": len(word_counts),
            "words_appearing_5plus_times": len([w for w, c in word_counts.items() if c >= 5]),
        },
        "temporal_analysis": {
            "date_range": {
                "earliest": combined_df['date'].min().strftime('%Y-%m-%d'),
                "latest": combined_df['date'].max().strftime('%Y-%m-%d'),
            },
            "contracts_by_year": combined_df.groupby(combined_df['date'].dt.year).size().to_dict(),
        },
        "top_contracts": {
            "highest_value_contracts": combined_df.nlargest(10, 'value')[['indicator', 'value', 'date', 'category']].to_dict('records'),
        }
    }
    
    # Save insights
    with open(f"{output_dir}/comprehensive_insights.json", "w", encoding='utf-8') as f:
        json.dump(key_insights, f, indent=2, ensure_ascii=False, default=str)
    
    return key_insights, combined_df


# Gemini Insight
def generate_insights(key_insights, combined_df, insight_text, output_dir):
    try:
        prompt = f""" 
**Role**: You are a senior economic strategist analyzing cross-sector ripple effects. Extract non-obvious implications from the data below.

**Data Inputs**:
1. SIPRI Insight:
\"\"\"
{insight_text}
\"\"\"

2. Summary Statistics:
{json.dumps(key_insights["summary_statistics"], indent=2, ensure_ascii=False)}

3. Category Breakdown:
{json.dumps(key_insights["category_breakdown"], indent=2, ensure_ascii=False)}

4. Value Distribution (contract_value_distribution):
{json.dumps(key_insights["value_analysis"]["contract_value_distribution"], indent=2, ensure_ascii=False)}

5. Category Value Stats:
{json.dumps(key_insights["value_analysis"]["category_value_stats"], indent=2, ensure_ascii=False)}

6. Word Frequency (top procurement terms):
{json.dumps(key_insights["frequency_analysis"], indent=2, ensure_ascii=False)}

7. Timeline: {key_insights['temporal_analysis']['date_range']['earliest']} to {key_insights['temporal_analysis']['date_range']['latest']}

---


### **Required Output Format**
## Defence Sector Second-Order Effect Analysis

### Core Trend
• Defence: [TREND SUMMARY IN 5–10 WORDS]  
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

        with open(f"{output_dir}/gemini_insight.txt", "w", encoding="utf-8") as f:
            f.write(gemini_insight)

        print("✅ Gemini insights generated and saved.")

    except Exception as e:
        print(f"❌ Gemini insight generation failed: {e}")

# Main execution
if __name__ == "__main__":
    try:
        full_df = df.copy()
        df_clean = df.drop(columns=['insight'])

        insights, combined_data = save_eda_data(df_clean)

        # Extract SIPRI insight text for Gemini
        sipri_text = (
            full_df.loc[
                full_df['file_source'] == 'sipri_insight', 'insight'
            ]
            .dropna()
            .unique()
        )
        insight_text = "\n".join(sipri_text)

        # Print 3 SIPRI insight
        print("🔍 First 3 SIPRI insight rows:")
        for i, row in enumerate(sipri_text[:3]):
            print(f"{i+1}. {row}\n")

        # Save the SIPRI insight text
        with open(f"{eda_path}/sipri_insight.txt", "w", encoding="utf-8") as f:
            f.write(insight_text)

        # Run Gemini insight generation
        generate_insights(insights, combined_data, insight_text, eda_path)

        print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")