import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from extraction.prompts import (
    build_invoice_prompt,
    build_po_prompt,
    build_grn_prompt
)
from utilities.validators import validate_extracted_json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ExtractionError(Exception):
    """Raised when OpenAI extraction fails or returns invalid data."""
    pass

def _clean_json(text: str) -> str:
    """Removes markdown backticks and whitespace."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    return text.strip()

def _call_openai(prompt: str) -> dict:
    """Calls OpenAI and ensures valid JSON is returned."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        output_text = response.choices[0].message.content.strip()
        cleaned = _clean_json(output_text)
        return json.loads(cleaned)
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {str(e)}")

def extract_invoice(text: str) -> dict:
    prompt = build_invoice_prompt(text)
    data = _call_openai(prompt)
    # This will now pass because our prompt is more aggressive
    validate_extracted_json(data, doc_type="invoice")
    return data

def extract_po(text: str) -> dict:
    prompt = build_po_prompt(text)
    data = _call_openai(prompt)
    validate_extracted_json(data, doc_type="po")
    return data

def extract_grn(text: str) -> dict:
    prompt = build_grn_prompt(text)
    data = _call_openai(prompt)
    validate_extracted_json(data, doc_type="grn")
    return data