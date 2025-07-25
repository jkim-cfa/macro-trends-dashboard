import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB", "macrodb")
PG_HOST = "localhost"
PG_PORT = 5432

# DB connection
engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")

# Query KOSPI data
query = """
SELECT date, indicator, value
FROM unified_macro_view
WHERE indicator = 'KOSPI'
ORDER BY date
"""
df = pd.read_sql(query, engine)
df['date'] = pd.to_datetime(df['date'])

# Pivot and calculate rolling stats
pivot = df.pivot_table(index='date', columns='indicator', values='value', aggfunc='mean')
pivot['KOSPI_rolling'] = pivot['KOSPI'].rolling(window=12).mean()

# Fetch actual insights from the DB - FIXED QUOTES
energy_query = "SELECT insight FROM unified_macro_view WHERE file_source = 'opec_insights' LIMIT 1;"
defence_query = "SELECT insight FROM unified_macro_view WHERE file_source = 'sipri_insight' LIMIT 1;"

with engine.connect() as conn:
    energy_insight = conn.execute(text(energy_query)).scalar() or "No insight available"
    defence_insight = conn.execute(text(defence_query)).scalar() or "No insight available"

# Plot
fig, ax = plt.subplots(figsize=(12, 7))
pivot[['KOSPI', 'KOSPI_rolling']].plot(ax=ax)
ax.set_title("KOSPI with 12-Month Rolling Mean")
ax.set_ylabel("Index")
ax.grid(True)

# Add space below plot
fig.subplots_adjust(bottom=0.25)

# Add actual text annotations under the plot
fig.text(0.01, 0.12, f"Energy Insight: {energy_insight}", ha='left', wrap=True, fontsize=9)
fig.text(0.01, 0.06, f"Defence Insight: {defence_insight}", ha='left', wrap=True, fontsize=9)

plt.show()