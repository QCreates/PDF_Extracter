import pdfplumber
import re
import pandas as pd

INPUT_PDF = "casegoods.pdf"
OUTPUT_XLSX = "extracted_skus.xlsx"

def recover_skus(raw):
    """
    Take a raw number string from the PDF (e.g., '331111113300')
    and try to extract valid 6-digit SKUs from it.
    """
    # Find all 6-digit substrings inside the raw number
    return re.findall(r"\d{6}", raw)

def extract_skus(pdf_path):
    skus = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                # Grab any 6+ digit sequences
                raw_numbers = re.findall(r"\d{6,}", text)
                for num in raw_numbers:
                    for sku in recover_skus(num):
                        skus.append({"Page": page_num, "SKU": sku})
    return skus

sku_list = extract_skus(INPUT_PDF)

# Deduplicate
df = pd.DataFrame(sku_list).drop_duplicates()
df.to_excel(OUTPUT_XLSX, index=False)

print(f"✅ Extracted {len(df)} SKUs and saved to {OUTPUT_XLSX}")
