"""
database.py - SQLite database layer for the CCSU Lost & Found application.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lost_and_found.db")

CATEGORIES = ["Electronics", "Keys", "Clothing", "Bags", "Books", "ID/Card", "Other"]
LOCATIONS = [
    "Student Center", "Library", "Rec Center", "Science Hall",
    "Willard Hall", "Vance Academic Center", "Copernicus Hall",
    "Parking Lot A", "Parking Lot B", "Other"
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist and seed sample data."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT    NOT NULL CHECK(report_type IN ('Lost', 'Found')),
            item_name   TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT,
            location    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            image_path  TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Seed sample data on first run
    c.execute("SELECT COUNT(*) FROM reports")
    if c.fetchone()[0] == 0:
        sample = [
            ("Lost",  "Black Wallet",    "ID/Card",     "Thin leather wallet, has student ID inside.",      "Student Center", "2026-04-01", None),
            ("Found", "Leather Wallet",  "ID/Card",     "Brown leather wallet found near study tables.",     "Library",        "2026-03-30", None),
            ("Found", "Wallet/ID Card",  "ID/Card",     "Blue wallet with CCSU ID card visible.",            "Rec Center",     "2026-03-28", None),
            ("Lost",  "Blue Backpack",   "Bags",        "Blue Jansport backpack with laptop inside.",        "Willard Hall",   "2026-04-05", None),
            ("Found", "AirPods Case",    "Electronics", "White AirPods Pro case, no earbuds inside.",        "Library",        "2026-04-06", None),
            ("Lost",  "Car Keys",        "Keys",        "Toyota key fob with small red keychain.",           "Parking Lot A",  "2026-04-07", None),
        ]
        c.executemany(
            "INSERT INTO reports (report_type,item_name,category,description,location,date,image_path) VALUES (?,?,?,?,?,?,?)",
            sample
        )
        conn.commit()
    conn.close()


def insert_report(report_type, item_name, category, description, location, date, image_path=None):
    """Insert a new lost/found report. Returns the new row id."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO reports (report_type,item_name,category,description,location,date,image_path) VALUES (?,?,?,?,?,?,?)",
        (report_type, item_name, category, description, location, date, image_path)
    )
    conn.commit()
    row_id = c.lastrowid
    conn.close()
    return row_id


def search_reports(keyword="", report_type=None):
    """Search reports by keyword in name/description. Optionally filter by type."""
    conn = get_connection()
    c = conn.cursor()
    kw = f"%{keyword}%"
    if report_type:
        c.execute(
            """SELECT * FROM reports
               WHERE report_type = ?
                 AND (item_name LIKE ? OR description LIKE ? OR category LIKE ? OR location LIKE ?)
               ORDER BY date DESC""",
            (report_type, kw, kw, kw, kw)
        )
    else:
        c.execute(
            """SELECT * FROM reports
               WHERE item_name LIKE ? OR description LIKE ? OR category LIKE ? OR location LIKE ?
               ORDER BY date DESC""",
            (kw, kw, kw, kw)
        )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_reports(report_type=None):
    """Return all reports, optionally filtered by type."""
    conn = get_connection()
    c = conn.cursor()
    if report_type:
        c.execute("SELECT * FROM reports WHERE report_type=? ORDER BY date DESC", (report_type,))
    else:
        c.execute("SELECT * FROM reports ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_opposite_reports(report_type):
    """Return reports of the opposite type (for AI matching)."""
    opposite = "Found" if report_type == "Lost" else "Lost"
    return get_all_reports(opposite)


def get_report_by_id(report_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE id=?", (report_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
