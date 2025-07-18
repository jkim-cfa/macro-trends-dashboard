import fitz  # PyMuPDF
import os
import re

# --- Paths ---
BASE_DIR = r"C:/Users/va26/Desktop/global event/data"
ENERGY_DIR = os.path.join(BASE_DIR, "energy")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed/energy")

OPEC_PDF = os.path.join(ENERGY_DIR, "OPEC_MOMR_Latest.pdf")
OPEC_RAW_TXT = os.path.join(PROCESSED_DIR, "opec_summary_extracted.txt")
OPEC_CLEANED_TXT = os.path.join(PROCESSED_DIR, "opec_summary_cleaned.txt")

OPEC_FEATURE_RAW_TXT = os.path.join(PROCESSED_DIR, "opec_feature_raw.txt")
OPEC_FEATURE_CLEANED_TXT = os.path.join(PROCESSED_DIR, "opec_feature_cleaned.txt")


# --- Extract summary pages 5–6 ---
def extract_opec_report(pdf_path, output_txt_path):
    doc = fitz.open(pdf_path)
    extracted_text = []
    for page_num in range(4, 6):
        text = doc.load_page(page_num).get_text("text")
        extracted_text.append(text)
    doc.close()
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(extracted_text))
    print(f"✓ Pages 5–6 extracted to: {output_txt_path}")


# --- Clean summary text ---
def clean_opec_summary(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    section_headers = [
        "Crude Oil Price Movements",
        "World Economy",
        "World Oil Demand",
        "World Oil Supply",
        "Product Markets and Refining Operations",
        "Tanker Market",
        "Crude and Refined Product Trade",
        "Commercial Stock Movements",
        "Balance of Supply and Demand",
        "Feature Article"
    ]

    sections = {}
    for i, header in enumerate(section_headers):
        pattern = re.escape(header)
        next_pattern = re.escape(section_headers[i + 1]) if i + 1 < len(section_headers) else None
        match = re.search(f"{pattern}(.*?){next_pattern}" if next_pattern else f"{pattern}(.*)", raw_text, re.DOTALL)
        if match:
            cleaned = re.sub(r'\n+', '\n', match.group(1).strip())
            cleaned = re.sub(r'[ \t]+', ' ', cleaned)
            sections[header] = cleaned

    with open(output_path, 'w', encoding='utf-8') as f:
        for title, body in sections.items():
            f.write(f"## {title}\n\n{body}\n\n")
    print(f"✓ Cleaned summary saved to: {output_path}")


# --- Extract feature article (page 7 only) ---
def extract_opec_feature_article(pdf_path, output_txt_path):
    doc = fitz.open(pdf_path)
    text = doc.load_page(6).get_text("text")
    doc.close()
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✓ Feature Article (page 7) extracted to: {output_txt_path}")


# --- Clean feature article with graph removal first ---
def clean_opec_feature_article(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    skip_next = 0

    for line in lines:
        if skip_next > 0:
            skip_next -= 1
            continue

        if line.strip().startswith("Graph 1:") or line.strip().startswith("Graph 2:"):
            skip_next = 2  # This line + next 2 lines (total 3)
            continue

        cleaned_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print(f"✓ Cleaned Feature Article saved to: {output_path}")


def remove_trailing_junk(input_path, output_path):
    patterns = [
        r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{2}',  # Month-Year
        r'^\\d{1,4}(,\\d{3})*$',  # Numbers (e.g., 1,000)
        r'^(US\\$/b|contracts|Sources?:|\\d+)$',  # Units, sources, single numbers
        r'^[A-Za-z ]+\\(RHS\\)|\\(LHS\\)$',  # Legends
        r'^[A-Za-z0-9 /().%-]+$',  # Standalone legends/labels
    ]
    import re
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    cleaned = []
    for line in lines:
        if any(re.match(pat, line.strip()) for pat in patterns):
            continue
        cleaned.append(line)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned)
    print(f"✓ Trailing junk removed and saved to: {output_path}")


# --- Run everything ---
if __name__ == "__main__":
    extract_opec_report(OPEC_PDF, OPEC_RAW_TXT)
    clean_opec_summary(OPEC_RAW_TXT, OPEC_CLEANED_TXT)
    remove_trailing_junk(OPEC_CLEANED_TXT, OPEC_CLEANED_TXT)
    extract_opec_feature_article(OPEC_PDF, OPEC_FEATURE_RAW_TXT)
    clean_opec_feature_article(OPEC_FEATURE_RAW_TXT, OPEC_FEATURE_CLEANED_TXT)
