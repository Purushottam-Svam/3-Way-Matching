from OCR.gemini_ocr import extract_document
# from extraction.openai_extractor import (
#     extract_invoice,
#     extract_po,
#     extract_grn
# )
from matching.three_way_matcher import three_way_match


invoice = extract_document("data/Inv_1.pdf" , "invoice")
po = extract_document("data/SamTell_PO_OCR_Fixed.pdf" , "po")
grn = extract_document("data/SamTell_GRN_OCR_Fixed.pdf" , "grn")

result = three_way_match(invoice, po, grn)