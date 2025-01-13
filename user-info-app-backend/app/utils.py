import sqlite3

def add_user(name, language):
    connection = sqlite3.connect('user_data.db')
    with connection:
        connection.execute('INSERT INTO user_info (name, language) VALUES (?, ?)', (name, language))
    connection.close()
