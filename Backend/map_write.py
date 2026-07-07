import sqlite3

conn = sqlite3.connect("Backend\\map.sql")
cursor = conn.cursor()

def data(source: str):
    with open(source, "rb") as f:
        return f.read()
    f.close()

def create(name): #Create a table with attributes ...
    cursor.execute(f"""CREATE  TABLE IF NOT EXISTS  {name}
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   Position_X INT,
                   Position_Y INT)
""")
    
def delete_table(name):
    cursor.execute(f"DROP TABLE IF EXISTS {name}")

def delete_rows(tablename, start_row, end_row):
    for row in range(start_row, end_row):
        cursor.execute(f"DELETE FROM {tablename} WHERE id = {row}")

def insert(name, *args):
    cursor.execute(f"""INSERT INTO {name} ...
""")

delete_table("test")
create("test")
