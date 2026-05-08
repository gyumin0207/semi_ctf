# init_db.py
import sqlite3
import os

db_path = '/app/ctf.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'user')''')
c.execute('''CREATE TABLE IF NOT EXISTS secrets 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, value TEXT NOT NULL)''')


users = [
    (1, 'alice', 'alice1234', 'user'),
    (2, 'bob', 'b0bpassword', 'user'),
    (3, 'admin', 'metamong123', 'admin')
]
secrets = [
    (1, 'FLAG', 'DH{this_is_fake_flag}'),
    (2, 'INTERNAL_KEY', 'INTERNAL-9f3a2b1c-do-not-share')
]

c.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", users)
c.executemany("INSERT OR IGNORE INTO secrets VALUES (?,?,?)", secrets)

conn.commit()
conn.close()
print('DB initialized successfully.')
