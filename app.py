"""
IT Self-Service Portal
-----------------------
A small Flask app that gives end users two things IT teams get asked for constantly:

  1. A searchable knowledge base of common troubleshooting steps.
  2. A self-service form to request a password reset or log another common issue,
     which creates a ticket in a local SQLite queue instead of an email/phone call.

This is a demo/personal project: it does not connect to a real Active Directory or
ticketing system, but the ticket queue, search, and status lookup are fully functional
so it can be run and clicked through end to end.

Run:
    pip install -r requirements.txt
    python app.py
    -> open http://127.0.0.1:5000
"""

import json
import random
import sqlite3
import string
from datetime import datetime
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "portal.db"
KB_PATH = BASE_DIR / "data" / "kb_articles.json"

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            request_type TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT,
            details TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def generate_ticket_id():
    return "TCK-" + "".join(random.choices(string.digits, k=6))


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

def load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    articles = load_kb()

    if query:
        articles = [
            a for a in articles
            if query in a["title"].lower() or query in a["category"].lower()
            or any(query in step.lower() for step in a["steps"])
        ]

    categories = sorted({a["category"] for a in load_kb()})
    return render_template("index.html", articles=articles, categories=categories, query=query)


@app.route("/article/<int:article_id>")
def article(article_id):
    articles = load_kb()
    match = next((a for a in articles if a["id"] == article_id), None)
    if not match:
        return redirect(url_for("index"))
    return render_template("kb_article.html", article=match)


@app.route("/request", methods=["GET", "POST"])
def request_form():
    if request.method == "POST":
        ticket_id = generate_ticket_id()
        db = get_db()
        db.execute(
            """INSERT INTO tickets (id, request_type, full_name, email, department, details, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)""",
            (
                ticket_id,
                request.form.get("request_type", "Other"),
                request.form.get("full_name", "").strip(),
                request.form.get("email", "").strip(),
                request.form.get("department", "").strip(),
                request.form.get("details", "").strip(),
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )
        db.commit()
        return redirect(url_for("confirmation", ticket_id=ticket_id))

    return render_template("request_form.html")


@app.route("/confirmation/<ticket_id>")
def confirmation(ticket_id):
    return render_template("confirmation.html", ticket_id=ticket_id)


@app.route("/status", methods=["GET", "POST"])
def status():
    ticket = None
    searched = False

    if request.method == "POST":
        searched = True
        ticket_id = request.form.get("ticket_id", "").strip().upper()
        db = get_db()
        row = db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row:
            ticket = dict(row)

    return render_template("ticket_status.html", ticket=ticket, searched=searched)


@app.route("/admin/tickets")
def admin_tickets():
    """Simple read-only queue view - what an IT tech would see on their side."""
    db = get_db()
    rows = db.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
    return render_template("admin_tickets.html", tickets=[dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    # Make sure the DB exists even when imported/run via a WSGI server
    init_db()
