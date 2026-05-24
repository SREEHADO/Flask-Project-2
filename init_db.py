# ============================================================
# init_db.py — SQLite Database Initialization Script
# ============================================================
# Run this script once to create the SQLite database and tables

import sqlite3

def init_db():
    # Connect to SQLite database (creates it if doesn't exist)
    con = sqlite3.connect("notes_db.db")
    cur = con.cursor()
    
    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Create notes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    con.commit()
    con.close()
    print("✅ Database initialized successfully! Created 'notes_db.db'")

if __name__ == "__main__":
    init_db()
