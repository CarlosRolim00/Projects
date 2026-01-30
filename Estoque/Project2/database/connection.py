import pyodbc

def connect_db():
    conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=.\\SQLEXPRESS;'
        'Database=Projeto2;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    return conn, cursor