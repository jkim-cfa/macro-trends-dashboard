import fitz
import re
import os
from dotenv import load_dotenv

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "data")

OPEC_PDF = os.path.join(DATA_DIR, "energy", "OPEC_MOMR_Latest.pdf")
OPEC_RAW_TXT = os.path.join(DATA_DIR, "processed", "energy", "opec_summary_extracted.txt")
OPEC_CLEANED_TXT = os.path.join(DATA_DIR, "processed", "energy", "opec_summary_cleaned.txt")

# Extract summary pages 5-6
def extract_opec_report(pdf_path, output_txt_path):
    doc = fitz.open(pdf_path)
    extracted_text = []
    for page_num in range(4, 6):  # Pages 5-6
        text = doc.load_page(page_num).get_text("text") # type: ignore
        extracted_text.append(text)
    doc.close()
    
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(extracted_text))
    print(f"Pages 5–6 extracted to: {output_txt_path}")
    return True

# Clean summary text
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
    for i, header in enumerate(section_headers[:-1]):  # Skip last
        pattern = re.escape(header)
        next_pattern = re.escape(section_headers[i + 1])
        
        match = re.search(f"{pattern}(.*?){next_pattern}", raw_text, re.DOTALL)
        if match:
            cleaned = re.sub(r'\n+', '\n', match.group(1).strip())
            cleaned = re.sub(r'[ \t]+', ' ', cleaned)
            sections[header] = cleaned

    with open(output_path, 'w', encoding='utf-8') as f:
        for title, body in sections.items():
            f.write(f"## {title}\n\n{body}\n\n")

    print(f"Cleaned summary saved to: {output_path}")
    return True

# Extract feature article (page 7 only)
def extract_opec_feature_article(pdf_path):
    doc = fitz.open(pdf_path)
    text = doc.load_page(6).get_text("text") # type: ignore
    doc.close()
    print(f"Feature Article extracted successfully")
    return text

# Clean feature article text directly
def clean_feature_text_directly(text):
    lines = text.split('\n')
    cleaned_lines = []
    skip_next = 0

    for line in lines:
        if skip_next > 0:
            skip_next -= 1
            continue

        if line.strip().startswith("Graph 1:") or line.strip().startswith("Graph 2:"):
            skip_next = 2  # Skip this line + next 2 lines
            continue

        cleaned_lines.append(line)

    # Remove trailing junk from the cleaned text
    cleaned_text = remove_trailing_junk_from_text('\n'.join(cleaned_lines))
    
    print(f"Feature article text cleaned successfully")
    return cleaned_text

def remove_trailing_junk_from_text(text):
    lines = text.split('\n')
    cleaned_lines = []

    # Step 1: Try to find last meaningful paragraph
    last_content_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.endswith('.') and
            len(stripped) > 50 and
            not stripped.startswith(('Sources:', 'Source:', 'Graph', 'Chart'))):
            last_content_idx = i

    # Base: keep up to last paragraph if found
    if last_content_idx >= 0:
        cleaned_lines = lines[:last_content_idx + 1]
        remaining_lines = lines[last_content_idx + 1:]
    else:
        remaining_lines = lines

    # Shared pattern filters
    patterns = [
        r'^-?\d+([,\d]*)?$',
        r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{2}$',
        r'^US\$/b$',
        r'^1,000 contracts$',
        r'^Sources?:\s*.+$',
        r'^.+\s+\((LHS|RHS)\)$',
        r'^(Naphtha|Jet/Kerosene|Gasoline 93|Gasoil \(ULSD 62\)|Fuel oil \(380c 3\.5s\))$',
    ]

    # Step 2: Filter remaining lines
    for line in remaining_lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        if any(re.match(pattern, stripped) for pattern in patterns):
            continue
        if (len(stripped) > 20 and 
            any(word in stripped.lower() for word in ['the', 'and', 'of', 'in', 'to', 'for', 'with'])):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

# Process OPEC complete report
def process_opec_complete_report(pdf_path=OPEC_PDF):
    if pdf_path is None:
        pdf_path = OPEC_PDF
    extract_opec_report(pdf_path, OPEC_RAW_TXT)
    clean_opec_summary(OPEC_RAW_TXT, OPEC_CLEANED_TXT)

    feature_text = extract_opec_feature_article(pdf_path)
    cleaned_feature = clean_feature_text_directly(feature_text)

    with open(OPEC_CLEANED_TXT, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## Feature Article\n\n{cleaned_feature}\n")

def main():
    process_opec_complete_report()
    print("\n All processing completed successfully!")

if __name__ == "__main__":
    main()