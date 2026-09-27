# guardrails/safety.py
import re

class SwarmGuardrails:
    CARD_PATTERN = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    @classmethod
    def mask_pii(cls, text: str) -> str:
        text = re.sub(cls.CARD_PATTERN, "[CONFIDENTIAL_CARD_REDACTED]", text)
        text = re.sub(cls.EMAIL_PATTERN, "[CONFIDENTIAL_EMAIL_REDACTED]", text)
        return text

    @classmethod
    def evaluate_vip_safety(cls, vip_tier: str, preliminary_action: str) -> dict:
        tier_clean = vip_tier.strip().upper()
        if tier_clean in ["PLATINUM", "GOLD"] and preliminary_action == "CANCEL_AND_FLAG":
            return {
                "override_triggered": True,
                "final_action": "ESCALATE_TO_SENIOR_ANALYST",
                "guardrail_log": f"Active safety block: Auto-cancellation prohibited for {tier_clean} VIP account."
            }
        return {
            "override_triggered": False,
            "final_action": preliminary_action,
            "guardrail_log": "Standard business rules applied."
        }