import json
import os

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# DATA GLOBAL
# =========================
users = load_json("users.json", {
    "ADMIN": {"password": "admin123", "role": "ADMIN"}
})
items = load_json("items.json", {})
sell_queue = load_json("sell_queue.json", {})
sales_history = load_json("sales_history.json", [])



def save_all():
    save_json("users.json", users)
    save_json("items.json", items)
    save_json("sell_queue.json", sell_queue)
    save_json("sales_history.json", sales_history)