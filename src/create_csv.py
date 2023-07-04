# create_csv.py
import pandas as pd
import sqlite3
from datetime import datetime
import pyodbc
import numpy as np


def create_pd_table(data, flag_sort):
    # Создание пустой пандас таблицы
    try:
        df = pd.DataFrame().from_dict(data[0])
        for i in range(1, len(data)):
            temp = pd.DataFrame().from_dict(data[i])
            temp['Time'] = temp['Time'].astype(str)
            df = df.merge(temp, on='Time', how='outer')
    except ValueError:
        df = pd.DataFrame().from_dict(data[0])
        for i in range(1, len(data)):
            temp = pd.DataFrame().from_dict(data[i])
            temp['Time'] = pd.to_datetime(temp['Time'])
            df = df.merge(temp, on='Time', how='outer')
    if not flag_sort:
        df = df.sort_values(by='Time')
    else:
        df = df.sort_values(by='Time', ascending=False)
    df.insert(0, 'Time', df.pop('Time'))
    df = df.reset_index(drop=True)
    return df


def quality(data):
    return data.apply(lambda x: x if x == 192 else None)


def upper(data):
    mean_val = data.mean()
    max_val = data.max()
    threshold = mean_val + (max_val - mean_val) / 2
    data = data[data <= threshold]
    return data


def take_data_sqlite(table, column, database_path):
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


def take_data_mssql(table, column, connection_string):
    # Подключение к базе данных MS SQL Server
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    query = f"SELECT {column} FROM {table}"
    cursor.execute(query)

    # Извлечение данных из результата запроса
    column_data = [value[0] for value in cursor.fetchall()]

    # Закрытие соединения с базой данных
    cursor.close()
    conn.close()
    return column_data


def take_datas(table_and_columns, database, database_var=0):
    array_of_dict = [{} for __ in range(len(table_and_columns.keys()))]
    k = 0
    if database_var == 0:
        for table in table_and_columns.keys():
            array = table_and_columns[table]
            for column in array:
                array_of_dict[k][column] = take_data_sqlite(table.replace(
                    " ", ""), column.replace(" ", ""), database)
                try:
                    quality_str = 'Quality_'+column.replace(" ", "")
                    quality_data = take_data_sqlite(table.replace(
                        " ", ""), quality_str, database)
                    array_of_dict[k][quality_str] = quality_data
                except:
                    continue
            array_of_dict[k]['Time'] = take_data_sqlite(
                table.replace(" ", ""), 'Time', database)
            k += 1
    else:
        for table in table_and_columns.keys():
            array = table_and_columns[table]
            for column in array:
                array_of_dict[k][column] = take_data_mssql(table.replace(
                    " ", ""), column.replace(" ", ""), database)
                try:
                    quality_str = 'Quality_'+column.replace(" ", "")
                    quality_data = take_data_mssql(table.replace(
                        " ", ""), quality_str, database)
                    array_of_dict[k][quality_str] = quality_data
                except:
                    continue
            array_of_dict[k]['Time'] = take_data_mssql(
                table.replace(" ", ""), 'Time', database)
            k += 1
    return array_of_dict


def get_table_data(table_name, database_path):
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


def user_upper(data, value):
    try:
        upper_threshold = int(value[0])
    except ValueError:
        try:
            bottom_threshold = int(value[1])
            return data[bottom_threshold <= data]
        except (ValueError, IndexError):
            return data
    else:
        try:
            bottom_threshold = int(value[1])
            return data[(data <= upper_threshold) & (bottom_threshold <= data)]
        except (ValueError, IndexError):
            return data


def processing_df(dataframe, flag_Time, user_outers, flag_outer=False):
    not_number = [
        'Name', 'Time', 'Tel_Number', 'Comp_Name', 'Object_Name',
        'Ser_Number', 'message', 'core_start_time', 'psw',
        'Trans_Mode', 'Prod_Fact', 'Stat_Name', 'TOil'
    ]
    try:
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f'))
    except ValueError:
        dataframe['Time'] = dataframe['Time'].dt.strftime(
            '%Y-%m-%dT%H:%M:%S.%f')
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f'))
    except TypeError:
        print('that is mssql')

    if not flag_Time:
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:00:00'))
    else:
        dataframe['Time'] = dataframe['Time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:00'))

    k = 0

    for column_name, column in dataframe.items():
        if column_name not in not_number and column_name.find('Quality_') == -1:
            if flag_outer:
                dataframe[column_name] = user_upper(column, user_outers[k])
                k += 1
            # else:
            #     dataframe[column_name] = upper(column)
        elif column_name.find('Quality_') == 0:
            # dataframe[column_name] = quality(column)
            continue
        elif column_name == 'Time':
            continue
        elif column_name in not_number:
            k += 1

    # Получение уникальных подстрок из названий колонок "smth"
    column_substrings = set([col.replace('Quality_', '')
                            for col in dataframe.columns if col.startswith('Quality_')])

    # Применение логики для каждой пары колонок
    for substring in column_substrings:
        smth_col = substring
        quality_col = 'Quality_' + substring
        dataframe[smth_col] = np.where(
            dataframe[quality_col] == 192, dataframe[smth_col], np.nan)

    dataframe = dataframe.dropna(
        subset=dataframe.columns[dataframe.columns != 'Time'], how='all')

    return dataframe


def save_csv(dataframe, output_file):
    dataframe.to_csv(f'{output_file}.csv', index=False)


def rename_columns(dataframe, new_names):
    columns = dataframe.columns.tolist()
    new_columns = ['Time']
    k = 1
    while k < len(columns)-1:
        if columns[k+1] == 'Quality_'+columns[k]:
            if new_names[columns[k]] == '':
                new_columns.append(columns[k])
                new_columns.append('Quality '+columns[k])
                k += 2
            else:
                new_columns.append(new_names[columns[k]])
                new_columns.append('Quality '+new_names[columns[k]])
                k += 2
        else:
            if new_names[columns[k]] == '':
                new_columns.append(columns[k])
                k += 1
            else:
                new_columns.append(columns[k])
                k += 1
    if len(columns) != len(new_columns):
        if new_names[columns[-1]] == '':
            new_columns.append(columns[-1])
        else:
            new_columns.append(new_names[columns[-1]])
    dataframe.columns = new_columns
    return dataframe


def main_alghrotitm(table_and_columns, database_path, flags, new_names={}, outers=[], output_file_name='output', database_var=0, date_limit=[]):
    # print(date_limit)
    taken = take_datas(table_and_columns, database_path, database_var)
    df = create_pd_table(taken, flags[0])
    processing_df(df, flags[-1], outers, flags[-2])
    if flags[1]:
        df = rename_columns(df, new_names)
    if flags[-1]:
        date_limit = [datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d') for date in date_limit]
        # Преобразование колонки 'Time' в тип данных datetime
        df['Time'] = pd.to_datetime(df['Time'])

        # Фильтрация строк по заданным границам дат
        filtered_df = df[(df['Time'] >= date_limit[0]) & (df['Time'] <= date_limit[1])]
        save_csv(filtered_df, output_file_name)
    else:
        save_csv(df,output_file_name)