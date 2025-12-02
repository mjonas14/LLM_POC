import sqlite3

conn = sqlite3.connect("app.db")  # creates file if not exists
conn.close()
