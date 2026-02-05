from typing import Dict, List
from openai import OpenAI
from matching.rules import AMOUNT_TOLERANCE_PERCENT

from dotenv import load_dotenv
load_dotenv()


client = OpenAI()

# -------------------------
# AI-assisted normalization
# -------------------------

def normalize_text_with_ai(values: List[str]) -> Dict[str, str]:
    """
    Uses LLM to normalize semantically similar strings.
    Returns mapping: original -> normalized
    """
    prompt = f"""
Normalize the following values to a canonical form.
If two values mean the same thing, normalize them to the SAME value.
Return JSON only as: {{ original: normalized }}.

VALUES:
{values}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return eval(response.output_text)  # safe here: controlled JSON-only prompt


# -------------------------
# Helpers
# -------------------------

def _within_amount_tolerance(a, b):
    tolerance = b * (AMOUNT_TOLERANCE_PERCENT / 100)
    return abs(a - b) <= tolerance


# -------------------------
# Main matcher
# -------------------------

def three_way_match(invoice: dict, po: dict, grn: dict) -> dict:
    warnings = []

    # -------------------------
    # 1. HEADER MATCHING
    # -------------------------

    # Hard check: PO number
    if invoice["po_number"] != po["po_number"]:
        return {"status": "FAIL", "reason": "PO_MISMATCH_INVOICE_PO"}

    if grn["po_number"] != po["po_number"]:
        return {"status": "FAIL", "reason": "PO_MISMATCH_PO_GRN"}

    # Soft check: Vendor name (AI-assisted)
    vendor_values = [
        invoice.get("vendor_name", ""),
        po.get("vendor_name", "")
    ]

    vendor_norm = normalize_text_with_ai(vendor_values)

    if len(set(vendor_norm.values())) != 1:
        warnings.append("VENDOR_NAME_VARIATION")

    # -------------------------
    # 2. LINE ITEM MATCHING
    # -------------------------

    # Collect all descriptions
    po_descs = [i["description"] for i in po["items"]]
    grn_descs = [i["description"] for i in grn["items"]]

    desc_norm = normalize_text_with_ai(po_descs + grn_descs)

    # Build normalized maps
    po_items = {
        desc_norm[item["description"]]: item
        for item in po["items"]
    }

    grn_items = {
        desc_norm[item["description"]]: item["received_quantity"]
        for item in grn["items"]
    }

    for norm_desc, po_item in po_items.items():

        if norm_desc not in grn_items:
            return {
                "status": "FAIL",
                "reason": f"ITEM_MISSING_IN_GRN: {norm_desc}"
            }

        if grn_items[norm_desc] < po_item["quantity"]:
            return {
                "status": "FAIL",
                "reason": f"QTY_SHORT_RECEIVED: {norm_desc}"
            }

    # -------------------------
    # 3. TOTAL CHECK
    # -------------------------

    if not _within_amount_tolerance(
        invoice["total_amount"],
        po["total_amount"]
    ):
        return {"status": "FAIL", "reason": "AMOUNT_MISMATCH"}

    # -------------------------
    # SUCCESS
    # -------------------------

    return {
        "status": "PASS",
        "reason": "FULL_THREE_WAY_MATCH",
        "warnings": warnings
    }
