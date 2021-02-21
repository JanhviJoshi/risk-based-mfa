import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username text, password text, phno text, " \
        "safe_ip text, safe_latitude text, safe_longitude text, safe_time_start text, safe_time_end text)"

cursor.execute(query)

query = "CREATE TABLE IF NOT EXISTS logs (username text, ip text, latitude text, longitude text, time_start text, time_end text)"
cursor.execute(query)

connection.commit()
connection.close()

