from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super_secret_session_key"
DATABASE = 'ctf.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def check_filter(input_str):
    blacklist = ['union', 'select', 'and', '--', '#', '/*']
    for word in blacklist:
        if word in input_str.lower():
            return True, word
    return False, None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        is_blocked, word = check_filter(username)
        if is_blocked:
            return f"<h1>Access Denied</h1><p>'{word}' 키워드는 사용할 수 없습니다.</p><a href='/login'>뒤로가기</a>"

        conn = get_db()
        cursor = conn.cursor()
       
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = cursor.execute(query).fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return "<h1>Login Failed</h1><a href='/login'>뒤로가기</a>"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/admin/system')
def admin_system():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return "<h1>Access Denied</h1>", 403
    
    
    env_vars = dict(os.environ)
    return render_template('system.html', env_vars=env_vars)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    
    if not os.path.exists(DATABASE):
        import subprocess
        subprocess.run(["python", "init_db.py"])
    
    
    real_flag = os.environ.get("FLAG")
    if real_flag:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE secrets SET value = ? WHERE name = 'FLAG'", (real_flag,))
        conn.commit()
        conn.close()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
