from flask import Flask, request, jsonify, render_template
from pathlib import Path
from datetime import datetime, timezone
import json
import secrets
import time

app = Flask(__name__)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Simple in-memory rate limit for PIN lookups.
LOOKUP_LOG = {}
MAX_ATTEMPTS = 10
WINDOW_SECONDS = 60

def client_key():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()

def allowed_lookup(key):
    now = time.time()
    attempts = [t for t in LOOKUP_LOG.get(key, []) if now - t < WINDOW_SECONDS]
    if len(attempts) >= MAX_ATTEMPTS:
        LOOKUP_LOG[key] = attempts
        return False
    attempts.append(now)
    LOOKUP_LOG[key] = attempts
    return True

def generate_pin():
    for _ in range(20):
        pin = f"{secrets.randbelow(1_000_000):06d}"
        if not (REPORTS_DIR / f"{pin}.json").exists():
            return pin
    raise RuntimeError("Não foi possível gerar um PIN disponível.")

@app.get("/")
def dashboard():
    return render_template("dashboard.html")

@app.post("/api/submit")
def submit_report():
    if not request.is_json:
        return jsonify({"error": "JSON esperado"}), 400

    report = request.get_json(silent=True)
    if not isinstance(report, dict):
        return jsonify({"error": "Relatório inválido"}), 400

    # The scanner sends only audit information after user consent.
    pin = generate_pin()

    report["_server_received_at"] = datetime.now(timezone.utc).isoformat()
    report["_pin"] = pin

    (REPORTS_DIR / f"{pin}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return jsonify({"ok": True, "pin": pin})

@app.get("/api/result/<pin>")
def get_result(pin):
    if not (len(pin) == 6 and pin.isdigit()):
        return jsonify({"error": "PIN inválido"}), 400

    key = f"{client_key()}:{pin}"
    if not allowed_lookup(key):
        return jsonify({"error": "Muitas tentativas. Aguarde um minuto."}), 429

    path = REPORTS_DIR / f"{pin}.json"
    if not path.exists():
        return jsonify({"error": "Relatório não encontrado"}), 404

    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return jsonify({"error": "Relatório corrompido"}), 500

    return jsonify(report)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
