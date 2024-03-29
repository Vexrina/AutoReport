# database.py
import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
from tkinter import ttk
import pyodbc


def open_MSSQL_window(window, table_tree, selected_tables, gui_entry):
    msql_window = tk.Toplevel(window)
    msql_window.title(
        'Введите данные для локального или удаленного MS SQL Server')
    msql_window.geometry("200x325")
    info_label = tk.Label(
        msql_window, text='Введите данные для локального\n или удаленного MS SQL Server')
    info_label.pack(pady=10)

    server_label = tk.Label(
        msql_window, text='Имя или IP-адрес сервера MS SQL')
    database_label = tk.Label(msql_window, text='Имя базы данных')
    username_label = tk.Label(msql_window, text='Имя пользователя')
    password_label = tk.Label(msql_window, text='Пароль')

    server_entry = tk.Entry(msql_window, width=25)
    database_entry = tk.Entry(msql_window, width=25)
    username_entry = tk.Entry(msql_window, width=25)
    password_entry = tk.Entry(msql_window, width=25)
    server_label.pack(pady=5)
    server_entry.pack()
    database_label.pack(pady=10)
    database_entry.pack()
    username_label.pack(pady=10)
    username_entry.pack()
    password_label.pack(pady=10)
    password_entry.pack()

    confirm_button = tk.Button(msql_window, text='Совершить подключение', command=lambda: connect_to_msql(
        msql_window, server_entry, database_entry, username_entry, password_entry, table_tree, selected_tables, gui_entry))
    confirm_button.pack(pady=10)


def connect_to_msql(msql_window, server_entry, database_entry, username_entry, password_entry, table_tree, selected_tables, entry):
    try:
        server = server_entry.get()
        database = database_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        # connection_string = f"DRIVER={{SQL Server}};SERVER=DESKTOP-28I0R39;DATABASE={database};Trusted_Connection=yes;"
        DRIVER_NAME = 'SQL SERVER'
        connection_string = f"""
            DRIVER={{{DRIVER_NAME}}};
            SERVER={server};
            DATABASE={database};
            uid={username};
            pwd={password};
        """
        entry.delete(0, tk.END)
        entry.insert(tk.END, connection_string)
        # print(connection_string)
        display_mssql_tables(table_tree, selected_tables, connection_string)
        msql_window.destroy()

    except pyodbc.OperationalError:
        messagebox.showerror(
            "Ошибка",
            "SQL Server не существует, или доступ запрещён."
        )
    except pyodbc.InterfaceError:
        messagebox.showerror(
            "Ошибка",
            f"При входе в систему пользователя \"{username}\" произошла ошибка."
        )
    except pyodbc.ProgrammingError:
        messagebox.showerror(
            "Ошибка",
            f"Не удается открыть базу данных \"{database}\", запрашиваемую именем входа. Не удалось выполнить вход."
        )


def tables_mssql_info(connection_string):
    conn = pyodbc.connect(connection_string)
    # Создаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()

    # Получаем список таблиц в базе данных
    cursor.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
    tables_and_columns = {}
    tables = cursor.fetchall()

    for table in tables:
        tables_and_columns[table[0]] = []

    for table_name in tables_and_columns.keys():
        # Получаем список столбцов в таблице
        cursor.execute(
            f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';")
        columns = cursor.fetchall()
        # Выводим список столбцов
        for column in columns:
            tables_and_columns[table_name].append(column[0])

    conn.close()

    wo_time = []
    for key in tables_and_columns.keys():
        if 'Time' not in tables_and_columns[key]:
            wo_time.append(key)

    for item in wo_time:
        tables_and_columns.pop(item)
    sorted_t_a_c = dict(sorted(tables_and_columns.items()))
    return sorted_t_a_c


def display_mssql_tables(table_tree, selected_tables, connection_string):
    tables = tables_mssql_info(connection_string)
    for row in table_tree.get_children():
        table_tree.delete(row)
    for table in tables:
        table_tree.insert("", tk.END, values=(
            update_checkbox_state(table, selected_tables), table))


def open_time_window(window, labels):
    time_window = tk.Toplevel(window)
    time_window.title("Имя выходной файл")

    # Метка для выходного файла
    output_file_label = tk.Label(
        time_window, text="Введите имя выходного файла:")
    output_file_label.pack(pady=10)

    # Поле для ввода имени выходного файла
    output_file_entry = tk.Entry(time_window, width=30)
    output_file_entry.pack()

    # Кнопка подтверждения
    confirm_button = tk.Button(time_window, text="Подтвердить", command=lambda: save_data(
        time_window, output_file_entry.get(), labels))
    confirm_button.pack(pady=10)


def select_database_file(entry, table_tree, selected_tables, window, labels, database_var):
    if database_var.get() == 1:
        open_MSSQL_window(window, table_tree, selected_tables, entry)
    else:
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite Databases", "*.db *.sqlite")])
        entry.delete(0, tk.END)
        entry.insert(tk.END, file_path)
        display_tables(file_path, table_tree, selected_tables)
    open_time_window(window, labels)


def save_data(time_window, output_file, labels):
    # Сохранение времени и имени файла
    labels[0]["text"] = f"Имя выходного файла: {output_file}"

    # Дополнительные действия, если необходимо
    time_window.destroy()


def tables_info(database_file: str) -> dict:
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect(database_file)

    # Создаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()

    # Получаем список таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_and_columns = {}
    tables = cursor.fetchall()

    for table in tables:
        if table[0] != 'sqlite_sequence':
            tables_and_columns[table[0]] = []

    for table_name in tables_and_columns.keys():
        # Получаем список столбцов в таблице
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        # Выводим список столбцов
        for column in columns:
            tables_and_columns[table_name].append(column[1])

    conn.close()

    wo_time = []
    for key in tables_and_columns.keys():
        if 'Time' not in tables_and_columns[key]:
            wo_time.append(key)

    for item in wo_time:
        tables_and_columns.pop(item)
    sorted_t_a_c = dict(sorted(tables_and_columns.items()))
    return sorted_t_a_c


def display_tables(database_file, table_tree, selected_tables):
    tables = tables_info(database_file)
    for row in table_tree.get_children():
        table_tree.delete(row)
    for table in tables:
        table_tree.insert("", tk.END, values=(
            update_checkbox_state(table, selected_tables), table))


def toggle_checkbox_state(item, table_tree, selected_tables):
    table = table_tree.item(item)["values"][-1]
    if table in selected_tables:
        selected_tables.remove(table)
    else:
        selected_tables.append(table)
    table_tree.item(item, values=(
        update_checkbox_state(table, selected_tables), table))
    update_checkbox_header(table_tree)


def toggle_checkbox_state(item, table_tree, selected_tables):
    table = table_tree.item(item)["values"][-1]
    if table in selected_tables:
        selected_tables.remove(table)
    else:
        selected_tables.append(table)
    table_tree.item(item, values=(
        update_checkbox_state(table, selected_tables), table))
    update_checkbox_header(table_tree)


def toggle_all_checkboxes(table_tree):
    global checkbox_header_state
    global selected_tables
    if checkbox_header_state == "[X]":
        checkbox_header_state = "[  ]"
        selected_tables.clear()
    else:
        checkbox_header_state = "[X]"
        selected_tables = list(table_tree.get_children())
    for item in table_tree.get_children():
        table_tree.item(item, values=(checkbox_header_state,
                        table_tree.item(item)["values"][1]))
    update_checkbox_header(table_tree)


def update_checkbox_header(table_tree):
    global checkbox_header_state
    checkbox_header_state = "[~]"
    all_selected = True
    all_unselected = True

    for item in table_tree.get_children():
        values = table_tree.item(item)["values"]
        if values[0] != "[X]":
            all_selected = False
        else:
            all_unselected = False

    if all_selected:
        checkbox_header_state = "[X]"
    elif all_unselected:
        checkbox_header_state = "[  ]"

    table_tree.heading("Checkbox", text=checkbox_header_state)


def update_checkbox_state(table, selected_tables):
    if table in selected_tables:
        return "[X]"
    else:
        return "[  ]"
