import os
import json
from datetime import datetime

DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

def log_debug(doc_type: str, step: str, payload):
    """
    doc_type: invoice | po | grn | unknown
    step: parsed_json | gemini_raw_output | non_json_response | etc
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_step = step.replace("/", "_")
    filename = f"{doc_type}_{ts}_{safe_step}.log"

    path = os.path.join(DEBUG_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        if isinstance(payload, (dict, list)):
            json.dump(payload, f, indent=2)
        else:
            f.write(str(payload))
