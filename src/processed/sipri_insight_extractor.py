import fitz

# Extract All Text from PDF
pdf_path = r"C:/Users/va26/Desktop/global event/data/defence/SIPRI_yearbook.pdf"
output_txt_path = r"C:/Users/va26/Desktop/global event/data/processed/defence/sipri_summary_cleaned.txt"

doc = fitz.open(pdf_path)
all_text = [page.get_text() for page in doc]
doc.close()

with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_text))

print(f"Full text saved to: {output_txt_path}")
