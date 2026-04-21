from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secretkey"


# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bhairesh123@",
    database="attendance_db"
)

cursor = conn.cursor()


# Home Page
@app.route('/')
def home():
    return render_template("login.html")


# Login
@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        return "Invalid Login"


# Dashboard
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    return render_template("dashboard.html")


# Attendance Page
@app.route('/attendance')
def attendance():

    if 'user' not in session:
        return redirect('/')

    cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
    records = cursor.fetchall()

    return render_template("attendance.html", records=records)


# Logout
@app.route('/logout')
def logout():

    session.pop('user', None)
    return redirect('/')


# Run Flask
if __name__ == "__main__":
    app.run(debug=True, port=8000)