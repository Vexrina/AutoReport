import tkinter as tk
from tkinter import filedialog
import sqlite3
from tkinter import ttk

def select_database_file():
    file_path = filedialog.askopenfilename(filetypes=[("SQLite Databases", "*.db *.sqlite")])
    database_entry.delete(0, tk.END)
    database_entry.insert(tk.END, file_path)
    display_tables(file_path)

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

def update_checkbox_state(table):
    if table in selected_tables:
        return "[X]"
    else:
        return "[  ]"

def display_tables(database_file):
    tables = tables_info(database_file)
    # Очистка таблицы перед обновлением
    for row in table_tree.get_children():
        table_tree.delete(row)

    # Добавление данных в таблицу
    for table in tables:
        table_tree.insert("", tk.END, values=(update_checkbox_state(table), table))

def toggle_checkbox_state(item):
    table = table_tree.item(item)["values"][-1]  # Получение названия таблицы

    if table in selected_tables:
        selected_tables.remove(table)
    else:
        selected_tables.append(table)

    # Обновление отображения
    table_tree.item(item, values=(update_checkbox_state(table), table))
    update_checkbox_header()

def toggle_all_checkboxes():
    global checkbox_header_state
    global selected_tables 
    if checkbox_header_state == "[X]":
        checkbox_header_state = "[  ]"
        selected_tables.clear()
    else:
        checkbox_header_state = "[X]"
        selected_tables = list(table_tree.get_children())

    for item in table_tree.get_children():
        table_tree.item(item, values=(checkbox_header_state, table_tree.item(item)["values"][1]))
    update_checkbox_header()

def update_checkbox_header():
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

# Создание окна
window = tk.Tk()
window.title("Выбор файла базы данных")
window.geometry("600x500")

# Глобальная переменная для хранения выбранных таблиц
selected_tables = []

# Текстовое поле для отображения выбранного файла базы данных
database_entry = tk.Entry(window, width=50)
database_entry.pack(pady=10)

# Кнопка для выбора файла базы данных
select_button = tk.Button(window, text="Выбрать базу данных", command=select_database_file)
select_button.pack(pady=5)

# Создание таблицы
table_tree = ttk.Treeview(window, columns=("Checkbox", "Table"), show="headings")
table_tree.heading("Checkbox", text="")
table_tree.heading("Table", text="Table")
table_tree.pack(pady=10)

# Функция для обновления изображения флажка в Treeview
def update_checkbox_value(item):
    values = table_tree.item(item)["values"]
    if values:
        checkbox_state = values[0]
        if checkbox_state == "[X]":
            table_tree.item(item, values=('[  ]', values[1]))
        else:
            table_tree.item(item, values=('[X]', values[1]))

# Добавление столбца для флажков
table_tree.column("Checkbox", width=50)
table_tree.heading("Checkbox", command=toggle_all_checkboxes)  # Привязка функции toggle_all_checkboxes к клику на заголовок
table_tree.bind("<ButtonRelease-1>", lambda event: toggle_checkbox_state(table_tree.focus()))  # Привязка функции toggle_checkbox_state к событию отпускания кнопки мыши

# Обновление отображения флажков
if table_tree.get_children():
    first_item = table_tree.get_children()[0]  # Выбор первого элемента
    table_tree.focus(first_item)  # Установка фокуса на первый элемент
    for item in table_tree.get_children():
        update_checkbox_value(item)

# Обновление заголовка флажка
update_checkbox_header()

window.mainloop()
