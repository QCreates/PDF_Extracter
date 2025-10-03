import pdfplumber
import re
import pandas as pd
import os

INPUT_DIR = "bh_pdfs"          # folder with your 6 PDFs
OUTPUT_XLSX = "extracted_skus.xlsx"

def recover_skus(raw):
    """
    Default extractor:
    - Must contain at least one digit
    - Must not start with '66299'
    - Take odd-position characters
    - Accept if >= 5 alphanumeric chars
    """
    if not any(ch.isdigit() for ch in raw):
        return []
    if raw.startswith("66299"):
        return []

    filtered = raw[::2]  # odd-position chars
    if len(filtered) >= 5 and filtered.isalnum():
        return [filtered.upper()]
    return []

def recover_skus_swivel(raw):
    """
    Special extractor for swivel_chair.pdf:
    - Handles slash-separated SKUs
    - Rebuilds shortened forms with prefix
    - Must contain at least one digit
    """
    results = []
    parts = raw.split("/")
    if len(parts) > 1:
        base = parts[0]
        for i, part in enumerate(parts):
            if i == 0:
                results.append(base)
            else:
                if len(part) < len(base):
                    prefix_len = len(base) - len(part)
                    results.append(base[:prefix_len] + part)
                else:
                    results.append(part)
    else:
        results.append(raw)

    # Enforce: must have at least one digit + 5+ chars
    filtered = [
        sku.strip().upper()
        for sku in results
        if re.match(r"^[A-Z0-9]{5,}$", sku.strip()) and any(ch.isdigit() for ch in sku)
    ]
    return filtered

def extract_skus_from_pdf(pdf_path, fname):
    skus = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Allow alphanumerics and '/' for split SKUs
                raw_numbers = re.findall(r"[A-Za-z0-9/]{5,}", text)
                for num in raw_numbers:
                    # Use special extractor for swivel_chair.pdf
                    if fname.lower() == "swivel_chair.pdf":
                        extracted = recover_skus_swivel(num)
                    else:
                        extracted = recover_skus(num)

                    for sku in extracted:
                        skus.append(sku)
    return skus

all_skus = []
for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith(".pdf"):
        pdf_path = os.path.join(INPUT_DIR, fname)
        skus = extract_skus_from_pdf(pdf_path, fname)
        for sku in skus:
            all_skus.append({"PDF File": fname, "SKU": sku})

# Deduplicate across everything
df = pd.DataFrame(all_skus).drop_duplicates()

# Save only columns PDF File, SKU
df[["PDF File", "SKU"]].to_excel(OUTPUT_XLSX, index=False)

print(f"✅ Extracted {len(df)} SKUs from {INPUT_DIR} into {OUTPUT_XLSX}")
