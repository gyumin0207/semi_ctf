FROM python:3.11-slim

WORKDIR /app

RUN pip install flask==3.0.3 --no-cache-dir

COPY . .

RUN python -c " \
import sqlite3, os; \
conn = sqlite3.connect('/app/ctf.db'); \
c = conn.cursor(); \
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'user')'''); \
c.execute('''CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, value TEXT NOT NULL)'''); \
c.execute(\"INSERT OR IGNORE INTO users (id,username,password,role) VALUES (1,'alice','alice1234','user')\"); \
c.execute(\"INSERT OR IGNORE INTO users (id,username,password,role) VALUES (2,'bob','b0bpassword','user')\"); \
c.execute(\"INSERT OR IGNORE INTO users (id,username,password,role) VALUES (3,'admin','sup3r_s3cr3t_4dm1n!','admin')\"); \
c.execute(\"INSERT OR IGNORE INTO secrets (id,name,value) VALUES (1,'FLAG','CTF{SQLi_1s_4lw4ys_d4ng3r0us_sanitize_inputs!}')\"); \
c.execute(\"INSERT OR IGNORE INTO secrets (id,name,value) VALUES (2,'INTERNAL_KEY','INTERNAL-9f3a2b1c-do-not-share')\"); \
conn.commit(); \
conn.close(); \
print('DB initialized.');"

EXPOSE 5000

CMD ["python", "app.py"]
