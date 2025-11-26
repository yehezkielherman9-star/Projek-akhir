import storage
from datetime import datetime

def now_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_id(item_id):
    return str(item_id)

# ==================================================
# Tambah Barang
# ==================================================
def add_item(name, price, stock=1):
    for item_id, item in storage.items.items():
        if item["name"].lower() == name.lower():
            item["stock"] = item.get("stock", 0) + stock
            storage.save_all()
            return item_id

    new_id = 1
    while str(new_id) in storage.items:
        new_id += 1

    storage.items[str(new_id)] = {
        "name": name,
        "price": price,
        "stock": stock
    }

    storage.save_all()
    refresh_items()
    return str(new_id)

# ==================================================
# Customer Membeli Barang
# ==================================================
def customer_buy_item(item_id, username):
    key = normalize_id(item_id)

    if key not in storage.items or storage.items[key]["stock"] <= 0:
        return False

    item = storage.items[key]
    item["stock"] -= 1

    storage.sales_history.append({
        "time": now_time(),
        "name": item["name"],
        "price": item["price"],
        "buyer": username,
        "seller": "Toko",
        "status": "Terjual"
    })

    if item["stock"] == 0:
        del storage.items[key]

    storage.save_all()
    return True

# ==================================================
# Customer Ajukan Jual Barang (Pending)
# ==================================================
def request_sell_item(owner, name, price, stock=1):

    for item_id, item in storage.sell_queue.items():
        if (
            item["name"].lower() == name.lower()
            and item["owner"] == owner
            and item["price"] == price
        ):
            item["stock"] += stock
            item["status"] = "Menunggu Konfirmasi"
            storage.save_all()
            return item_id

    new_id = 1
    while str(new_id) in storage.sell_queue:
        new_id += 1

    storage.sell_queue[str(new_id)] = {
        "name": name,
        "price": price,
        "owner": owner,
        "stock": stock,
        "status": "Menunggu Konfirmasi"
    }

    storage.save_all()
    refresh_sell_queue()
    return str(new_id)

# ==================================================
# ADMIN – Setujui Barang Customer
# ==================================================
def approve_buy_from_customer(item_id, quantity):
    key = normalize_id(item_id)

    if key not in storage.sell_queue:
        return False

    data = storage.sell_queue[key]
    available_stock = data["stock"]

    if quantity <= 0 or quantity > available_stock:
        return False

    add_item(data["name"], data["price"], stock=quantity)

    remaining = available_stock - quantity

    if remaining <= 0:
        storage.sell_queue.pop(key)
    else:
        storage.sell_queue[key]["stock"] = remaining
        storage.sell_queue[key]["status"] = "Menunggu Konfirmasi"

    # Tambahkan history diterima
    storage.sales_history.append({
        "time": now_time(),
        "name": data["name"],
        "quantity": quantity,
        "price": data["price"],
        "buyer": "Toko (Admin)",
        "seller": data["owner"],
        "status": "Diterima"
    })

    storage.save_all()
    refresh_sell_queue()
    refresh_sales_history()
    return True

# ==================================================
# ADMIN – Tolak Barang Customer
# ==================================================
def reject_sell_item(item_id):
    key = normalize_id(item_id)

    if key not in storage.sell_queue:
        return False

    data = storage.sell_queue[key]

    storage.sales_history.append({
        "time": now_time(),
        "name": data["name"],
        "stock": data["stock"],
        "price": data["price"],
        "buyer": "-",
        "seller": data["owner"],
        "status": "Ditolak"
    })

    storage.sell_queue.pop(key)

    storage.save_all()
    refresh_sell_queue()
    refresh_sales_history()
    return True

# ==================================================
# Refresh Item Toko
# ==================================================
def refresh_items():
    storage.items = dict(sorted(storage.items.items(), key=lambda x: int(x[0])))
    storage.save_all()

# ==================================================
# Refresh Sell Queue (Pending ID selalu urut)
# ==================================================
def refresh_sell_queue():
    new_dict = {}
    new_id = 1

    for old_id, data in sorted(storage.sell_queue.items(), key=lambda x: int(x[0])):
        new_dict[str(new_id)] = data
        new_id += 1

    storage.sell_queue = new_dict
    storage.save_all()

# ==================================================
# Refresh History (ID bagian Diterima & Ditolak selalu urut)
# ==================================================
def refresh_sales_history():
    new_list = []
    new_id = 1

    for h in storage.sales_history:
        if h.get("status") in ["Diterima", "Ditolak"]:
            h["id"] = str(new_id)
            new_id += 1
        new_list.append(h)

    storage.sales_history = new_list
    storage.save_all()
