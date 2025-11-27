import os
from InquirerPy import inquirer

# clear
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

# tabel
def make_table(headers, rows):
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(col)))

    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))

    separator = "-".join('-' * (col_widths[i] + 2) for i in range(len(headers)))

    row_lines = []
    for row in rows:
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
        row_lines.append(line)

    return f"{header_line}\n{separator}\n" + "\n".join(row_lines)



# option
def menu(title, options):

    choice = inquirer.select(
        message=title,
        choices=options,
        qmark="",
        instruction=""
    ).execute()

    return options.index(choice)


# input
def prompt(msg):
    return inquirer.text(
        message=msg,
        qmark=""
    ).execute().strip()


# pesan
def message(msg):
    clear_terminal()
    print(msg)
    input("\nTekan Enter untuk melanjutkan...")

# list
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

    if "." in choice:
        return choice.split(".")[0].strip()

    return choice.strip()

# terima atau tolak
def confirm_or_back(msg):
    result = inquirer.confirm(
        message=msg,
        qmark="",
        default=True
    ).execute()

    return True if result else None
