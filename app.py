from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Dictionary to store usernames and passwords
users = {}

# Function to get the database path for a username
def get_db_path(username):
    return f'{username}.db'

# Function to initialize the database (create tasks and events tables if they don't exist)
def init_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          date TEXT NOT NULL,
                          event TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          description TEXT NOT NULL,
                          due_date TEXT NOT NULL)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            # Authenticate or register user
            if username in users:
                if users[username] == password:
                    session['username'] = username
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error="Invalid username or password")
            else:
                users[username] = password
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html', error=None)

# Route for the homepage
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    db_path = get_db_path(username)
    if not os.path.exists(db_path):
        init_db(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, date, event FROM events ORDER BY date')
        events = cursor.fetchall()

        cursor.execute('SELECT id, description, due_date FROM tasks ORDER BY due_date')
        tasks = cursor.fetchall()

        conn.close()
        return render_template('planner.html', tasks=tasks, events=events)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "Internal Server Error", 500

# Route to add a task
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return redirect(url_for('login'))

    task_description = request.form.get('task_description')
    due_date = request.form.get('due_date')
    if task_description and due_date:
        try:
            username = session['username']
            db_path = get_db_path(username)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (description, due_date) VALUES (?, ?)', (task_description, due_date))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error adding task: {e}")
            return "Internal Server Error", 500
    return redirect(url_for('index'))

# Route to delete a task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']
        db_path = get_db_path(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error deleting task: {e}")
        return "Internal Server Error", 500
    return redirect(url_for('index'))

# Route to add an event
@app.route('/add_event', methods=['POST'])
def add_event():
    if 'username' not in session:
        return redirect(url_for('login'))

    event_description = request.form.get('event_description')
    event_date = request.form.get('event_date')
    if event_description and event_date:
        try:
            username = session['username']
            db_path = get_db_path(username)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO events (date, event) VALUES (?, ?)', (event_date, event_description))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error adding event: {e}")
            return "Internal Server Error", 500
    return redirect(url_for('index'))

# Route to delete an event
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']
        db_path = get_db_path(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error deleting event: {e}")
        return "Internal Server Error", 500
    return redirect(url_for('index'))

# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
