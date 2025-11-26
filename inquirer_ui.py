import os
from InquirerPy import inquirer

# =========================================================
# CLEAR TERMINAL
# =========================================================
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def make_table(headers, rows):
    # Hitung lebar kolom
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(col)))

    # Header
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))

    # Garis bawah
    separator = "-".join('-' * (col_widths[i] + 2) for i in range(len(headers)))

    # Isi tabel
    row_lines = []
    for row in rows:
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        row_lines.append(line)

    return f"{header_line}\n{separator}\n" + "\n".join(row_lines)


# =========================================================
# MENU INTERAKTIF (SINKRON DENGAN MENU AWAL)
# =========================================================
def menu(title, options):

    choice = inquirer.select(
        message=title,
        choices=options,
        qmark="",
        instruction=""
    ).execute()

    return options.index(choice)

# =========================================================
# PROMPT INPUT BIASA
# =========================================================
def prompt(msg):
    return inquirer.text(
        message=msg,
        qmark=""
    ).execute().strip()

# =========================================================
# PESAN POP-UP
# =========================================================
def message(msg):
    clear_terminal()
    print(msg)
    input("\nTekan Enter untuk melanjutkan...")

# =========================================================
# PROMPT DARI LIST MULTILINE
# =========================================================
def prompt_under_list(list_text, prompt_text):
    lines = list_text.splitlines()

    if not lines:
        return None

    try:
        choice = inquirer.select(
            message=prompt_text,
            choices=lines,
            qmark="",
            instruction=""
        ).execute()
    except Exception:
        return None

    # Ambil ID sebelum titik
    if "." in choice:
        return choice.split(".")[0].strip()

    return choice.strip()

# =========================================================
# KONFIRM YA / TIDAK
# =========================================================
def confirm_or_back(msg):
    result = inquirer.confirm(
        message=msg,
        qmark="",
        default=True
    ).execute()

    return True if result else None
