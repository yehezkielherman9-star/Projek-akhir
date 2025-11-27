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
                "List Barang Toko",
                "Beli Barang",
                "Jual Barang ke Toko",
                "Status Barang yang Dijual",
                "Logout",
            ]
        )

        
        # 0. lihat barang di toko
       
        if pilih == 0:
            print()
            header("List Barang Di Toko")

            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            rows = [
                [item_id, d["name"], f"Rp{d['price']}", d.get("stock", 0)]
                for item_id, d in storage.items.items()
            ]

            message(make_table(
                ["ID", "Nama", "Harga", "Stok"],
                rows
            ))

        
        # 1. beli barang
        elif pilih == 1:
            print()
            header("Beli Barang")

            if not storage.items:
                message("Belum ada barang di toko.")
                continue

            # TABEL barang di toko
            rows = [
                [item_id, d["name"], f"Rp{d['price']}", d.get("stock", 0)]
                for item_id, d in storage.items.items()
            ]
            message(make_table(["ID", "Nama", "Harga", "Stok"], rows))

            # list pilihan
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

            jumlah_input = prompt(
                f"Jumlah pembelian (tersedia {item.get('stock', 0)}): "
            ).strip()

            if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
                message("Jumlah tidak valid.")
                continue

            jumlah = int(jumlah_input)

            if jumlah > item.get("stock", 0):
                message(f"Jumlah melebihi stok tersedia ({item.get('stock', 0)}).")
                continue
            
            if confirm_or_back(
                f"Beli {jumlah}x '{item['name']}' (Rp{item['price']} per item)?"
            ) is None:
                continue

            success_count = sum(
                1 for _ in range(jumlah)
                if items.customer_buy_item(item_id, username)
            )

            message(f"Pembelian berhasil: {success_count} dari {jumlah}")

        
        # 2. jual barang ke toko
        elif pilih == 2:
            print()
            header("Jual Barang Ke Toko")

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

            existing_id = None
            for item_id, data in storage.sell_queue.items():
                if (
                    data["name"].lower() == name.lower()
                    and data["owner"] == username
                ):
                    existing_id = item_id
                    break

            if existing_id:
                storage.sell_queue[existing_id]["stock"] += jumlah
                storage.sell_queue[existing_id]["status"] = "Menunggu Konfirmasi"
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
                    f"ID Baru: {new_id}\n"
                    f"Nama: {name}\n"
                    f"Stok: {jumlah}"
                )

        
        # 3. status barang dijual
        elif pilih == 3:
            print()
            header("Status Barang Yang Anda Jual")

            pending = []
            diterima = []
            ditolak = []

            # data barang yang dijual
            for item_id, d in storage.sell_queue.items():
                if d["owner"] == username:
                    pending.append((item_id, d))

            # DATA DITERIMA & DITOLAK
            for h in storage.sales_history:
                if h.get("seller") != username:
                    continue

                if h.get("status") == "Diterima":
                    diterima.append(h)
                elif h.get("status") == "Ditolak":
                    ditolak.append(h)

            # Jika semuanya kosong
            if not pending and not diterima and not ditolak:
                message("Tidak ada barang milik Anda.")
                continue

            # TABEL 1 — Menunggu konfirmasi
            if pending:
                print()
                header("MENUNGGU KONFIRMASI ADMIN")

                rows_pending = [
                    [
                        item_id,
                        d["name"],
                        f"Rp{d['price']}",
                        d.get("stock", 1),
                        "Menunggu konfirmasi"
                    ]
                    for item_id, d in pending
                ]

                message(make_table(
                    ["ID", "Nama", "Harga", "Stok", "Status"],
                    rows_pending
                ))

            # TABEL 2 — Diterima
            if diterima:
                print()
                header("BARANG DISETUJUI ADMIN")

                rows_diterima = [
                    [
                        h.get("name", "-"),
                        h.get("quantity", h.get("stock", 1)),
                        "Diterima",
                        f"Rp{h.get('price', '-')}"
                    ]
                    for h in diterima
                ]

                message(make_table(
                    ["Nama", "Jumlah", "Status", "Harga Akhir"],
                    rows_diterima
                ))

            # TABEL 3 — ditolak
            if ditolak:
                print()
                header("BARANG DITOLAK ADMIN")

                rows_ditolak = [
                    [
                        h.get("name", "-"),
                        h.get("quantity", h.get("stock", 1)),
                        "Ditolak",
                        f"Rp{h.get('price', '-')}"
                    ]
                    for h in ditolak
                ]

                message(make_table(
                    ["Nama", "Jumlah", "Status", "Harga Akhir"],
                    rows_ditolak
                ))

        # 4. logout       
        else:
            break
