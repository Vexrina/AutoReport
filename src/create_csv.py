# create_csv.py
import pandas as pd
import sqlite3
import pyodbc

# database = r'C:\Users\Vexrina\Desktop\projects\practice\Obluchok.sqlite'
tables_and_collumns = {
    # 'EventsShsm': ['Name', 'Type', 'Identifier'],
    'EventsSHUM': ['Name', 'Type', 'Identifier'],
    # 'Events7XA': ['Name', 'Type', 'Identifier'],
    'EventsAvtuk': ['Name', 'Type', 'Identifier'],
}


def pre_processing_df(dataframe: pd.DataFrame):
    new_df = pd.DataFrame(columns=['Name', 'ID', 'Приход', 'Уход',
                                   'Длительность', 'Квитирование']
                          )
    index = 0
    iteration = 0
    while index < len(dataframe):
        iteration += 1
        row = dataframe.iloc[index]
        new_row = {
            'Name': row['Name'],
            'ID': row['Identifier'],
        }
        if row['Type'] == 0:
            name, id = row['Name'], row['Identifier']
            new_index = index
            for inner_index, inner_row in dataframe.iloc[index:].iterrows():
                if name == inner_row['Name'] and inner_row['Type'] == 1:
                    new_index = inner_index
                    break
            if new_index > index:
                time_start = row['Time']
                time_end = dataframe.iloc[new_index]['Time']
                new_row['Приход'] = pd.to_datetime(time_start)
                new_row['Уход'] = pd.to_datetime(time_end)
                new_row['Длительность'] = new_row['Уход'] - new_row['Приход']
                new_row['Квитирование'] = '---'
            else:
                time_start = row['Time']
                new_row['Приход'] = pd.to_datetime(time_start)
                new_row['Уход'] = '---'
                new_row['Длительность'] = '---'
                new_row['Квитирование'] = '---'
            new_df = pd.concat(
                [new_df, pd.DataFrame([new_row])], ignore_index=True)
            dataframe = dataframe.drop(
                dataframe.index[0]).reset_index(drop=True)
            # index += 1
        if row['Type'] == 2:
            name, id = row['Name'], row['Identifier']
            inner_index = len(new_df)-1
            while inner_index > 0:
                inner_row = new_df.iloc[inner_index].copy()
                if inner_row['Name'] == name and inner_row['ID'] == id and inner_row['Квитирование'] == '---':
                    inner_row['Квитирование'] = pd.to_datetime(row['Time'])
                    break
                inner_index -= 1
            if inner_index > 0:
                new_df.loc[inner_index] = inner_row
                dataframe = dataframe.drop(
                    dataframe.index[0]).reset_index(drop=True)
            else:
                time_kvit = row['Time']
                new_row['Приход'] = '---'
                new_row['Уход'] = '---'
                new_row['Длительность'] = '---'
                new_row['Квитирование'] = pd.to_datetime(time_kvit)
                dataframe = dataframe.drop(
                    dataframe.index[0]).reset_index(drop=True)
            # index += 1
        if row['Type'] == 1:
            time_end = row['Time']
            new_row['Приход'] = '---'
            new_row['Уход'] = pd.to_datetime(time_end)
            new_row['Длительность'] = '---'
            new_row['Квитирование'] = '---'
            dataframe = dataframe.drop(
                dataframe.index[0]).reset_index(drop=True)
    return new_df


def create_pd_table(data, flag_sort, need_names, date_limit, table_names):
    df_list = []
    for i in range(len(data)):
        df = pd.DataFrame.from_dict(data[i])
        df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%dT%H:%M:%S.%f')
        if len(date_limit)>0:
            df = df[(df['Time'] >= date_limit[0]) & (df['Time'] <= date_limit[1])]
        df = pre_processing_df(df)
        df = df[df['Name'].isin(need_names[i])]
        df['TableName'] = table_names[i]
        df_list.append(df)
    result_df = pd.concat(df_list, axis=0)
    if not flag_sort:
        result_df = result_df.sort_values('Приход')
    else:
        result_df = result_df.sort_values('Приход', ascending=False)
    return result_df


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
    data = ['Name', 'Type', 'Identifier', 'Time']
    if database_var == 0:
        for table in table_and_columns.keys():
            table_data = {}
            for column in data:
                table_data[column] = take_data_sqlite(table, column, database)
            array_of_dict.append(table_data)
    else:
        for table in table_and_columns.keys():
            table_data = {}
            for column in data:
                table_data[column] = take_data_mssql(table, column, database)
            array_of_dict.append(table_data)
    return array_of_dict


def save_csv(dataframe: pd.DataFrame, output_file):
    dataframe.to_csv(f'{output_file}.csv', index=False)


def main_alghrotitm(table_and_columns: dict, database_path, flags, output_file_name, date_limit):
    taken = take_datas(table_and_columns, database_path, flags[1])
    # print(taken)
    taken = [k for k in taken if k != {}]
    need_names = [table_and_columns[k] for k in table_and_columns.keys()]
    table_names = [k for k in table_and_columns.keys()]
    df = create_pd_table(taken, flags[0], need_names, date_limit, table_names)
    df['Длительность'] = df['Длительность'].astype(str)
    save_csv(df, output_file_name)
    return True

# main_alghrotitm(tables_and_collumns, database, [0, 0, 0, 0])
