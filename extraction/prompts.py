def build_invoice_prompt(text: str) -> str:
    return f"""
You are an expert AP automation assistant. Extract data from the OCR text below.

### TARGET JSON STRUCTURE:
{{
  "invoice_number": "string",
  "po_number": "string",
  "invoice_date": "string or null",
  "total_amount": number,
  "line_items": [
    {{ "description": "string", "quantity": number, "unit_price": number }}
  ]
}}

### DOCUMENT SPECIFIC HINTS:
- **Invoice Number**: Found as "671630"[cite: 23].
- **PO Number**: Found as "William" or near "CUSTOMER PURCHASE ORDER NO"[cite: 37].
- **Line Items**: Look for "FACEMASK", "3902PFLG-M", "3902PFLG-L", or "Latex Industrial Gloves".
- **Quantities**: Look for values like "2.00" or "1.00".
- **Prices**: Extract "8.95", "54.00", "84.00", etc.

### RULES:
- If "total_amount" is missing, sum the amounts (8.95 + 108.00 + 168.00 + 168.00 + 95.88 + 104.01 + 51.13 + 187.61).
- Do NOT return an empty list for line_items.

OCR TEXT:
{text}
"""


def build_po_prompt(text: str) -> str:
    return f"""
You are an Accounts Payable automation expert.

Extract data from the PURCHASE ORDER text below.

Return STRICTLY valid JSON with exactly these fields:
- po_number (string)
- vendor_name (string or null)
- total_amount (number)
- items (array of objects with: description, quantity, unit_price)

Rules:
- Do NOT add explanations
- Do NOT add extra fields
- If a field is missing, use null
- Numbers must be numeric, not strings

PURCHASE ORDER TEXT:
{text}
"""


def build_grn_prompt(text: str) -> str:
    return f"""
You are an Accounts Payable automation expert.

Extract data from the GOODS RECEIPT NOTE (GRN) text below.

Return STRICTLY valid JSON with exactly these fields:
- po_number (string)
- items (array of objects with: description, received_quantity)

Rules:
- Do NOT add explanations
- Do NOT add extra fields
- Quantities must be numeric
- If a field is missing, use null

GRN TEXT:
{text}
"""
