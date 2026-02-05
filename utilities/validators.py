def validate_extracted_json(data: dict, doc_type: str):
    if not isinstance(data, dict):
        raise ValueError(f"{doc_type}: Extracted data is not a dict")

    if doc_type == "invoice":
        _require_fields(data, [
            "invoice_number",
            "po_number",
            "total_amount",
            "line_items"
        ])
        _validate_line_items(data["line_items"], qty_key="quantity")

    elif doc_type == "po":
        _require_fields(data, [
            "po_number",
            "total_amount",
            "items"
        ])
        _validate_line_items(data["items"], qty_key="quantity")

    elif doc_type == "grn":
        _require_fields(data, [
            "po_number",
            "items"
        ])
        _validate_line_items(data["items"], qty_key="received_quantity")

    else:
        raise ValueError(f"Unknown doc_type: {doc_type}")


# --------------------
# Helpers
# --------------------

def _require_fields(data: dict, fields: list):
    for field in fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")


def _validate_line_items(items: list, qty_key: str):
    if not isinstance(items, list) or not items:
        raise ValueError("Line items must be a non-empty list")

    for item in items:
        if "description" not in item:
            raise ValueError("Line item missing description")

        if qty_key not in item:
            raise ValueError(f"Line item missing {qty_key}")

        if not isinstance(item[qty_key], (int, float)):
            raise ValueError(f"{qty_key} must be numeric")

        if item[qty_key] < 0:
            raise ValueError(f"{qty_key} cannot be negative")
