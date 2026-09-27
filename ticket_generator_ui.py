# ticket_generator_ui.py
import json
import os
import random
import threading
import time
import webbrowser
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Fraud Ticket Generator")

# Absolute path resolution locked to project root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER_FILE = os.path.join(BASE_DIR, "testcases", "incoming_order.txt")
LOG_FILE = os.path.join(BASE_DIR, "logs", "audit_trail.jsonl")

# Ensure target directories exist
os.makedirs(os.path.dirname(ORDER_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

CUSTOMERS = [
    {"id": "CUST-101", "name": "Sarah Jenkins", "tier": "Platinum"},  # VIP
    {"id": "CUST-202", "name": "Michael Chang", "tier": "Standard"},  # Standard
    {"id": "CUST-303", "name": "David Ross", "tier": "Standard"}      # Guest/New
]

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fraud Swarm Ticket Simulator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; padding: 24px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }
        h1 { font-size: 1.4rem; color: #38bdf8; }
        .btn { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.95rem; transition: background 0.2s; }
        .btn:hover { background: #1d4ed8; }
        .grid { display: grid; grid-template-columns: 1fr 1.6fr; gap: 20px; }
        .panel { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px; }
        h2 { font-size: 1.05rem; margin-bottom: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        pre { background: #090d16; padding: 14px; border-radius: 6px; color: #a5f3fc; font-size: 0.85rem; line-height: 1.5; height: 350px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; border: 1px solid #1e293b; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 0.85rem; }
        th { background: #090d16; color: #94a3b8; font-weight: 600; }
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; display: inline-block; }
        .badge-danger { background: #7f1d1d; color: #fca5a5; }
        .badge-warning { background: #78350f; color: #fde68a; }
        .badge-success { background: #14532d; color: #86efac; }
        .badge-vip { background: #581c87; color: #e9d5ff; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1>Autonomous Fraud Swarm Event Simulator</h1>
            <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">Writes to <code>test_cases/incoming_order.txt</code> &bull; Grok Swarm evaluates and records to <code>logs/audit_trail.jsonl</code></p>
        </div>
        <button class="btn" onclick="generateTicket()">+ Generate Random Flagged Ticket</button>
    </header>

    <div class="grid">
        <div class="panel">
            <h2>Current Active Ticket (Saved to File)</h2>
            <pre id="ticket-view">No ticket generated yet. Click the button above to generate one.</pre>
        </div>

        <div class="panel">
            <h2>Live Audit Trail (logs/audit_trail.jsonl)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Order</th>
                        <th>Risk Assessment</th>
                        <th>VIP Tier</th>
                        <th>Final Directive</th>
                    </tr>
                </thead>
                <tbody id="logs-body">
                    <tr><td colspan="5" style="text-align: center; color: #64748b; padding: 20px;">No audit records found yet.</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    async function generateTicket() {
        const btn = document.querySelector('.btn');
        btn.innerText = "Writing to disk...";
        btn.disabled = true;
        try {
            const res = await fetch('/api/generate-ticket', { method: 'POST' });
            const data = await res.json();
            document.getElementById('ticket-view').innerText = data.content;
        } catch (err) {
            console.error(err);
        } finally {
            btn.innerText = "+ Generate Random Flagged Ticket";
            btn.disabled = false;
        }
    }

    async function refreshLogs() {
        try {
            const res = await fetch('/api/get-audit-logs');
            const records = await res.json();
            if (!records || records.length === 0) return;

            const tbody = document.getElementById('logs-body');
            tbody.innerHTML = '';

            records.slice(-10).reverse().forEach(entry => {
                const sub1 = entry.subagent_1_risk_evaluation || {};
                const sub2 = entry.subagent_2_resolution || {};
                const action = sub2.final_action || 'UNKNOWN';

                let badgeClass = 'badge-warning';
                if (action.includes('CANCEL')) badgeClass = 'badge-danger';
                if (action.includes('ESCALATE')) badgeClass = 'badge-vip';
                if (action.includes('APPROVE')) badgeClass = 'badge-success';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="color: #94a3b8;">${entry.timestamp ? entry.timestamp.split('T')[1].slice(0,8) : ''}</td>
                    <td><strong>${entry.order_id || 'N/A'}</strong></td>
                    <td><span class="badge ${sub1.classification === 'HIGH_RISK_FRAUD' ? 'badge-danger' : 'badge-warning'}">${sub1.risk_score !== undefined ? sub1.risk_score : ''} ${sub1.classification || ''}</span></td>
                    <td><span class="badge ${sub2.vip_tier === 'Platinum' ? 'badge-vip' : ''}">${sub2.vip_tier || 'Standard'}</span></td>
                    <td><span class="badge ${badgeClass}">${action}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (e) {
            console.error(e);
        }
    }

    setInterval(refreshLogs, 1500);
    refreshLogs();
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT

@app.post("/api/generate-ticket")
def generate_ticket():
    order_id = f"ORD-{random.randint(9000, 9999)}"
    cust = random.choice(CUSTOMERS)
    amount = round(random.uniform(90.0, 980.0), 2)
    mismatch = random.choice(["No", "No", "Yes"])
    vpn = random.choice(["Yes", "No"])
    failed_attempts = random.choice([0, 1, 2, 3])

    card_num = f"4128-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    email = f"{cust['name'].lower().replace(' ', '.')}@secure-corp-mail.com"

    ticket_body = f"""ALERT: TRANSACTION FLAGGED BY GATEWAY
Order ID: {order_id}
Customer ID: {cust['id']}
Amount: ${amount:.2f}
Customer Contact: {email}
Payment Card: {card_num}
Shipping Address: {random.randint(100, 999)} Market Street, San Francisco, CA
Billing Address: {random.randint(100, 999)} Fifth Avenue, New York, NY
Shipping/Billing Match: {mismatch}
VPN Detected: {vpn}
Failed Payment Attempts (Past 24h): {failed_attempts}
Flagged Timestamp: {datetime.now(timezone.utc).isoformat()}
"""

    # Direct atomic write and hardware flush to ensure immediate availability
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        f.write(ticket_body)
        f.flush()
        os.fsync(f.fileno())

    print(f"\n[+] SUCCESS: Written to disk -> {order_id}")
    print(f"    Path: {ORDER_FILE}\n")

    return {"status": "ok", "order_id": order_id, "content": ticket_body}

@app.get("/api/get-audit-logs")
def get_audit_logs():
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return logs

def open_browser():
    time.sleep(1.2)
    print("[+] Launching web browser at http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("\n=======================================================")
    print("  STARTING FRAUD TRIAGE SIMULATOR UI")
    print(f"  Target File: {ORDER_FILE}")
    print(f"  Audit Trail: {LOG_FILE}")
    print("  Local URL:   http://127.0.0.1:8000")
    print("=======================================================\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")