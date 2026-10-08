import json
import sqlite3

DB_NAME = "medilens.db"


def init_db():
    """Initialize the database with the reports table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            extracted_text TEXT,
            summary TEXT,
            key_findings TEXT,
            analysis_data TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_report(filename, extracted_text, summary, key_findings, analysis_data):
    """Save a report to the database and return its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports (
            filename, extracted_text, summary, key_findings, analysis_data
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (filename, extracted_text, summary, key_findings, json.dumps(analysis_data)),
    )

    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id


def get_all_reports():
    """Get all saved reports, newest first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, filename, upload_date FROM reports ORDER BY upload_date DESC"
    )
    reports = cursor.fetchall()
    conn.close()
    return reports


def get_report_by_id(report_id):
    """Get a specific report by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report = cursor.fetchone()
    conn.close()
    return report


def delete_report(report_id):
    """Delete a report."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
