from inquirer_ui import (
    menu, prompt, message, prompt_under_list,
    confirm_or_back, clear_terminal, make_table
)
import storage, items


def header(text):
    clear_terminal()
    garis = "═" * (len(text) + 6)
    print(f"╔{garis}╗")
    print(f"║   {text}   ║")
    print(f"╚{garis}╝")


def admin_menu():
    while True:
        header("MENU ADMIN")

        pilih = menu("Pilih opsi:", [
            "Tambah Barang",
            "Ubah Barang",
            "List Barang Toko",
            "Konfirmasi barang yang Dijual Pelanggan",
            "History",
            "Logout"
        ])

        # =========================================================
        # 0. TAMBAH BARANG
        # =========================================================
        if pilih == 0:
            header("TAMBAH BARANG")

            name = prompt("Nama barang:").strip()
            if not name:
                message("Nama tidak boleh kosong.")
                continue

            price_input = prompt("Harga barang:").strip()
            try:
                price = int(price_input)
                if price <= 0:
                    message("Harga harus lebih dari 0.")
                    continue
            except ValueError:
                message("Harga tidak valid.")
                continue

            stock_input = prompt("Jumlah stok:").strip()
            if not stock_input.isdigit() or int(stock_input) <= 0:
                message("Jumlah stok harus lebih dari 0.")
                continue
            stock = int(stock_input)

            if confirm_or_back(
                f"Tambah '{name}' harga Rp{price} stok {stock}?"
            ) is None:
                continue

            new_id = items.add_item(name, price, stock)
            message(
                f"Barang berhasil ditambahkan!\n"
                f"ID: {new_id}\nNama: {name}\nHarga: Rp{price}\nStok: {stock}"
            )

        # =========================================================
        # 1. UBAH BARANG
        # =========================================================
        elif pilih == 1:
            header("UBAH BARANG")

            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            list_text = items.format_item_list(storage.items)
            inp = prompt_under_list(list_text, "Pilih barang yang diubah:")
            if inp is None:
                continue

            item_id = str(inp)
            if item_id not in storage.items:
                message("Barang tidak ditemukan.")
                continue
            
            item = storage.items[item_id]

            rows = [
                [item_id, item["name"], f"Rp{item['price']}", item.get("stock", 0)]
            ]

            message(make_table(
                ["ID", "Nama", "Harga", "Stok"],
                rows
            ))

            new_name = prompt("Nama baru (enter jika tidak):").strip()
            new_price_input = prompt("Harga baru (enter jika tidak):").strip()
            new_stock_input = prompt("Stok baru (enter jika tidak):").strip()

            new_price = None
            new_stock = None

            if new_price_input:
                try:
                    new_price = int(new_price_input)
                    if new_price <= 0:
                        message("Harga harus lebih dari 0.")
                        continue
                except ValueError:
                    message("Harga tidak valid.")
                    continue

            if new_stock_input:
                if not new_stock_input.isdigit() or int(new_stock_input) < 0:
                    message("Stok tidak valid!")
                    continue
                new_stock = int(new_stock_input)

            if confirm_or_back(
                f"Simpan perubahan untuk '{item['name']}'?"
            ) is None:
                continue

            if new_name:
                storage.items[item_id]["name"] = new_name
            if new_price is not None:
                storage.items[item_id]["price"] = new_price
            if new_stock is not None:
                storage.items[item_id]["stock"] = new_stock

            storage.save_all()
            message("Barang berhasil diperbarui.")

        # =========================================================
        # 2. LIST BARANG TOKO
        # =========================================================
        elif pilih == 2:
            header("LIST BARANG TOKO")

            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            rows = [
                [iid, v["name"], f"Rp{v['price']}", v.get("stock", 0)]
                for iid, v in storage.items.items()
            ]
            message(make_table(["ID", "Nama", "Harga", "Stok"], rows))

        # =========================================================
        # 3. KONFIRMASI PENJUALAN CUSTOMER
        # =========================================================
        elif pilih == 3:
            header("KONFIRMASI PENJUALAN PELANGGAN")

            if not storage.sell_queue:
                message("Tidak ada barang menunggu.")
                continue

            rows = [
                [iid, d["name"], f"Rp{d['price']}", d["stock"], d["owner"]]
                for iid, d in storage.sell_queue.items()
            ]
            message(make_table(
                ["ID", "Nama", "Harga", "Stok", "Pemilik"], rows
            ))

            list_text = "\n".join([
                f"{i}. {d['name']} - Rp{d['price']} | {d['owner']}"
                for i, d in storage.sell_queue.items()
            ])

            inp = prompt_under_list(list_text, "ID diproses:")
            if inp not in storage.sell_queue:
                message("ID tidak ditemukan.")
                continue

            aksi = menu("Aksi:", ["Setujui", "Tolak", "Batal"])

            # ===== SETUJUI =====
            if aksi == 0:
                max_stock = storage.sell_queue[inp].get("stock", 1)
                jumlah_input = prompt(
                    f"Jumlah disetujui (maks {max_stock}): "
                )

                if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
                    message("Jumlah tidak valid!")
                    continue

                jumlah = int(jumlah_input)

                success = items.approve_buy_from_customer(inp, jumlah)
                items.refresh_sell_queue()
                items.refresh_sales_history()

                if success:
                    message(f"Disetujui! {jumlah} item masuk ke toko")
                else:
                    message("Gagal menyetujui barang.")

            # ===== TOLAK =====
            elif aksi == 1:
                success = items.reject_sell_item(inp)
                items.refresh_sell_queue()
                items.refresh_sales_history()

                if success:
                    message("Barang ditolak.")
                else:
                    message("Gagal menolak barang.")

        # =========================================================
        # 4. HISTORY ADMIN
        # =========================================================
        elif pilih == 4:
            header("HISTORY TRANSAKSI")

            items.refresh_sales_history()

            if not storage.sales_history:
                message("Belum ada history.")
                continue

            rows = [
                [
                    h["time"],
                    f"{h['name']} x{h.get('quantity', h.get('stock', 1))}",
                    f"Rp{h['price']}",
                    f"{h['buyer']} <-- {h['seller']}",
                    h.get("status", "-")
                ]
                for h in storage.sales_history
            ]

            message(make_table(
                ["Waktu", "Barang", "Harga", "Transaksi", "Status"], rows
            ))

        else:
            break
