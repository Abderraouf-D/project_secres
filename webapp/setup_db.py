import sqlite3
import os
from hashlib import sha256

# Define the user data
users = {
    "admin": ("admin", "admin@admin.local", sha256(os.environ.get('ADMIN_PASSWORD').encode()).hexdigest(), 1),
}
DB_FILE = "nexus.db"

def init_db():
    """Initialize the SQLite database and create tables."""
    if os.path.exists(DB_FILE):
        print(f"{DB_FILE} already exists. Skipping initialization.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()

        # Insert the user data
        cursor.executemany('''
            INSERT OR REPLACE INTO users (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', users.values())

        conn.commit()

        # Create posts table
        cursor.execute('''
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Add an insert of an admin post containing a flag
        cursor.execute(
            "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ("About", "Hi, My name is Andy", 1)
        )
        cursor.execute(
            "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
            ("Flag", "SecRes{1st_flag_ssti_leaked}", 1)
        )

        conn.commit()

         # Create the 'flags' table for storing flags (2nd flag table)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag TEXT NOT NULL
            )
        """)

        # Insert the 2nd flag into the 'flags' table
        cursor.execute("""
            INSERT INTO flags (flag) VALUES ('SecRes{2nd_flag_sql_dumped}')
        """)

        # Commit the changes to the database
        conn.commit()

        print(f"Databases initialized and {DB_FILE} created successfully.")

if __name__ == "__main__":
    init_db()

