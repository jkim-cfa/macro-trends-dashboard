import fitz
from dotenv import load_dotenv
import os

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR")

# Extract All Text from PDF
pdf_path = os.path.join(DATA_DIR, "defence", "SIPRI_yearbook.pdf")
output_txt_path = os.path.join(DATA_DIR, "processed", "defence", "sipri_summary_cleaned.txt")

doc = fitz.open(pdf_path)
all_text = [page.get_text() for page in doc]
doc.close()

with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_text))

print(f"Full text saved to: {output_txt_path}")
