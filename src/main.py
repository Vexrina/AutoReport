import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import select_database_file, toggle_checkbox_state, toggle_all_checkboxes, update_checkbox_header, tables_info

selected_tables = []
selected_columns = {}


def select_columns():
    global selected_tables
    selected_columns.clear()

    if not selected_tables:
        messagebox.showerror("Ошибка", "Не выбраны таблицы")
        return selected_columns

    tables_columns = tables_info(database_entry.get())
    for table in tables_columns:
        ind = tables_columns[table].index('Time')
        tables_columns[table].pop(ind)

    def create_column_window(table_name):
        column_window = tk.Toplevel(window)
        column_window.title(f"Выбор столбцов для таблицы {table_name}")

        column_frame = tk.Frame(column_window)
        column_frame.pack(pady=10, anchor='w')

        column_tree = ttk.Treeview(column_frame, columns=(
            "Checkbox", "Column"), show="headings", height=10)
        column_tree.heading("Checkbox", text="")
        column_tree.heading("Column", text="Column")
        column_tree.pack(anchor='w')

        column_tree.column("Checkbox", width=25)
        column_tree.heading(
            "Checkbox", command=lambda: toggle_all_checkboxes(column_tree))
        selected_columns[table_name] = []
        column_tree.bind("<ButtonRelease-1>", lambda event, table_name=table_name:
                         toggle_checkbox_state(column_tree.focus(), column_tree, selected_columns[table_name]))

        columns = tables_columns[table_name]
        for column in columns:
            column_tree.insert("", "end", values=["[  ]", column])

        update_checkbox_header(column_tree)

        confirm_button = tk.Button(
            column_frame, text="Подтвердить выбор", command=lambda: confirm_selection(column_window, table_name, column_tree))
        confirm_button.pack()

        return column_window

    def confirm_selection(window, table_name, column_tree):
        selected_columns[table_name] = []
        for child in column_tree.get_children():
            values = column_tree.item(child)["values"]
            if values[0] == "[X]":
                selected_columns[table_name].append(values[1])

        window.destroy()

        if selected_tables:
            next_table_name = selected_tables.pop(0)
            create_column_window(next_table_name)
        else:
            update_selected_columns_table()

    def update_selected_columns_table():
        selected_columns_tree.delete(*selected_columns_tree.get_children())
        for table_name, columns in selected_columns.items():
            for column in columns:
                selected_columns_tree.insert(
                    "", "end", values=(table_name, column))

    table_name = selected_tables.pop(0)
    create_column_window(table_name)

    return selected_columns


window = tk.Tk()
window.title("Выбор файла базы данных")
window.geometry("800x600")

# Определение сетки для окна
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

left_frame = tk.Frame(window)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Определение сетки для left_frame
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_rowconfigure(0, weight=1)

database_entry = tk.Entry(left_frame, width=30)
database_entry.pack(pady=10, anchor='w')

select_button = tk.Button(left_frame, text="Выбрать базу данных", command=lambda: select_database_file(
    database_entry, table_tree, selected_tables, window, labels=[remaining_time_label, output_file_name]))
select_button.pack(anchor='w', pady=5)

table_frame = tk.Frame(left_frame)
table_frame.pack(pady=10, anchor='w')

table_tree = ttk.Treeview(table_frame, columns=(
    "Checkbox", "Table"), show="headings", height=50)
table_tree.heading("Checkbox", text="")
table_tree.heading("Table", text="Table")
table_tree.pack(anchor='w')

table_tree.column("Checkbox", width=25)
table_tree.heading(
    "Checkbox", command=lambda: toggle_all_checkboxes(table_tree))
table_tree.bind("<ButtonRelease-1>", lambda event: toggle_checkbox_state(
    table_tree.focus(), table_tree, selected_tables))

right_frame = tk.Frame(window)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Определение сетки для right_frame
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=1)

select_columns_button = tk.Button(
    right_frame, text="Выбрать столбцы", command=select_columns)
select_columns_button.pack(anchor='w', pady=5)

remaining_time_label = tk.Label(right_frame, text="Оставшееся время: 0 секунд")
remaining_time_label.pack()

output_file_name = tk.Label(right_frame, text="Имя выходного файла: ")
output_file_name.pack()

def work():
    print()

execute_button = tk.Button(right_frame, text="Выполнить", command=work)
execute_button.pack(anchor='s', pady=5, padx=15)


selected_columns_tree = ttk.Treeview(right_frame, columns=(
    "Table", "Column"), show="headings", height=50)
selected_columns_tree.heading("Table", text="Table")
selected_columns_tree.heading("Column", text="Column")
selected_columns_tree.pack(anchor='w')


# Заполнение пустого пространства в окне
window.grid_rowconfigure(1, weight=1)

window.mainloop()
