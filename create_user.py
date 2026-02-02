#!/usr/bin/env python3
"""
Script to create a new admin user
"""
import sqlite3
import hashlib
import os
import sys

# Database path (adjust if needed)
db_path = os.getenv('DATABASE_PATH', 'documents_calendar.db')

# User credentials (set via environment variables or edit here)
username = os.getenv('NEW_ADMIN_USERNAME', 'admin')
password = os.getenv('NEW_ADMIN_PASSWORD', 'changeme')

# Create password hash (using sha256 format that the app supports)
password_hash = hashlib.sha256(password.encode()).hexdigest()
hashed_password = f"sha256${password_hash}"

# Connect to database
try:
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
    
    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if user:
        # Update existing user
        cursor.execute('''
            UPDATE users 
            SET hashed_password = ? 
            WHERE username = ?
        ''', (hashed_password, username))
        print(f"Updated user password: {username}")
    else:
        # Create new user
        cursor.execute('''
            INSERT INTO users (username, hashed_password)
            VALUES (?, ?)
        ''', (username, hashed_password))
        print(f"Created new user: {username}")
    
    conn.commit()
    conn.close()
    
    print(f"Done! Login with: {username} / {password}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

