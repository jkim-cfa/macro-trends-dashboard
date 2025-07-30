import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define base path to EDA outputs
EDA_DIR = os.getenv("EDA_DIR", "eda_outputs")
INSIGHT_DIR = os.path.join(EDA_DIR, "outputs")  # Specifically for insight .txt files
os.makedirs(INSIGHT_DIR, exist_ok=True)

def load_sector_insights():
    """Load AI insight .txt files for all sectors into a dictionary."""
    insights = {}
    sectors = ["Agriculture", "Defence", "Economy", "Energy", "Industry", "Global Trade", "Korea Trade"]
    
    for sector in sectors:
        filename = f"{sector.lower().replace(' ', '_')}_insight.txt"
        file_path = os.path.join(INSIGHT_DIR, filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    insights[sector] = f.read()
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        else:
            print(f"⚠️ Insight file not found: {file_path}")
    
    return insights
