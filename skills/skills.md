# Operational Skills & Runbook Matrix

## Subagent 1: Risk Assessment Heuristics
Analyze raw order metrics and calculate a risk score from 0.00 to 1.00:
- **Base Score**: 0.10
- **Add 0.35** if `Shipping/Billing Match == No`.
- **Add 0.25** if `VPN Detected == Yes`.
- **Add 0.10 per failed payment attempt** within the last 24 hours.
- **Add 0.20** if `Order Amount > $500.00`.

### Score Thresholds
- **Score < 0.35**: `LEGITIMATE`
- **Score 0.35 - 0.69**: `MANUAL_REVIEW`
- **Score >= 0.70**: `HIGH_RISK_FRAUD`

---

## Subagent 2: Resolution Policies & Action Matrix

### Baseline Actions
1. **`LEGITIMATE`**:
   - Action: `AUTO_APPROVE`
   - Directive: Instruct fulfillment warehouse to release hold.
2. **`MANUAL_REVIEW`**:
   - Action: `HOLD_AND_VERIFY`
   - Directive: Dispatch step-up authentication challenge (SMS OTP).
3. **`HIGH_RISK_FRAUD`**:
   - Action: `CANCEL_AND_FLAG`
   - Directive: Cancel order, void authorization, and flag token.

### Guardrail Override Clause
- If the baseline action is `CANCEL_AND_FLAG`, check the customer's CRM tier via MCP:
  - If tier is **`Gold`** or **`Platinum`**: Override action to **`ESCALATE_TO_SENIOR_ANALYST`**.
  - Auto-cancellation is strictly forbidden for high-tier accounts.