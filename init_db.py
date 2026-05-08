import sqlite3
db_path = 'ctf.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, name TEXT, value TEXT)')


users = [(1, 'alice', 'alice123', 'user'), (3, 'admin', 'metamong123', 'admin')]
secrets = [(1, 'FLAG', 'DH{this_is_a_fake_flag}')]

c.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", users)
c.executemany("INSERT OR IGNORE INTO secrets VALUES (?,?,?)", secrets)
conn.commit()
conn.close()
