import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env credentials
load_dotenv()

PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB", "macrodb")
PG_HOST = "localhost"
PG_PORT = 5432

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

# Base directory of your processed CSV files
base_dir = Path("data/processed")

# Loop through all CSV files
for domain_dir in base_dir.iterdir():
    if not domain_dir.is_dir():
        continue
    domain = domain_dir.name
    for file in domain_dir.glob("*.csv"):
        table_name = f"{domain}_{file.stem}".lower().replace("-", "_")
        print(f"🔄 Uploading: {file} → table: {table_name}")
        try:
            df = pd.read_csv(file)
            df["domain"] = domain
            df["file_source"] = file.stem
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"✅ Done: {table_name}")
        except Exception as e:
            print(f"❌ Failed on {file}: {e}")
