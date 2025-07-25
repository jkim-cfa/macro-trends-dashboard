import os
import csv
import ast
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env and configure Gemini
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")

def extract_insights_from_summary(summary_text, report_name, year, sector):
    prompt = f"""
From the following summary of a {report_name} {year} report, extract the main insights as a list of dictionaries. Each dictionary should include:

- "report": always "{report_name}"
- "year": {year}
- "topic": the main theme or subject of the insight
- "insight": a concise, factual statement
- "sector": always "{sector}"

Summary:
\"\"\" 
{summary_text}
\"\"\" 
Only return a Python list of dictionaries.
"""

    response = MODEL.generate_content(prompt)

    try:
        raw = response.text.strip()

        # Remove markdown ```python ... ``` if present
        cleaned = re.sub(r"^```(?:python)?\s*|```$", "", raw, flags=re.MULTILINE).strip()

        # Safe evaluation
        insights = ast.literal_eval(cleaned)

        if isinstance(insights, dict):
            insights = [insights]

        if not isinstance(insights, list) or not all(isinstance(x, dict) for x in insights):
            raise ValueError("Response is not a list of dictionaries.")

        return insights

    except Exception as e:
        print(f"\n❌ Failed to parse Gemini response: {e}")
        print("Raw response:\n", response.text)
        return []

def process_summary_file(summary_path, report_name, year, output_csv_path):
    with open(summary_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract folder name as sector
    sector = Path(summary_path).parent.name

    insights = extract_insights_from_summary(text, report_name, year, sector)

    if insights:
        save_insights_to_csv(insights, output_csv_path)
    else:
        print(f"No insights extracted from {report_name}.")

def save_insights_to_csv(insights, csv_path):
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["report", "year", "topic", "insight", "sector"])
        writer.writeheader()
        writer.writerows(insights)
    print(f"✅ Saved {len(insights)} insights to: {csv_path}")

# Run summaries
process_summary_file(
    summary_path=os.path.join(DATA_DIR, "processed", "defence", "sipri_summary_gemini.txt"),
    report_name="SIPRI",
    year=2025,
    output_csv_path=os.path.join(DATA_DIR, "processed", "defence", "sipri_insights.csv")
)

process_summary_file(
    summary_path=os.path.join(DATA_DIR, "processed", "energy", "opec_summary_gemini.txt"),
    report_name="OPEC",
    year=2025,
    output_csv_path=os.path.join(DATA_DIR, "processed", "energy", "opec_insights.csv")
)
