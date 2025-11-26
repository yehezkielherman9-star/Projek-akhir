import storage

def register(username, password):
    if not username or not password:
        return False, "Username dan password tidak boleh kosong."
    
    if username in storage.users:
        return False, "Username sudah ada."
    
    storage.users[username] = {"password": password, "role": "USER"}
    storage.save_all()
    return True, "Registrasi berhasil."

def login(username, password):
    if not username or not password:
        return False, "Input tidak boleh kosong."
    
    if username not in storage.users:
        return False, "User tidak ditemukan."
    
    if storage.users[username]["password"] != password:
        return False, "Password salah."
    
    # login berhasil, kembalikan role user
    return True, storage.users[username]["role"]
