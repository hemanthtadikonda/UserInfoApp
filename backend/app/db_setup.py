import sqlite3

def init_db():
    connection = sqlite3.connect('user_data.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS user_info (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                language TEXT NOT NULL)''')
    connection.close()
