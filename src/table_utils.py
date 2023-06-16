# table_utils.py

def update_checkbox_value(item, table_tree):
    values = table_tree.item(item)["values"]
    if values:
        checkbox_state = values[0]
        if checkbox_state == "[X]":
            table_tree.item(item, values=('[  ]', values[1]))
        else:
            table_tree.item(item, values=('[X]', values[1]))


def update_checkbox_columns(item, tree):
    # Получение значения флажка
    checkbox_value = tree.set(item, "Checkbox")

    # Обновление значения флажка
    if checkbox_value == "[X]":
        tree.set(item, "Checkbox", "[  ]")
    elif checkbox_value == "[  ]":
        tree.set(item, "Checkbox", "[X]")

    # Обновление отображения флажка в таблице
    tree.item(item, values=(tree.set(item, "Checkbox"), tree.set(item, "Column")))
