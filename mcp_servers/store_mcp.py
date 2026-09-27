# mcp_servers/store_mcp.py
from mcp.server.fastmcp import FastMCP
import json
import os
from datetime import datetime, timezone

# Initialize FastMCP Server
mcp = FastMCP("EcommerceOperationsServer")

# In-memory customer CRM records
CUSTOMER_DATABASE = {
    "CUST-101": {
        "name": "Sarah Jenkins",
        "vip_tier": "Platinum",
        "lifetime_spend": 4850.00,
        "account_age_days": 420,
        "past_chargebacks": 0
    },
    "CUST-202": {
        "name": "Michael Chang",
        "vip_tier": "Standard",
        "lifetime_spend": 65.00,
        "account_age_days": 12,
        "past_chargebacks": 2
    }
}

# In-memory warehouse inventory/order stages
ORDER_DATABASE = {
    "ORD-9901": {
        "fulfillment_stage": "HELD_FOR_RISK_REVIEW",
        "payment_status": "AUTHORIZED_PENDING_APPROVAL",
        "warehouse_zone": "Hub-NorthEast"
    }
}

@mcp.tool()
def get_customer_crm_profile(customer_id: str) -> str:
    """Fetches customer loyalty tier, lifetime value, and dispute history by customer ID."""
    cust = CUSTOMER_DATABASE.get(customer_id.strip().upper())
    if not cust:
        return f"Customer ID '{customer_id}' not found in CRM."
    return (
        f"Customer: {cust['name']} | "
        f"Tier: {cust['vip_tier']} | "
        f"Lifetime Spend: ${cust['lifetime_spend']:.2f} | "
        f"Account Age: {cust['account_age_days']} days | "
        f"Prior Chargebacks: {cust['past_chargebacks']}"
    )

@mcp.tool()
def check_order_fulfillment(order_id: str) -> str:
    """Checks the warehouse staging and payment authorization state for a specific order."""
    order = ORDER_DATABASE.get(order_id.strip().upper())
    if not order:
        return f"Order ID '{order_id}' not found in warehouse registry."
    return (
        f"Order: {order_id} | "
        f"Fulfillment Stage: {order['fulfillment_stage']} | "
        f"Payment Status: {order['payment_status']} | "
        f"Zone: {order['warehouse_zone']}"
    )

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "audit_trail.jsonl")

@mcp.tool()
def record_audit_event(
    order_id: str,
    risk_score: float,
    classification: str,
    vip_tier: str,
    final_action: str,
    reason: str
) -> str:
    """Appends an operational audit record cleanly to the JSONL log file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": order_id,
        "subagent_1_risk_evaluation": {
            "risk_score": risk_score,
            "classification": classification
        },
        "subagent_2_resolution": {
            "vip_tier": vip_tier,
            "final_action": final_action,
            "reason": reason
        }
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return f"Audit event recorded for {order_id} with action: {final_action}"

if __name__ == "__main__":
    mcp.run()