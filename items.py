import storage
from datetime import datetime

def now_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_id(item_id):
    return str(item_id)

# ==================================================
# Tambah Barang / Add Item (dengan stok)
# ==================================================
def add_item(name, price, stock=1):
    # Jika barang sudah ada di toko, update stok
    for item_id, item in storage.items.items():
        if item["name"].lower() == name.lower():
            item["stock"] = item.get("stock", 0) + stock
            storage.save_all()
            return item_id

    # Cari ID numerik terkecil yang belum digunakan
    new_id = 1
    while str(new_id) in storage.items:
        new_id += 1

    storage.items[str(new_id)] = {
        "name": name,
        "price": price,
        "stock": stock
    }
    storage.save_all()
    return str(new_id)

# ==================================================
# Hapus Barang
# ==================================================
def delete_item(item_id):
    key = normalize_id(item_id)
    if key not in storage.items:
        return None
    deleted = storage.items.pop(key)
    storage.save_all()
    return deleted

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
        "seller": "Toko"
    })  

    if item["stock"] == 0:
        del storage.items[key]

    storage.save_all()
    return True

# ==================================================
# Customer Mengajukan Barang untuk Dijual
# ==================================================
def request_sell_item(owner, name, price, stock=1):
    for item_id, item in storage.sell_queue.items():
        if (
            item["name"].lower() == name.lower()
            and item["owner"] == owner
            and item["price"] == price
        ):
            item["stock"] += stock
            storage.save_all()
            return item_id
    # Cari ID numerik terkecil yang belum digunakan
    new_id = 1
    while str(new_id) in storage.sell_queue:
        new_id += 1

    storage.sell_queue[str(new_id)] = {
        "name": name,
        "price": price,
        "owner": owner,
        "stock": stock,
        "status": "Menunggu konfirmasi"
    }
    storage.save_all()
    return str(new_id)

# ==================================================
# Approve Barang dari Customer
# ==================================================
def approve_buy_from_customer(item_id, quantity):
    key = normalize_id(item_id)

    if key not in storage.sell_queue:
        return False

    data = storage.sell_queue[key]
    available_stock = data.get("stock", 1)

    # Validate quantity
    if quantity <= 0 or quantity > available_stock:
        return False

    # Add item to shop inventory using the offered price
    new_id = add_item(data["name"], data["price"], stock=quantity)

    # Update remaining stock in queue or remove if fully approved
    remaining = available_stock - quantity
    if remaining <= 0:
        storage.sell_queue.pop(key)
    else:
        storage.sell_queue[key]["stock"] = remaining

    # Record transaction in sales history
    storage.sales_history.append({
        "time": now_time(),
        "name": data["name"],
        "price": data["price"],
        "buyer": "Toko (Admin)",
        "seller": data["owner"],
        "quantity": quantity,
        "status": "Diterima"
    })

    storage.save_all()
    return True

def reject_sell_item(item_id):
    key = normalize_id(item_id)
    if item_id not in storage.sell_queue:
        return False

    storage.sell_queue.pop(item_id)
    storage.save_all()
    return True
# ==================================================
# List Semua Barang (urut ID)
# ==================================================
def format_items_list(items_dict):
    lines = []
    for item_id in sorted(items_dict, key=lambda x: int(x)):
        item = items_dict[item_id]
        lines.append(f"{item_id}. {item['name']} - Rp{item['price']} | Stok: {item.get('stock',0)}")
    return "\n".join(lines)


