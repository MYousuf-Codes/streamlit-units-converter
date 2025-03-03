import sqlite3
import hashlib
import os
import json

DB_NAME = "users.db"


# ---------- Database Connection ----------
def get_db_connection():
    """Creates a persistent database connection."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn

conn = get_db_connection()
cursor = conn.cursor()


# ---------- Create Tables ----------
def initialize_db():
    """Creates necessary tables if they do not exist."""
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT UNIQUE, 
                        password TEXT,
                        salt TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        category TEXT,
                        conversion TEXT,
                        input_value REAL,
                        converted_value REAL)''')

    conn.commit()


# ---------- Safe Column Addition ----------
def add_salt_column():
    """Adds the 'salt' column to 'users' if it doesn't exist."""
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone() is None:
        print("⚠ Error: 'users' table does not exist. Run 'initialize_db()' first!")
        return

    cursor.execute("PRAGMA table_info(users);")
    columns = {column[1] for column in cursor.fetchall()}  # Set for faster lookup
    
    if "salt" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT;")
        conn.commit()
        print("✅ 'salt' column added successfully!")
    else:
        print("⚠ 'salt' column already exists.")


# ---------- Security Functions ----------
def generate_salt():
    """Generates a secure random salt."""
    return os.urandom(16).hex()  # 16-byte salt in hexadecimal

def hash_password(password, salt):
    """Hashes a password using SHA-256 and a salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


# ---------- Database Query Functions ----------
def execute_query(query, params=()):
    """Executes an SQL query with parameters and commits changes."""
    cursor.execute(query, params)
    conn.commit()

def fetch_data(query, params=()):
    """Fetches data from the database and returns it as a list of dictionaries."""
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]  # Converts to dictionary format


# ---------- Export Database to JSON ----------
def export_data_to_json(filename="database_export.json"):
    """Exports both users and conversion history to a JSON file."""
    
    # Export users
    cursor.execute("SELECT id, username FROM users")  # Avoid exporting passwords for security
    users_data = [dict(row) for row in cursor.fetchall()]

    # Export conversion history
    cursor.execute("SELECT * FROM history")
    history_data = [dict(row) for row in cursor.fetchall()]
    
    # Create a dictionary containing both users and history
    export_data = {
        "users": users_data,
        "history": history_data
    }

    # Save to JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=4)

    print(f"✅ Database exported successfully to {filename}!")


# Call the function to export
export_data_to_json()


# ---------- Ensure Database is Ready ----------
initialize_db()  # ✅ Ensure tables exist first
add_salt_column()  # ✅ Then check for the column
