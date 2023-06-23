import pyodbc

DRIVER_NAME = 'SQL SERVER'
server = '127.0.0.1'
database='Raketa'
username='Vexrina'
password='sa'

SERVER_NAME = server
DATABASE_NAME = database

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={server};
    DATABASE={database};
    uid={username};
    pwd={password};
"""

conn = pyodbc.connect(connection_string)

print(conn)
