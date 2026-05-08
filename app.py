from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)


FLAG = os.environ.get("FLAG", "DH{this_is_fake_flag_for_local_test}")

DATABASE = '/app/ctf.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )
    ''')

    
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, 'alice', 'alice1234', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2, 'bob', 'b0bpassword', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (3, 'admin', 'sup3r_s3cr3t_4dm1n!', 'admin')")

    
    cursor.execute("INSERT OR IGNORE INTO secrets (id, name, value) VALUES (1, 'FLAG', ?)", (FLAG,))
    cursor.execute("INSERT OR IGNORE INTO secrets (id, name, value) VALUES (2, 'INTERNAL_KEY', 'INTERNAL-9f3a2b1c-do-not-share')")

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()

        
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

@app.route('/admin/system')
def admin_system():
    
    if not session.get('logged_in') or session.get('role') != 'admin':
        return "<h1>Access Denied</h1><p>관리자만 접근 가능합니다.</p>", 403
    
    import os
    
    env_vars = dict(os.environ)
    
    return render_template('system.html', env_vars=env_vars)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
