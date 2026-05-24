# ============================================================
# SQLITE COMMANDS GUIDE
# ============================================================

## 1. INITIALIZE DATABASE
================================
# Run this once to create the database and tables:
python init_db.py

# Or manually in SQLite CLI:
sqlite3 notes_db.db
.schema


## 2. OPEN SQLITE DATABASE IN CLI
================================
sqlite3 notes_db.db

# Exit SQLite CLI:
.quit  or  .exit  or  Ctrl+D


## 3. VIEW DATABASE STRUCTURE
================================
.schema                    # Show all tables and their structure
.schema users              # Show only users table structure
.schema notes              # Show only notes table structure
.tables                    # List all tables


## 4. USER OPERATIONS
================================

# View all users
SELECT * FROM users;

# Add a test user manually (not recommended - let Flask handle this)
INSERT INTO users (username, email, password) 
VALUES ('testuser', 'test@example.com', 'hashed_password_here');

# Update a user's email
UPDATE users SET email = 'newemail@example.com' WHERE username = 'testuser';

# Delete a user (cascades to delete their notes)
DELETE FROM users WHERE username = 'testuser';

# Find user by email
SELECT * FROM users WHERE email = 'user@example.com';


## 5. NOTES OPERATIONS
================================

# View all notes
SELECT * FROM notes;

# View notes for a specific user (user_id = 1)
SELECT * FROM notes WHERE user_id = 1 ORDER BY created_at DESC;

# Search notes by title or content
SELECT * FROM notes WHERE title LIKE '%Flask%' OR content LIKE '%Flask%';

# View a specific note
SELECT * FROM notes WHERE id = 1 AND user_id = 1;

# Count notes per user
SELECT user_id, COUNT(*) as note_count FROM notes GROUP BY user_id;

# Delete a note
DELETE FROM notes WHERE id = 1 AND user_id = 1;

# Delete all notes from a user
DELETE FROM notes WHERE user_id = 1;


## 6. USEFUL SQLITE COMMANDS
================================

# Show table row count
SELECT COUNT(*) as total_rows FROM users;
SELECT COUNT(*) as total_rows FROM notes;

# Display results in column format
.mode column
.headers on

# Display results as CSV
.mode csv

# Export data to CSV
.output users.csv
SELECT * FROM users;
.output stdout

# Import data from SQL file
.read backup.sql

# Backup database
.dump > backup.sql

# Show query execution time
.timer on

# Show all SQLite settings
.show


## 7. COMMON QUERIES
================================

# Get all users and their note count
SELECT u.id, u.username, u.email, COUNT(n.id) as note_count
FROM users u
LEFT JOIN notes n ON u.id = n.user_id
GROUP BY u.id, u.username, u.email;

# Get recent notes (last 7 days)
SELECT * FROM notes 
WHERE created_at >= datetime('now', '-7 days')
ORDER BY created_at DESC;

# Get user info with most notes
SELECT u.username, COUNT(n.id) as note_count
FROM users u
LEFT JOIN notes n ON u.id = n.user_id
GROUP BY u.id, u.username
ORDER BY note_count DESC
LIMIT 1;


## 8. BACKUP & RESTORE
================================

# Backup entire database
sqlite3 notes_db.db ".dump" > notes_backup.sql

# Restore from backup
sqlite3 notes_db.db < notes_backup.sql

# Copy database file
cp notes_db.db notes_db_backup.db


## 9. TROUBLESHOOTING
================================

# Check if database is corrupted
PRAGMA integrity_check;

# Optimize database (reclaim space)
VACUUM;

# Get database info
PRAGMA database_list;

# Get table info
PRAGMA table_info(users);
PRAGMA table_info(notes);

# Rebuild indices
REINDEX;


## 10. KEY DIFFERENCES FROM MYSQL → SQLITE
================================

MySQL                          SQLite
-------------------------------------------
%s (placeholder)               ? (placeholder)
mysql.connector.connect()      sqlite3.connect()
AUTO_INCREMENT                 AUTOINCREMENT
DEFAULT CURRENT_TIMESTAMP      DEFAULT CURRENT_TIMESTAMP (same!)
UNIQUE constraint              UNIQUE constraint (same!)
Foreign Keys                   PRAGMA foreign_keys=ON (enable manually if needed)


## 11. FLASK APP SETUP
================================

# Create virtual environment (if not done)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies (updated for SQLite)
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run Flask app
python app.py

# App will run at http://127.0.0.1:5000


## 12. QUICK START
================================

1. python -m venv venv
2. .\venv\Scripts\activate
3. pip install -r requirements.txt
4. python init_db.py
5. python app.py
6. Open browser: http://localhost:5000
