# ============================================================
# ERROR CHECKLIST & SETUP GUIDE
# ============================================================

## ERRORS FOUND & FIXED ✅

### 1. **Database Connection Issue**
   - **Problem**: SQLite database file didn't exist
   - **Fix**: Run `init_db.py` to create it
   - **Status**: ✅ FIXED

### 2. **Row Object Access Issue** 
   - **Problem**: SQLite Row factory caused templates to fail
   - **Fix**: Removed `row_factory` to use regular tuples
   - **Status**: ✅ FIXED

### 3. **Login Function Logic**
   - **Problem**: Overly complex row handling
   - **Fix**: Simplified to use tuple indexing (user[0], user[1], user[3])
   - **Status**: ✅ FIXED


## STEP-BY-STEP SETUP & TESTING
================================

### STEP 1: Activate Virtual Environment
```powershell
cd "C:\Users\dosap\OneDrive\Desktop\Flask Project-2"
.\venv\Scripts\activate
```

### STEP 2: Install Dependencies
```powershell
pip install -r requirements.txt
```
✓ Installs: Flask, Flask-Mail, Werkzeug, etc. (NO mysql-connector needed)


### STEP 3: Initialize Database
```powershell
python init_db.py
```
✓ Creates `notes_db.db` file
✓ Creates `users` table
✓ Creates `notes` table
✓ Output: "✅ Database initialized successfully! Created 'notes_db.db'"


### STEP 4: Run Flask App
```powershell
python app.py
```
✓ Should see:
  - "Running on http://127.0.0.1:5000"
  - "WARNING in werkzeug... (this is normal)"
  - "Press CTRL+C to quit"


### STEP 5: Test Registration
1. Open browser: http://localhost:5000
2. Click "Register"
3. Fill form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test123!`
4. Click Register button

✓ Should see green popup: "Account created successfully!"
✓ Should redirect to Login page


### STEP 6: Test Login (THE KEY STEP)
1. In login page, enter:
   - Username: `testuser`
   - Password: `Test123!`
2. Click Login

Expected Results:
✓ Green popup: "Welcome back, testuser! 👋"
✓ Redirects to Dashboard page
✓ Shows "My Notes" page (empty, but should load)


### STEP 7: Test Add Note
1. Click "Add New Note" button
2. Fill form:
   - Title: `First Note`
   - Content: `This is my first note`
3. Click Save

✓ Should see: "Note added successfully! ✅"
✓ Should show note on dashboard


### STEP 8: Test View/Edit/Delete
- Click "View" → should open note
- Click "Edit" → should edit note
- Click "Delete" → should delete note


## COMMON ERRORS & FIXES
================================

### Error 1: "DatabaseError: unable to open database file"
**Cause**: Database file doesn't exist
**Fix**: 
```powershell
python init_db.py
```

### Error 2: "Incorrect username or password"
**Cause**: Wrong credentials OR database is empty
**Fix**: 
- Register a new account first
- Make sure you used exact username/password

### Error 3: "No module named 'mysql'"
**Cause**: Old requirements still installed
**Fix**:
```powershell
pip uninstall mysql-connector-python -y
pip install -r requirements.txt
```

### Error 4: "OperationalError: no such table: users"
**Cause**: init_db.py wasn't run
**Fix**:
```powershell
python init_db.py
```

### Error 5: "TypeError: 'NoneType' object is not subscriptable"
**Cause**: User not found in database
**Fix**: Register an account first

### Error 6: "KeyError: 'user_id'"
**Cause**: Session variable missing
**Fix**: Login before accessing dashboard

### Error 7: "Flask app not starting"
**Cause**: Port 5000 in use OR syntax error
**Fix**:
```powershell
# Kill process using port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port
python app.py --port 5001
```


## DATABASE INSPECTION
================================

### Check if database exists
```powershell
Test-Path "notes_db.db"
# Returns: True or False
```

### View all users
```powershell
sqlite3 notes_db.db "SELECT * FROM users;"
```

### View all notes
```powershell
sqlite3 notes_db.db "SELECT * FROM notes;"
```

### Delete database and restart (NUCLEAR OPTION)
```powershell
Remove-Item notes_db.db
python init_db.py
```


## FILES CHANGED
================================
✅ app.py → SQLite integration + login fix
✅ requirements.txt → Removed mysql-connector-python
✅ init_db.py → NEW - Database initialization
✅ SQLITE_COMMANDS.md → NEW - Reference guide


## VERIFICATION CHECKLIST
================================

Before running, verify:

□ Virtual environment activated (you see (venv) in terminal)
□ requirements.txt installed (pip list should show Flask, Flask-Mail, etc.)
□ init_db.py has been run (notes_db.db file exists)
□ app.py has no syntax errors
□ All templates exist in templates/ folder
□ Port 5000 is not in use

If all checked ✓, your app should work!


## NEXT STEPS AFTER LOGIN WORKS
================================

1. ✅ Test all CRUD operations (Create, Read, Update, Delete notes)
2. ✅ Test Search functionality on dashboard
3. ✅ Test Forgot Password (requires mail config - see app.py line 41-45)
4. ✅ Test Logout

That's it! Your Flask app is now running on SQLite! 🎉
