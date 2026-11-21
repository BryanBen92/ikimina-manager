import sqlite3

DB_FILE = "ikimina.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                date_joined TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                contribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL REFERENCES members(member_id),
                amount REAL NOT NULL,
                contribution_date TEXT NOT NULL
            )
        """)
