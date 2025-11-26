from inquirer_ui import (
    menu, prompt, message, prompt_under_list,
    confirm_or_back, clear_terminal, make_table
)
import storage, items
from admin_menu import header


def customer_menu(username):
    while True:
        header("MENU PELANGGAN")

        pilih = menu(
            "Pilih opsi:",
            [
                "Lihat Barang Toko",
                "Beli Barang",
                "Jual Barang ke Toko",
                "Status Barang yang Dijual",
                "Logout",
            ]
        )

        # =========================================================
        # 0. LIHAT BARANG TOKO
        # =========================================================
        if pilih == 0:
            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            rows = [
                [i, d["name"], f"Rp{d['price']}", d.get("stock", 0)]
                for i, d in storage.items.items()
            ]

            table_text = make_table(
                ["ID", "Nama", "Harga", "Stok"], rows
            )
            message(table_text)

        # =========================================================
        # 1. BELI BARANG
        # =========================================================
        elif pilih == 1:
            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            # tampilkan tabel
            rows = [
                [i, d["name"], f"Rp{d['price']}", d.get("stock", 0)]
                for i, d in storage.items.items()
            ]
            table_text = make_table(["ID", "Nama", "Harga", "Stok"], rows)
            
            # buat list untuk selection
            list_text = "\n".join([
                f"{i}. {d['name']} - Rp{d['price']} | Stok: {d.get('stock', 0)}"
                for i, d in storage.items.items()
            ])

            inp = prompt_under_list(list_text, "Pilih ID barang yang ingin dibeli:")
            if inp is None:
                continue

            item_id = str(inp).strip()
            if item_id not in storage.items:
                message("Barang tidak ditemukan.")
                continue

            item = storage.items[item_id]
            jumlah_input = prompt(f"Jumlah pembelian (tersedia {item.get('stock', 0)}): ").strip()
            if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
                message("Jumlah tidak valid.")
                continue

            jumlah = int(jumlah_input)

            if confirm_or_back(
                f"Beli {jumlah}x '{item['name']}' (Rp{item['price']} per item)?"
            ) is None:
                continue

            success_count = 0
            for _ in range(jumlah):
                if items.customer_buy_item(item_id, username):
                    success_count += 1

            message(f"Pembelian berhasil: {success_count} dari {jumlah}")

        # =========================================================
        # 2. JUAL BARANG KE TOKO
        # =========================================================
        elif pilih == 2:
            name = prompt("Nama barang: ").strip()
            if not name:
                message("Nama tidak boleh kosong.")
                continue

            price_input = prompt("Harga penawaran: ").strip()
            if not price_input.isdigit():
                message("Harga tidak valid.")
                continue

            price = int(price_input)

            jumlah_input = prompt("Jumlah barang: ").strip()
            if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
                message("Jumlah tidak valid.")
                continue

            jumlah = int(jumlah_input)

            if confirm_or_back(
                f"Ajukan {jumlah}x '{name}' dengan harga Rp{price}?"
            ) is None:
                continue

            # cek apakah user sudah punya item serupa
            existing_id = None
            for item_id, data in storage.sell_queue.items():
                if data["name"].lower() == name.lower() and data["owner"] == username:
                    existing_id = item_id
                    break

            if existing_id:
                storage.sell_queue[existing_id]["stock"] += jumlah
                storage.save_all()

                message(
                    f"Stok barang diperbarui!\n"
                    f"ID: {existing_id}\n"
                    f"Nama: {name}\n"
                    f"Stok sekarang: {storage.sell_queue[existing_id]['stock']}"
                )
            else:
                new_id = items.request_sell_item(username, name, price, stock=jumlah)
                message(
                    f"Pengajuan berhasil!\n"
                    f"Nama: {name}\n"
                    f"ID Baru: {new_id}\n"
                    f"Stok: {jumlah}"
                )

        # =========================================================
        # 3. STATUS BARANG YANG DIJUAL
        # =========================================================
        elif pilih == 3:
            pending = [
                (i, d) for i, d in storage.sell_queue.items()
                if d["owner"] == username
            ]

            history = [
                h for h in storage.sell_history
                if h["owner"] == username
            ]

            if not pending and not history:
                message("Tidak ada barang milik Anda.")
                continue

            # Pending
            if pending:
                rows_pending = [
                    [
                        i, d["name"], f"Rp{d['price']}",
                        d.get("stock", 1),
                        d.get("status", "Menunggu")
                    ]
                    for i, d in pending
                ]
                message(make_table(
                    ["ID", "Nama", "Harga", "Stok", "Status"], rows_pending
                ))

            # History
            if history:
                rows_history = [
                    [
                        h["id"], h["name"], h["stock"],
                        h["status"], f"Rp{h.get('final_price', '-')}"
                    ]
                    for h in history
                ]
                message(make_table(
                    ["ID", "Nama", "Stok", "Status", "Harga Akhir"], rows_history
                ))

        # =========================================================
        # 4. LOGOUT
        # =========================================================
        else:
            break
