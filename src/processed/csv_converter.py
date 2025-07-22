import os
import csv
import ast
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")


def extract_insights_from_summary(summary_text, report_name, year):
    prompt = f"""
From the following summary of a {report_name} {year} report, extract the main insights as a list of dictionaries. Each dictionary should include:

- "report": always "{report_name}"
- "year": {year}
- "topic": the main theme or subject of the insight
- "insight": a concise, factual statement

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
        print(f"\nFailed to parse Gemini response: {e}")
        print("Raw response:\n", response.text)
        return []


def save_insights_to_csv(insights, csv_path):
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["report", "year", "topic", "insight"])
        writer.writeheader()
        writer.writerows(insights)
    print(f"✅ Saved {len(insights)} insights to: {csv_path}")


def process_summary_file(summary_path, report_name, year, output_csv_path):
    with open(summary_path, "r", encoding="utf-8") as f:
        text = f.read()

    insights = extract_insights_from_summary(text, report_name, year)

    if insights:
        save_insights_to_csv(insights, output_csv_path)
    else:
        print(f"No insights extracted from {report_name}.")


# Run summaries
process_summary_file(
    summary_path=r"C:/Users/va26/Desktop/global event/data/processed/defence/sipri_summary_gemini.txt",
    report_name="SIPRI",
    year=2025,
    output_csv_path=r"C:/Users/va26/Desktop/global event/data/processed/defence/sipri_insights.csv"
)

process_summary_file(
    summary_path=r"C:/Users/va26/Desktop/global event/data/processed/energy/opec_summary_gemini.txt",
    report_name="OPEC",
    year=2025,
    output_csv_path=r"C:/Users/va26/Desktop/global event/data/processed/energy/opec_insights.csv"
)
