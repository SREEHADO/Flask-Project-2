# ============================================================
# app.py — Flask Notes Management System
# ============================================================
# Flask     → web framework (handles routes, requests, responses)
# session   → stores user login state in browser cookie
# flash     → sends one-time messages (shown as popups)
# url_for   → generates URLs for routes by function name
# ============================================================

from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import sqlite3


# ── App Setup ────────────────────────────────────────────────
app = Flask(__name__)

# secret_key: required for sessions and flash messages to work
# In production, use a long random string and store in environment variable
app.secret_key = "notes_super_secret_key_2024"


# ── Database Connection ───────────────────────────────────────
# This function is called every time we need to talk to SQLite.
# We don't keep a permanent connection open — we open, use, close.
def get_db():
    con = sqlite3.connect("notes_db.db")
    return con


# ── Mail Configuration ────────────────────────────────────────
# Used for sending password reset emails via Gmail SMTP
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587      # TLS port
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'     # ← Change this
app.config['MAIL_PASSWORD'] = 'your_app_password_here'   # ← Gmail App Password

mail = Mail(app)

# Serializer for generating secure tokens (used in password reset links)
s = URLSafeTimedSerializer(app.secret_key)


# ╔══════════════════════════════════════════════════════════╗
# ║                    USER MODULE                           ║
# ╚══════════════════════════════════════════════════════════╝

# ── REGISTER ─────────────────────────────────────────────────
# GET  → show the registration form
# POST → receive form data, validate, save to DB
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()   # .strip() removes extra spaces
        email    = request.form["email"].strip()
        password = request.form["password"]

        # generate_password_hash() converts "mypassword" → "pbkdf2:sha256:..."
        # We NEVER store plain text passwords
        hashed_pwd = generate_password_hash(password)

        con = get_db()
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pwd)
            )
            con.commit()
            # "success" → green toast popup
            flash("Account created successfully! Please login.", "success")
            return redirect("/login")

        except sqlite3.IntegrityError:
            # IntegrityError fires when UNIQUE constraint is violated
            # (username or email already exists)
            flash("Username or email already exists. Try a different one.", "danger")
            return redirect("/register")
        finally:
            con.close()   # Always close DB connection

    return render_template("register.html")


# ── LOGIN ─────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def login():
    # If already logged in, skip the login page
    if "user_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()   # Returns tuple: (id, username, email, password)
        con.close()

        # check_password_hash() compares the plain password with the stored hash
        if user and check_password_hash(user[3], password):
            # Store user info in session (like a login ticket in the browser)
            session["user_id"]   = user[0]   # user[0] = id column
            session["username"]  = user[1]   # user[1] = username column
            flash(f"Welcome back, {user[1]}! 👋", "success")
            return redirect("/dashboard")
        else:
            flash("Incorrect username or password. Please try again.", "danger")
            return redirect("/login")

    return render_template("login.html")


# ── LOGOUT ────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    username = session.get("username", "")
    session.clear()   # Destroys the login session
    flash(f"Goodbye, {username}! You have been logged out.", "info")
    return redirect("/login")


# ── FORGOT PASSWORD ───────────────────────────────────────────
@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip()

        # Check if email exists in DB first
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        con.close()

        if not user:
            flash("No account found with that email address.", "danger")
            return redirect("/forgot")

        # Generate a secure, time-limited token containing the email
        token = s.dumps(email, salt="password-reset-salt")
        reset_url = url_for("reset_password", token=token, _external=True)

        msg = Message(
            "Notes App — Password Reset",
            sender="your_email@gmail.com",
            recipients=[email]
        )
        msg.body = f"""
Hello!

You requested a password reset for your Notes App account.

Click the link below to reset your password (valid for 10 minutes):
{reset_url}

If you did not request this, please ignore this email.
"""
        mail.send(msg)
        flash("Password reset link sent! Check your email inbox.", "success")
        return redirect("/forgot")

    return render_template("forgot.html")


# ── RESET PASSWORD ────────────────────────────────────────────
@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        # Decode the token and check it's not older than 600 seconds (10 min)
        email = s.loads(token, salt="password-reset-salt", max_age=600)
    except SignatureExpired:
        flash("The reset link has expired. Please request a new one.", "danger")
        return redirect("/forgot")
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect("/forgot")

    if request.method == "POST":
        new_password = generate_password_hash(request.form["password"])
        con = get_db()
        cur = con.cursor()
        cur.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        con.commit()
        con.close()
        flash("Password updated successfully! Please login with your new password.", "success")
        return redirect("/login")

    return render_template("reset_password.html")


# ╔══════════════════════════════════════════════════════════╗
# ║                    NOTES MODULE                          ║
# ╚══════════════════════════════════════════════════════════╝

# Helper decorator concept — we check session manually each route
# If "user_id" not in session → user is not logged in → redirect to login

# ── DASHBOARD (View All Notes) ────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login to access your notes.", "warning")
        return redirect("/login")

    search_query = request.args.get("search", "").strip()
    
    con = get_db()
    cur = con.cursor()
    
    if search_query:
        # Search notes by title or content containing the search term
        cur.execute(
            "SELECT * FROM notes WHERE user_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY created_at DESC",
            (session["user_id"], f"%{search_query}%", f"%{search_query}%")
        )
    else:
        # Only fetch notes belonging to the logged-in user (user_id = session user)
        # ORDER BY created_at DESC → newest notes appear first
        cur.execute(
            "SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC",
            (session["user_id"],)
        )
    
    notes = cur.fetchall()   # Returns list of tuples: [(id, title, content, created_at, user_id), ...]
    con.close()

    return render_template("dashboard.html", notes=notes, search_query=search_query)


# ── ADD NOTE ──────────────────────────────────────────────────
@app.route("/addnote", methods=["GET", "POST"])
def add_note():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title   = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            flash("Title and content cannot be empty.", "warning")
            return redirect("/addnote")

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO notes (title, content, user_id) VALUES (?, ?, ?)",
            (title, content, session["user_id"])
            # created_at is auto-filled by SQLite DEFAULT CURRENT_TIMESTAMP
        )
        con.commit()
        con.close()
        flash("Note added successfully! ✅", "success")
        return redirect("/dashboard")

    return render_template("add_note.html")


# ── VIEW SINGLE NOTE ──────────────────────────────────────────
@app.route("/viewnote/<int:note_id>")
def view_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()
    # WHERE user_id = session["user_id"] prevents one user from seeing another's note
    cur.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    note = cur.fetchone()
    con.close()

    if not note:
        flash("Note not found or access denied.", "danger")
        return redirect("/dashboard")

    return render_template("view_note.html", note=note)


# ── EDIT NOTE ─────────────────────────────────────────────────
@app.route("/editnote/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        title   = request.form["title"].strip()
        content = request.form["content"].strip()

        cur.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ? AND user_id = ?",
            (title, content, note_id, session["user_id"])
        )
        con.commit()
        con.close()
        flash("Note updated successfully! ✏️", "success")
        return redirect("/dashboard")

    # GET → load existing note data into the form
    cur.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    note = cur.fetchone()
    con.close()

    if not note:
        flash("Note not found.", "danger")
        return redirect("/dashboard")

    return render_template("edit_note.html", note=note)


# ── DELETE NOTE ───────────────────────────────────────────────
@app.route("/deletenote/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()
    # AND user_id check ensures users can only delete THEIR OWN notes
    cur.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    con.commit()
    con.close()
    flash("Note deleted successfully! 🗑️", "success")
    return redirect("/dashboard")


# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
    # debug=True → auto-reloads when you save changes
    # NEVER use debug=True in production (live website)