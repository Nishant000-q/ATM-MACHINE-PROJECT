from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "customers.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def timestamp():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

# ── serve frontend ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    body = request.json
    user_id = body.get("id", "").strip()
    pin     = str(body.get("pin", "")).strip()

    data = load_data()

    if user_id in data and pin == str(data[user_id]["atm_pin"]):
        user = data[user_id]
        return jsonify({
            "success": True,
            "name":    user["name"],
            "balance": user["balance"]
        })
    return jsonify({"success": False, "message": "Invalid ID or PIN"}), 401


@app.route("/api/balance", methods=["POST"])
def balance():
    body    = request.json
    user_id = body.get("id", "").strip()
    data    = load_data()

    if user_id not in data:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({"success": True, "balance": data[user_id]["balance"]})


@app.route("/api/deposit", methods=["POST"])
def deposit():
    body    = request.json
    user_id = body.get("id", "").strip()
    amount  = body.get("amount", 0)
    data    = load_data()

    if user_id not in data:
        return jsonify({"success": False, "message": "User not found"}), 404
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"success": False, "message": "Invalid amount"}), 400

    data[user_id]["balance"] += amount

    txn = {"type": "Deposit", "amount": amount, "date": timestamp(),
           "balance_after": data[user_id]["balance"]}
    data[user_id].setdefault("transactions", []).append(txn)

    save_data(data)
    return jsonify({"success": True, "balance": data[user_id]["balance"]})


@app.route("/api/withdraw", methods=["POST"])
def withdraw():
    body    = request.json
    user_id = body.get("id", "").strip()
    amount  = body.get("amount", 0)
    data    = load_data()

    if user_id not in data:
        return jsonify({"success": False, "message": "User not found"}), 404
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"success": False, "message": "Invalid amount"}), 400
    if amount > data[user_id]["balance"]:
        return jsonify({"success": False, "message": "Insufficient balance"}), 400

    data[user_id]["balance"] -= amount

    txn = {"type": "Withdrawal", "amount": amount, "date": timestamp(),
           "balance_after": data[user_id]["balance"]}
    data[user_id].setdefault("transactions", []).append(txn)

    save_data(data)
    return jsonify({"success": True, "balance": data[user_id]["balance"]})


@app.route("/api/transfer", methods=["POST"])
def transfer():
    body       = request.json
    user_id    = body.get("id", "").strip()
    target_id  = body.get("target_id", "").strip()
    amount     = body.get("amount", 0)
    data       = load_data()

    if user_id not in data:
        return jsonify({"success": False, "message": "Sender not found"}), 404
    if target_id not in data:
        return jsonify({"success": False, "message": "Recipient account not found"}), 404
    if user_id == target_id:
        return jsonify({"success": False, "message": "Cannot transfer to yourself"}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"success": False, "message": "Invalid amount"}), 400
    if amount > data[user_id]["balance"]:
        return jsonify({"success": False, "message": "Insufficient balance"}), 400

    data[user_id]["balance"]  -= amount
    data[target_id]["balance"] += amount

    ts = timestamp()
    data[user_id].setdefault("transactions", []).append({
        "type": f"Transfer to {target_id}", "amount": amount, "date": ts,
        "balance_after": data[user_id]["balance"]
    })
    data[target_id].setdefault("transactions", []).append({
        "type": f"Transfer from {user_id}", "amount": amount, "date": ts,
        "balance_after": data[target_id]["balance"]
    })

    save_data(data)
    return jsonify({"success": True, "balance": data[user_id]["balance"],
                    "recipient_name": data[target_id]["name"]})


@app.route("/api/transactions", methods=["POST"])
def transactions():
    body    = request.json
    user_id = body.get("id", "").strip()
    data    = load_data()

    if user_id not in data:
        return jsonify({"success": False, "message": "User not found"}), 404

    txns = data[user_id].get("transactions", [])
    return jsonify({"success": True, "transactions": list(reversed(txns[-10:]))})


# ── run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
