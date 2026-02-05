# Amount difference allowed between Invoice and PO (percentage)
AMOUNT_TOLERANCE_PERCENT = 0.0
# Example:
# 0.0  → exact match
# 2.0  → allow ±2% difference


# Quantity rules
ALLOW_PARTIAL_GRN = False
# False → GRN qty must be >= PO qty (your SamTell case)
# True  → allow partial receipt (future use)


# Header matching behavior
VENDOR_MATCH_STRICT = False
# False → vendor mismatch = warning
# True  → vendor mismatch = hard FAIL


# Description matching behavior
USE_AI_NORMALIZATION = True
# True  → semantic match via LLM (Broadridge vs Broadridge India)
# False → exact string match only


# Safety limits
MAX_LINE_ITEMS = 200
# Prevents garbage / OCR hallucination from blowing up matching
