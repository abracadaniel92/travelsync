"""
Simple script to set admin password to test123
"""
import sqlite3
import hashlib
import os

db_path = os.path.join(os.path.dirname(__file__), 'documents_calendar.db')

# Create simple hash
password = 'test123'
password_hash = hashlib.sha256(password.encode()).hexdigest()
hashed_password = f"sha256${password_hash}"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR UNIQUE,
        hashed_password VARCHAR
    )
''')

# Check if admin user exists
cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()

if user:
    # Update existing user
    cursor.execute('''
        UPDATE users 
        SET hashed_password = ? 
        WHERE username = ?
    ''', (hashed_password, 'admin'))
    print("Updated admin password to: test123")
else:
    # Create new user
    cursor.execute('''
        INSERT INTO users (username, hashed_password)
        VALUES (?, ?)
    ''', ('admin', hashed_password))
    print("Created admin user with password: test123")

conn.commit()
conn.close()

print("Done! Login with: admin / test123")



