from typing import Dict, List
import json
from openai import OpenAI
from matching.rules import AMOUNT_TOLERANCE_PERCENT

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

# -------------------------
# AI-assisted normalization
# -------------------------

def normalize_text_with_ai(values: List[str]) -> Dict[str, str]:
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

    raw = response.output_text.strip()

    # Strip markdown if present
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)


# -------------------------
# Helpers
# -------------------------

def _within_amount_tolerance(a, b):
    tolerance = b * (AMOUNT_TOLERANCE_PERCENT / 100)
    return abs(a - b) <= tolerance


# -------------------------
# Adapters (KEY FIX)
# -------------------------

def _unwrap_invoice(invoice: dict) -> dict:
    if "invoice" in invoice:
        invoice = invoice["invoice"]

    return {
        "po_reference": invoice.get("po_reference"),
        "vendor_name": invoice.get("vendor_name"),
        "line_items": invoice.get("line_items", []),
        "total_amount": invoice.get("total_amount")
    }


def _unwrap_po(po: dict) -> dict:
    if "purchase_order" in po:
        po = po["purchase_order"]

    return {
        "po_number": po.get("order_details", {}).get("po_number"),
        "vendor_name": po.get("vendor_details", {}).get("name"),
        "line_items": po.get("line_items", []),
        "total_amount": po.get("total_amount")
    }


def _unwrap_grn(grn: dict) -> dict:
    if "grn" in grn:
        grn = grn["grn"]

    return {
        "po_number": grn.get("po_number"),
        "line_items": grn.get("line_items", grn.get("items", []))
    }


# -------------------------
# Main matcher
# -------------------------

def three_way_match(invoice: dict, po: dict, grn: dict) -> dict:
    warnings = []
    confidence = 1.0

    # -------------------------
    # 0. Normalize document shapes
    # -------------------------

    invoice = _unwrap_invoice(invoice)
    po = _unwrap_po(po)
    grn = _unwrap_grn(grn)

    # -------------------------
    # 1. HEADER MATCHING
    # -------------------------

    # if invoice.get("po_reference") != po.get("po_number"):
    #     confidence *= 0.1
    #     return {
    #         "status": "FAIL",
    #         "reason": "INVOICE_PO_REFERENCE_MISMATCH",
    #         "confidence": confidence
    #     }

    if grn.get("po_number") != po.get("po_number"):
        confidence *= 0.1
        return {
            "status": "FAIL",
            "reason": "GRN_PO_NUMBER_MISMATCH",
            "confidence": confidence
        }

    # Vendor name (soft check, AI-assisted)
    vendor_values = [
        invoice.get("vendor_name", ""),
        po.get("vendor_name", "")
    ]

    vendor_norm = normalize_text_with_ai(vendor_values)

    if len(set(vendor_norm.values())) != 1:
        confidence *= 0.85
        warnings.append("VENDOR_NAME_VARIATION")

    # -------------------------
    # 2. LINE ITEM MATCHING
    # -------------------------

    po_items_raw = po.get("line_items", [])
    grn_items_raw = grn.get("line_items", [])

    po_descs = [i["description"] for i in po_items_raw]
    grn_descs = [i["description"] for i in grn_items_raw]

    desc_norm = normalize_text_with_ai(po_descs + grn_descs)

    po_items = {
        desc_norm[item["description"]]: item
        for item in po_items_raw
    }

    grn_items = {
        desc_norm[item["description"]]: item.get("received_quantity", item.get("qty_recv", 0))
        for item in grn_items_raw
    }

    for norm_desc, po_item in po_items.items():
        if norm_desc not in grn_items:
            confidence *= 0.6
            return {
                "status": "FAIL",
                "reason": f"ITEM_MISSING_IN_GRN: {norm_desc}",
                "confidence": confidence
            }

        if grn_items[norm_desc] < po_item.get("qty_ord", po_item.get("quantity", 0)):
            confidence *= 0.6
            return {
                "status": "FAIL",
                "reason": f"QTY_SHORT_RECEIVED: {norm_desc}",
                "confidence": confidence
            }

    # -------------------------
    # 3. TOTAL AMOUNT CHECK
    # -------------------------

    if not _within_amount_tolerance(
        invoice.get("total_amount", 0),
        po.get("total_amount", 0)
    ):
        confidence *= 0.7
        return {
            "status": "FAIL",
            "reason": "AMOUNT_MISMATCH",
            "confidence": confidence
        }

    # -------------------------
    # SUCCESS
    # -------------------------

    return {
        "status": "PASS",
        "reason": "FULL_THREE_WAY_MATCH",
        "confidence": round(confidence, 2),
        "warnings": warnings
    }
