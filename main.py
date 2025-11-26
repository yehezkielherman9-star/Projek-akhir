import os
from auth import login, register
from admin_menu import admin_menu
from customer_menu import customer_menu
from inquirer_ui import menu, prompt, message, clear_terminal

def header(text):
    clear_terminal()
    garis = "═" * (len(text) + 6)
    print(f"╔{garis}╗")
    print(f"║   {text}   ║")
    print(f"╚{garis}╝")
    
def main():
    while True:
        header("SELAMAT DATANG DI TOKO BARANG ANTIK")

        choice_idx = menu("Pilih opsi:", ["Login", "Register", "Logout"])
        
        if choice_idx == 0:
            header("LOGIN")
            username = prompt("Username:")
            password = prompt("Password:")

            success, msg_or_role = login(username, password)

            if not success:
                message(msg_or_role)
                continue

            message("Login berhasil!")
            
            if msg_or_role == "ADMIN":
                admin_menu()
            else:
                customer_menu(username)


        elif choice_idx == 1:
            header("REGISTER")
            username = prompt("Username baru:")
            password = prompt("Password baru:")

            success, msg = register(username, password)
            if success:
                message("Registrasi berhasil, Silahkan login.")

            else:
                message(msg)

        else:  
            header("Terima kasih telah berkunjung.")
            break

if __name__ == "__main__":
    main()