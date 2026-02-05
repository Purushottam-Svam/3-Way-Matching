from OCR.tesseract_ocr import ocr_document
from extraction.openai_extractor import (
    extract_invoice,
    extract_po,
    extract_grn
)
from matching.three_way_matcher import three_way_match


def main():
    # -------------------
    # 1. OCR
    # -------------------
    invoice_text = ocr_document("data/Inv_1.pdf")
    po_text = ocr_document("data/SamTell_PO_OCR_Fixed.pdf")
    grn_text = ocr_document("data/SamTell_GRN_OCR_Fixed.pdf")

    # --- ADD THIS PRINT STATEMENT HERE ---
    print("\n--- DEBUG: RAW OCR TEXT START ---", flush=True)
    print(invoice_text, flush=True)
    print("--- DEBUG: RAW OCR TEXT END ---\n", flush=True)

    # -------------------
    # 2. LLM Extraction
    # -------------------
    invoice = extract_invoice(invoice_text)
    po = extract_po(po_text)
    grn = extract_grn(grn_text)

    # -------------------
    # 3. 3-Way Matching
    # -------------------
    result = three_way_match(invoice, po, grn)

    # -------------------
    # 4. Output
    # -------------------
    print("3-WAY MATCH RESULT:")
    print(result)


if __name__ == "__main__":
    main()
