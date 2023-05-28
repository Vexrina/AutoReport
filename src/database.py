import tkinter as tk
from tkinter import filedialog
import sqlite3
from tkinter import ttk


def select_database_file(entry, table_tree, selected_tables):
    file_path = filedialog.askopenfilename(
        filetypes=[("SQLite Databases", "*.db *.sqlite")])
    entry.delete(0, tk.END)
    entry.insert(tk.END, file_path)
    display_tables(file_path, table_tree, selected_tables)


def tables_info(database_file):
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
    return tables_and_columns


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
