import sqlite3
import random
import smtplib

# Initialize Database
conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS limits (
                    user_id INTEGER,
                    account_limit INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

conn.commit()

# Register User Function
def register_user(username, email, password):
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute('INSERT INTO limits (user_id, account_limit) VALUES (?, ?)', (user_id, 5))  # Default limit
        conn.commit()
        print(f"User {username} registered successfully!")
    except sqlite3.IntegrityError:
        print("Username or email already exists!")

# Generate Account Function
def generate_account(username):
    cursor.execute('SELECT id, account_limit FROM users JOIN limits ON users.id = limits.user_id WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if user and user[1] > 0:
        with open('hits.txt', 'r') as file:
            hits = file.readlines()
        if hits:
            hit = random.choice(hits).strip()
            email, password = hit.split(':')
            print(f"Generated Account - Email: {email}, Password: {password}")
            cursor.execute('UPDATE limits SET account_limit = account_limit - 1 WHERE user_id = ?', (user[0],))
            conn.commit()
        else:
            print("No hits available in hits.txt")
    else:
        print("Account generation limit reached or user not found!")

# Broadcast Message Function
def broadcast_message(message):
    cursor.execute('SELECT email FROM users')
    users = cursor.fetchall()
    for user in users:
        send_email(user[0], message)

# Send Email Function
def send_email(to_email, message):
    from_email = 'your-email@example.com'
    password = 'your-email-password'
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, message)
    server.quit()

# Example Usage
register_user('user1', 'user1@example.com', 'password1')
generate_account('user1')
broadcast_message('This is a broadcast message to all users.')
