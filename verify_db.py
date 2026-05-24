import sqlite3

con = sqlite3.connect("notes_db.db")
cur = con.cursor()

# Check tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("✅ Tables found:", [t[0] for t in tables])

# Check users table structure
cur.execute("PRAGMA table_info(users)")
users_cols = cur.fetchall()
print("\n📋 Users table columns:")
for col in users_cols:
    print(f"   - {col[1]} ({col[2]})")

# Check notes table structure
cur.execute("PRAGMA table_info(notes)")
notes_cols = cur.fetchall()
print("\n📝 Notes table columns:")
for col in notes_cols:
    print(f"   - {col[1]} ({col[2]})")

con.close()
print("\n✅ Database ready to use!")
