from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = '/app/ctf.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table (로그인용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Secret table (플래그 보관)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )
    ''')

    # 일반 사용자 데이터
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, 'alice', 'alice1234', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2, 'bob', 'b0bpassword', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (3, 'admin', 'sup3r_s3cr3t_4dm1n!', 'admin')")

    # 플래그 저장
    cursor.execute("INSERT OR IGNORE INTO secrets (id, name, value) VALUES (1, 'FLAG', 'CTF{SQLi_1s_4lw4ys_d4ng3r0us_sanitize_inputs!}')")
    cursor.execute("INSERT OR IGNORE INTO secrets (id, name, value) VALUES (2, 'INTERNAL_KEY', 'INTERNAL-9f3a2b1c-do-not-share')")

    conn.commit()
    conn.close()

# ──────────────────────────────────────────────
# 라우트
# ──────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

# [취약] 로그인 — SQL Injection 가능
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()

        # !! 취약한 쿼리 !!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except Exception as e:
            conn.close()
            error = f"DB Error: {e}"
            return render_template('login.html', error=error)

        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials."

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html',
                           username=session.get('username'),
                           role=session.get('role'))

# [취약] 사용자 검색 — UNION-based SQL Injection 가능
@app.route('/search')
def search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    query_param = request.args.get('q', '')
    results = []
    error = None
    raw_query = None

    if query_param:
        conn = get_db()
        cursor = conn.cursor()

        # !! 취약한 쿼리 !!
        raw_query = f"SELECT id, username, role FROM users WHERE username LIKE '%{query_param}%'"

        try:
            cursor.execute(raw_query)
            results = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            error = f"Query Error: {e}"

        conn.close()

    return render_template('search.html',
                           results=results,
                           query=query_param,
                           raw_query=raw_query,
                           error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
