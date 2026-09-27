# utils/logger.py
import json
import os
from datetime import datetime, timezone

LOG_FILE = "logs/audit_trail.jsonl"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def append_audit_log(order_id: str, supervisor_data: dict, subagent_1_data: dict, subagent_2_data: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": order_id,
        "supervisor": supervisor_data,
        "subagent_1_risk_evaluation": subagent_1_data,
        "subagent_2_resolution": subagent_2_data
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")