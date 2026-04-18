from flask import Flask, render_template, request, session, redirect
import sqlite3
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

app = Flask(__name__)
app.secret_key = "secret"

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# ---------- TABLES ----------
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    email TEXT UNIQUE,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    issue_type TEXT,
    location TEXT,
    description TEXT,
    status TEXT
)
''')

conn.commit()

# ---------- AUTH ----------

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/send', methods=['POST'])
def send():
    email = request.form['email']

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        return render_template('already.html')

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['email'] = email

    return render_template('otp.html', otp=otp)

@app.route('/verify', methods=['POST'])
def verify():
    if request.form['otp'] == session.get('otp'):
        return render_template('password.html')
    return "Wrong OTP"

@app.route('/set_password', methods=['POST'])
def set_password():
    password = request.form['password']
    email = session.get('email')

    cursor.execute("INSERT INTO users VALUES (?, ?)", (email, password))
    conn.commit()

    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    if cursor.fetchone():
        session['email'] = email
        return redirect('/report')
    return "Invalid Login"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------- ISSUE ----------

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/submit_issue', methods=['POST'])
def submit_issue():
    issue_type = request.form['issue_type']

    # Handle "Others"
    if issue_type == "Others":
        issue_type = request.form['other_issue']

    cursor.execute(
        "INSERT INTO issues (email, issue_type, location, description, status) VALUES (?, ?, ?, ?, ?)",
        (
            session.get('email'),
            issue_type,
            request.form['location'],
            request.form['description'],
            "Pending"
        )
    )
    conn.commit()
    return redirect('/view_issues')

# ---------- ADMIN ----------

@app.route('/view_issues')
def view_issues():
    cursor.execute("""
    SELECT * FROM issues
    ORDER BY 
        CASE status
            WHEN 'Pending' THEN 1
            WHEN 'In Progress' THEN 2
            WHEN 'Resolved' THEN 3
        END
    """)
    data = cursor.fetchall()
    return render_template('view.html', data=data)

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    cursor.execute("UPDATE issues SET status=? WHERE id=?",
                   (request.form['status'], id))
    conn.commit()
    return redirect('/view_issues')

# ---------- DELETE (ONLY OWNER) ----------

@app.route('/delete_issue/<int:id>', methods=['POST'])
def delete_issue(id):
    cursor.execute("SELECT email FROM issues WHERE id=?", (id,))
    issue = cursor.fetchone()

    if issue and issue[0] == session.get('email'):
        cursor.execute("DELETE FROM issues WHERE id=?", (id,))
        conn.commit()

    return redirect('/view_issues')

# ---------- DASHBOARD ----------

@app.route('/dashboard')
def dashboard():
    cursor.execute("SELECT * FROM issues")
    data = cursor.fetchall()

    if not data:
        df = pd.DataFrame(columns=["id","email","type","location","desc","status"])
    else:
        df = pd.DataFrame(data, columns=["id","email","type","location","desc","status"])

    # PIE
    plt.figure(figsize=(6,6))
    if not df.empty:
        df['type'].value_counts().plot.pie(autopct='%1.1f%%')
    else:
        plt.text(0.5, 0.5, "No Data", ha='center')
    plt.ylabel("")
    plt.savefig("static/pie.png")
    plt.close()

    # BAR
    plt.figure(figsize=(6,6))
    if not df.empty:
        ax = sns.countplot(x='location', data=df)
        max_val = df['location'].value_counts().max()
    else:
        ax = plt.gca()
        max_val = 1

    step = 1 if max_val <= 5 else 5 if max_val <= 20 else 10
    ax.set_yticks(np.arange(0, max_val + step, step))
    plt.savefig("static/bar.png")
    plt.close()

    # LINE
    plt.figure(figsize=(6,6))
    if not df.empty:
        counts = range(1, len(df) + 1)
        plt.plot(counts)
        max_val = len(df)
    else:
        plt.plot([0])
        max_val = 1

    step = 1 if max_val <= 5 else 5 if max_val <= 20 else 10
    plt.yticks(np.arange(0, max_val + step, step))
    plt.savefig("static/line.png")
    plt.close()

    # INSIGHTS
    if not df.empty:
        most_common = df['type'].value_counts().idxmax()
        top_location = df['location'].value_counts().idxmax()
    else:
        most_common = "0"
        top_location = "0"

    return render_template(
        "dashboard.html",
        most_common=most_common,
        top_location=top_location
    )

# ---------- RUN ----------

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
