import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pdf2image import convert_from_path

from utilities.debug_logger import log_debug
from OCR.invoice_model import InvoiceDocument
from OCR.po_model import PurchaseOrderDocument
from OCR.grn_model import GRNDocument


# -------------------------
# CONFIG
# -------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

client = genai.Client(api_key=API_KEY)

POPPLER_PATH = r"C:\Users\PurushottamKaushik\Documents\OCR_test\poppler-24.08.0\Library\bin"

MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview"
]


# -------------------------
# Helpers
# -------------------------
def _extract_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end + 1]


# -------------------------
# Main OCR + Parsing
# -------------------------
def extract_document(pdf_path: str, doc_type: str) -> dict:
    # -------------------------
    # 1. PDF → Image
    # -------------------------
    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    temp_img = "__temp_page.png"
    images[0].save(temp_img, "PNG")

    log_debug(doc_type, "pdf_to_image_done", pdf_path)

    with open(temp_img, "rb") as f:
        image_bytes = f.read()

    # -------------------------
    # 2. Prompt
    # -------------------------
    prompt = """
Return ONLY raw JSON. The response must start with { and end with }.

Return the document details in VALID JSON ONLY.

Do not include markdown.
Do not include explanations.
Return raw JSON text.
"""

    response_text = None

    # -------------------------
    # 3. Try models
    # -------------------------
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/png"
                    )
                ]
            )
            response_text = response.text
            break
        except Exception as e:
            log_debug(doc_type, f"model_failed_{model_name}", str(e))
            continue

    os.remove(temp_img)

    if not response_text:
        raise RuntimeError("Gemini extraction failed for all models")

    # -------------------------
    # 4. Parse JSON (RAW)
    # -------------------------
    raw_text = response_text.strip()
    log_debug(doc_type, "gemini_raw_output", raw_text)

    json_text = _extract_json_block(raw_text)

    if not json_text:
        log_debug(doc_type, "non_json_response", raw_text)
        raise RuntimeError("Gemini did not return parsable JSON")

    try:
        raw_data = json.loads(json_text)
        log_debug(doc_type, "parsed_json_raw", raw_data)
    except json.JSONDecodeError:
        log_debug(doc_type, "json_parse_error", json_text)
        raise

    # -------------------------
    # 5. BaseModel Normalization
    # -------------------------
    if doc_type == "invoice":
        parsed = InvoiceDocument.model_validate(raw_data).model_dump()

    elif doc_type == "po":
        parsed = PurchaseOrderDocument.model_validate(raw_data).model_dump()

    elif doc_type == "grn":
        parsed = GRNDocument.model_validate(raw_data).model_dump()

    else:
        raise RuntimeError(f"Unknown doc_type: {doc_type}")

    log_debug(doc_type, "parsed_json_normalized", parsed)
    return parsed
