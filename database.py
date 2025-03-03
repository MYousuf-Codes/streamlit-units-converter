import sqlite3
import hashlib
import os
import json
import logging

# 🔹 Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 Define the database path (Absolute Path for Cross-Platform Compatibility)
DB_NAME = os.path.join(os.path.dirname(__file__), "users.db")  # ✅ Ensures correct path

# ---------- Database Connection ----------
def get_db_connection():
    """Creates and returns a database connection."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enables accessing columns by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"❌ Database connection error: {e}")
        return None


# ---------- Create Tables ----------
def initialize_db():
    """Creates necessary tables if they do not exist."""
    conn = get_db_connection()
    if not conn:
        logging.error("❌ Database connection failed. Skipping initialization.")
        return

    try:
        with conn:
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

            logging.info("✅ Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"❌ Database initialization error: {e}")
    finally:
        conn.close()


# ---------- Safe Column Addition ----------
def add_salt_column():
    """Adds the 'salt' column to 'users' if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        logging.error("❌ Database connection failed. Skipping column check.")
        return

    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users);")
            columns = {column[1] for column in cursor.fetchall()}  # Set for fast lookup

            if "salt" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT;")
                logging.info("✅ 'salt' column added successfully!")
            else:
                logging.info("⚠ 'salt' column already exists.")
    except sqlite3.Error as e:
        logging.error(f"❌ Error adding 'salt' column: {e}")
    finally:
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
    if not conn:
        return

    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
    except sqlite3.Error as e:
        logging.error(f"❌ Database query execution error: {e}")
    finally:
        conn.close()

def fetch_data(query, params=()):
    """Fetches data from the database and returns it as a list of dictionaries."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]  # Convert to dictionary format
    except sqlite3.Error as e:
        logging.error(f"❌ Error fetching data: {e}")
        return []
    finally:
        conn.close()


# ---------- Export Database to JSON ----------
def export_data_to_json(filename=None):
    """Exports both users and conversion history to a JSON file."""
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "database_export.json")  # ✅ Save in project folder

    conn = get_db_connection()
    if not conn:
        logging.error("❌ Database connection failed. Skipping export.")
        return

    try:
        with conn:
            cursor = conn.cursor()

            # Ensure tables exist before exporting
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if cursor.fetchone() is None:
                logging.warning("⚠ 'users' table does not exist. Skipping export.")
                return

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

            logging.info(f"✅ Database exported successfully to {filename}!")
    except sqlite3.Error as e:
        logging.error(f"❌ Error exporting database: {e}")
    finally:
        conn.close()


# ---------- Ensure Database is Ready ----------
if __name__ == "__main__":
    initialize_db()  # ✅ Ensure tables exist
    add_salt_column()  # ✅ Then check for missing columns

    # Call export function **ONLY if the database exists**
    if os.path.exists(DB_NAME):
        export_data_to_json()
