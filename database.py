import sqlite3
import hashlib
import os
import json

# ---------- Database Configuration ----------
DB_NAME = "/tmp/users.db"  # ✅ Store in /tmp to avoid write issues on Streamlit Cloud


# ---------- Database Connection ----------
def get_db_connection():
    """Creates a persistent database connection."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn


# ---------- Create Tables ----------
def initialize_db():
    """Creates necessary tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

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
    conn.close()


# ---------- Safe Column Addition ----------
def add_salt_column():
    """Adds the 'salt' column to 'users' if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users);")
    columns = {column[1] for column in cursor.fetchall()}  # Set for fast lookup

    if "salt" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT;")
        conn.commit()
        print("✅ 'salt' column added successfully!")
    else:
        print("⚠ 'salt' column already exists.")

    conn.close()


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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_data(query, params=()):
    """Fetches data from the database and returns it as a list of dictionaries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = [dict(row) for row in cursor.fetchall()]  # Convert to dictionary format
    conn.close()
    return data


# ---------- Export Database to JSON ----------
def export_data_to_json(filename="/tmp/database_export.json"):
    """Exports both users and conversion history to a JSON file."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure tables exist before exporting
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone() is None:
        print("⚠ Error: 'users' table does not exist. Skipping export.")
        conn.close()
        return

    # Export users
    cursor.execute("SELECT id, username FROM users")  # Avoid exporting passwords for security
    users_data = [dict(row) for row in cursor.fetchall()]

    # Export conversion history
    cursor.execute("SELECT * FROM history")
    history_data = [dict(row) for row in cursor.fetchall()]

    conn.close()

    # Create a dictionary containing both users and history
    export_data = {
        "users": users_data,
        "history": history_data
    }

    # Save to JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=4)

    print(f"✅ Database exported successfully to {filename}!")


# ---------- Ensure Database is Ready ----------
initialize_db()  # ✅ Ensure tables exist
add_salt_column()  # ✅ Then check for missing columns

# Call export function **ONLY if the database exists**
if os.path.exists(DB_NAME):
    export_data_to_json()