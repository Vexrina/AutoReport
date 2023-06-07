import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import select_database_file, toggle_checkbox_state, toggle_all_checkboxes, update_checkbox_header, tables_info
import create_csv
import re


selected_tables = []
selected_columns = {}


def select_columns():
    global selected_tables
    selected_columns.clear()

    if not selected_tables:
        messagebox.showerror("Ошибка", "Не выбраны таблицы")
        return selected_columns

    tables_columns = tables_info(database_entry.get())
    pattern = re.compile(r'^Quality_.+')
    '''
    т.к. есть необходимость удалять любые Quality при выборе столбцов, 
    лучше всего для этого подойдут регулярка: 
    ^ - указывает, что соответствие должно начинаться с начала строки.
    Quality_ - точное соответствие подстроке "Quality_".
    .+ - означает, что после подстроки "Quality_" может быть один 
    или более любых символов, кроме символа новой строки.
    '''
    for table in tables_columns:
        ind = tables_columns[table].index('Time')
        tables_columns[table].pop(ind)

    for table, values in tables_columns.items():
        filtered_values = [
            value for value in values if not pattern.match(value)]
        tables_columns[table] = filtered_values

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

var1 = tk.IntVar()
var3 = tk.IntVar()
var5 = tk.IntVar()
var7 = tk.IntVar()

radio1 = tk.Radiobutton(right_frame, text="Сортировать время по возрастанию",
                        variable=var1, value=0)
radio1.pack(anchor='w')
radio2 = tk.Radiobutton(right_frame, text="Сортировать время по убыванию",
                        variable=var1, value=1)
radio2.pack(anchor='w')

radio3 = tk.Radiobutton(right_frame, text="Настроить имена столбцов",
                        variable=var3, value=1)
radio3.pack(anchor='w')
radio4 = tk.Radiobutton(right_frame, text="Не настраивать имена столбцов",
                        variable=var3, value=0)
radio4.pack(anchor='w')

radio5 = tk.Radiobutton(right_frame, text="Настроить пороговые значения",
                        variable=var5, value=1)
radio5.pack(anchor='w')
radio6 = tk.Radiobutton(right_frame, text="Не настраивать пороговые значения",
                        variable=var5, value=0)
radio6.pack(anchor='w')

radio7 = tk.Radiobutton(right_frame, text="Формат времени: HH:MM:00",
                        variable=var7, value=1)
radio7.pack(anchor='w')
radio8 = tk.Radiobutton(right_frame, text="Формат времени: HH:00:00",
                        variable=var7, value=0)
radio8.pack(anchor='w')


def work():
    ready_to_work = {}
    radiobuttons_values = [var1.get(), var3.get(), var5.get(), var7.get()]
    old_names = []
    for item in selected_columns_tree.get_children():
        values = selected_columns_tree.item(item)["values"]
        table_name = values[0]
        column_value = values[1]
        old_names.append(column_value)
        if table_name in ready_to_work:
            ready_to_work[table_name].append(column_value)
        else:
            ready_to_work[table_name] = [column_value]
    if len(ready_to_work) == 0:
        messagebox.showerror("Ошибка", "Не выбраны столбцы")
        return
    flags = [bool(value) for value in radiobuttons_values]

    if flags[1]:  # по хорошему, надо обернуть в функцию, но не хочется парится с этим
        additional_window = tk.Toplevel(window)
        additional_window.title("Переименование столбцов")
        additional_window.resizable(width=False, height=True)
        additional_window.geometry("375x500")

        # Создание прокручиваемой области
        canvas = tk.Canvas(additional_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Создание виджета прокрутки
        scrollbar = tk.Scrollbar(additional_window, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка прокручиваемой области к виджету прокрутки
        canvas.config(yscrollcommand=scrollbar.set)

        # Создание фрейма в прокручиваемой области
        frame = tk.Frame(canvas)

        # Помещение фрейма в прокручиваемую область
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        instr_label = tk.Label(
            frame,
            text='Введите новые имена для столбцов\nПри вводе пустой строки останется старое имя столбца'
        )
        instr_label.pack(pady=5)

        entry_list = []

        for name in old_names:
            label = tk.Label(frame, text=f'Введите имя для столбца {name}')
            label.pack(pady=5)

            entry = tk.Entry(frame)
            entry.pack(pady=5)
            entry_list.append(entry)

        new_names = []

        def save_names():
            for entry in entry_list:
                new_names.append(entry.get())
            additional_window.destroy()

        # Создание вложенного фрейма для кнопки "Сохранить"
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        save_button = tk.Button(
            button_frame, text="Сохранить", command=save_names)
        save_button.pack()

        # Обновление размеров прокручиваемой области при изменении содержимого
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        frame.bind("<Configure>", update_scroll_region)

        additional_window.protocol("WM_DELETE_WINDOW", save_names)
        additional_window.wait_window(additional_window)
    if flags[2]:  # edit outers
        additional_window = tk.Toplevel(window)
        additional_window.title("Задача пороговых значений")
        additional_window.resizable(width=False, height=True)
        additional_window.geometry("375x500")
        canvas = tk.Canvas(additional_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(additional_window, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)
        instr_label = tk.Label(
            frame,
            text='Введите верхние пороговые значения для столбцов\nПри вводе любой не числовой строки,\n верхняя граница столбца будет определена автоматически'
        )
        instr_label.pack(pady=5)
        entry_list = []
        for name in old_names:
            label = tk.Label(
                frame, text=f'Введите верхнюю границу для столбца {name}')
            label.pack(pady=5)

            entry = tk.Entry(frame)
            entry.pack(pady=5)
            entry_list.append(entry)
        outers = []

        def save_names():
            for entry in entry_list:
                outers.append(entry.get())
            additional_window.destroy()
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        save_button = tk.Button(
            button_frame, text="Сохранить", command=save_names)
        save_button.pack()

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))
        frame.bind("<Configure>", update_scroll_region)
        additional_window.protocol("WM_DELETE_WINDOW", save_names)
        additional_window.wait_window(additional_window)


    if flags[1]:
        rename = {k: v for k, v in zip(old_names, new_names)}
    
    output_file = output_file_name.cget('text')
    output_file = output_file[output_file.find(':')+2:]
    # print(output_file)
    create_csv.main_alghrotitm(
        table_and_columns=ready_to_work,
        database_path=database_entry.get(),
        flags=flags,
        new_names=rename,
        outers=outers,
        output_file_name=output_file)


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
