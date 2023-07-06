# main.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import select_database_file, toggle_checkbox_state, toggle_all_checkboxes, update_checkbox_header, tables_info, tables_mssql_info
import create_csv
from datetime import date, datetime
from tkcalendar import Calendar


selected_tables = []
selected_columns = {}


def select_columns():
    global selected_tables
    selected_columns.clear()

    if not selected_tables:
        messagebox.showerror("Ошибка", "Не выбраны таблицы")
        return selected_columns
    if database_var.get() == 1:
        tables_columns = tables_mssql_info(database_entry.get())
    else:
        tables_columns = tables_info(database_entry.get())

    def create_column_window(table_name):
        column_window = tk.Toplevel(window)
        column_window.title(f"Выбор столбцов для таблицы {table_name}")
        column_window.geometry("600x300")
        column_frame = tk.Frame(column_window)
        column_frame.pack(pady=10, anchor='w')

        table_name_label = tk.Label(column_frame, text=table_name)
        table_name_label.pack()

        column_tree = ttk.Treeview(column_frame, columns=(
            "Checkbox", "Column"), show="headings", height=10,)
        column_tree.heading("Checkbox", text="")
        column_tree.heading("Column", text="Column")
        column_tree.pack(anchor='w')

        column_tree.column("Checkbox", width=25)
        column_tree.column("Column", width=550)
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

database_var = tk.IntVar()

sqlite_checkbox = tk.Radiobutton(
    left_frame, text="SQLite", variable=database_var, value=0)
sqlite_checkbox.pack(anchor='w')

ms_sql_checkbox = tk.Radiobutton(
    left_frame, text="MS SQL", variable=database_var, value=1)
ms_sql_checkbox.pack(anchor='w')

database_entry = tk.Entry(left_frame, width=30)
database_entry.pack(pady=10, anchor='w')

select_button = tk.Button(left_frame, text="Выбрать базу данных", command=lambda: select_database_file(
    database_entry, table_tree, selected_tables, window, label=output_file_name, database_var=database_var))
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
    right_frame, text="Выбрать названия событий", command=select_columns)
select_columns_button.pack(anchor='w', pady=5)

output_file_name = tk.Label(right_frame, text="Имя выходного файла: ")
output_file_name.pack()

var1 = tk.IntVar()

radio1 = tk.Radiobutton(right_frame, text="Сортировать время по возрастанию",
                        variable=var1, value=0)
radio1.pack(anchor='w')
radio2 = tk.Radiobutton(right_frame, text="Сортировать время по убыванию",
                        variable=var1, value=1)
radio2.pack(anchor='w')

var2 = tk.IntVar()

radio3 = tk.Radiobutton(right_frame, text="Задать диапазон времени",
                        variable=var2, value=1)
radio3.pack(anchor='w')
radio4 = tk.Radiobutton(right_frame, text="Не задавать диапазон времени",
                        variable=var2, value=0)
radio4.pack(anchor='w')


def work():
    execute_button.config(state="disabled")
    ready_to_work = {}
    radiobuttons_values = [var1.get(), database_var.get(), var2.get()]
    for item in selected_columns_tree.get_children():
        values = selected_columns_tree.item(item)["values"]
        table_name = values[0]
        column_value = values[1]
        if table_name in ready_to_work:
            ready_to_work[table_name].append(column_value)
        else:
            ready_to_work[table_name] = [column_value]
    if len(ready_to_work) == 0:
        messagebox.showerror("Ошибка", "Не выбраны события")
        execute_button.config(state='active')
        return
    flags = [bool(value) for value in radiobuttons_values]
    date_limit = []
    if flags[-1]:
        additional_window = tk.Toplevel(window)
        additional_window.title("Задача диапазона времени")
        additional_window.resizable(width=False, height=True)
        additional_window.geometry("375x500")
        today = date.today()

        def on_date_select(date1, date2):
            date1 = datetime.strptime(date1, '%d-%m-%Y').strftime('%Y-%m-%d')
            date1 = datetime.strptime(date1, '%Y-%m-%d')
            date2 = datetime.strptime(date2, '%d-%m-%Y').strftime('%Y-%m-%d')
            date2 = datetime.strptime(date2, '%Y-%m-%d')
            if date1 > date2:
                messagebox.showerror(
                    "Ошибка", "Вы выбрали конечную дату, которая была раньше, чем начальная дата")
                pass
            else:
                date_limit.append(date1)
                date_limit.append(date2)
                additional_window.destroy()
        label1 = tk.Label(
            additional_window, text=f'Введите начальную дату')
        label1.pack(pady=5)
        calendar1 = Calendar(additional_window, selectmode="day", date_pattern="dd-mm-yyyy",
                             year=today.year, month=today.month, day=today.day)
        calendar1.pack(pady=2)

        label2 = tk.Label(
            additional_window, text=f'Введите конечную дату')
        label2.pack(pady=5)
        calendar2 = Calendar(additional_window, selectmode="day", date_pattern="dd-mm-yyyy",
                             year=today.year, month=today.month, day=today.day)
        calendar2.pack(pady=2)

        button = tk.Button(additional_window, text="Выбрать",
                           command=lambda: on_date_select(calendar1.get_date(), calendar2.get_date()))
        button.pack(pady=5)

        additional_window.wait_window(additional_window)

    output_file = output_file_name.cget('text')
    output_file = output_file[output_file.find(':')+2:]
    complete = create_csv.main_alghrotitm(
        table_and_columns=ready_to_work,
        database_path=database_entry.get(),
        flags=flags,
        output_file_name=output_file if len(output_file) > 0 else 'output',
        date_limit=date_limit if len(date_limit) > 0 else []
    )
    if complete:
        messagebox.showinfo("Успех", "Отчёт успешно создан")
        execute_button.config(state="active")


execute_button = tk.Button(right_frame, text="Выполнить",
                           command=work)
execute_button.pack(anchor='s', pady=5, padx=15)


selected_columns_tree = ttk.Treeview(right_frame, columns=(
    "Table", "Column"), show="headings", height=50)
selected_columns_tree.heading("Table", text="Table")
selected_columns_tree.heading("Column", text="Column")
selected_columns_tree.pack(anchor='w')


# Заполнение пустого пространства в окне
window.grid_rowconfigure(1, weight=1)

window.mainloop()
