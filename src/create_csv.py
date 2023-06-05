import pandas as pd
import tkinter
import sqlite3
import numpy as np
import shutil
from datetime import datetime

# table_and_columns = {
#     'VibrShort': ['Quality_VibA1', 'VibA3'],
#     'MainBushMShort': ['UB', 'UC', 'IA']
# }

# database_path = r'C:\Users\Vexrina\Desktop\projects\practice\YERMAK_T1.sqlite'


def create_pd_table(data: dict, flag: bool) -> pd.DataFrame:
    # Создание пустой пандас таблицы
    df = pd.DataFrame().from_dict(data[0])
    for i in range(1, len(data)):
        temp = pd.DataFrame().from_dict(data[i])
        df = df.merge(temp, on='Time', how='outer')
    if not flag:
        df = df.sort_values(by='Time')
    else:
        df = df.sort_values(by='Time', ascending=False)
    df.insert(0, 'Time', df.pop('Time'))
    df = df.reset_index(drop=True)
    print(df.head())
    return df


def quality(data: pd.Series) -> pd.Series:
    return data.apply(lambda x: x if x == 192 else None)


def upper(data: pd.Series, column: str) -> pd.Series:
    mean_val = data.mean()
    max_val = data.max()
    threshold = mean_val + (max_val - mean_val) / 2
    data = data[data <= threshold]
    return data


def take_data(table: str, column: str, database_path: str) -> list[any]:
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    query = f"SELECT {column} FROM {table}"
    cursor.execute(query)

    # Извлечение данных из результата запроса
    column_data = [value[0] for value in cursor.fetchall()]

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()
    return column_data


def take_datas(table_and_columns: dict[str, list[str]], database: str) -> list[dict]:
    array_of_dict = [{} for __ in range(len(table_and_columns.keys()))]
    k = 0
    for table in table_and_columns.keys():
        array = table_and_columns[table]
        for column in array:
            array_of_dict[k][column] = take_data(table.replace(
                " ", ""), column.replace(" ", ""), database)
            try:
                quality_str = 'Quality_'+column.replace(" ", "")
                quality_data = take_data(table.replace(
                    " ", ""), quality_str, database)
                array_of_dict[k][quality_str] = quality_data
            except:
                continue
        array_of_dict[k]['Time'] = take_data(
            table.replace(" ", ""), 'Time', database)
        k += 1
    return array_of_dict


def get_table_data(table_name: str, database_path: str) -> list[any]:
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Выполнение запроса SELECT для получения всей таблицы
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Извлечение данных из результата запроса
    table_data = cursor.fetchall()

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()

    return table_data


def processing_df(dataframe: pd.DataFrame, flag_Time: bool) -> pd.DataFrame:
    not_number = [
        'Name', 'Time', 'Tel_Number', 'Comp_Name', 'Object_Name',
        'Ser_Number', 'message', 'core_start_time', 'psw',
        'Trans_Mode', 'Prod_Fact', 'Stat_Name', 'TOil'
    ]

    dataframe['Time'] = dataframe['Time'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f'))

    if not flag_Time:
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:00:00'))
    else:
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:00'))

    for column_name, column in dataframe.items():
        if column_name not in not_number and column_name.find('Quality_') == -1:
            dataframe[column_name] = upper(column, column_name)
        elif column_name.find('Quality_') == 0:
            dataframe[column_name] = quality(column)

    dataframe = dataframe.dropna(
        subset=dataframe.columns[dataframe.columns != 'Time'], how='all')

    return dataframe


def save_csv(dataframe: pd.DataFrame, output_file: str):
    dataframe.to_csv(f'{output_file}.csv', index=False)


def main_alghrotitm(table_and_columns: dict[str, list[str]], database_path: str, flags: list[bool]):
    taken = take_datas(table_and_columns, database_path)
    df = create_pd_table(taken, flags[0])
    processing_df(df, flags[-1])
    print(df.isna().sum())
    print(df.head())
    save_csv(df, 'output')
