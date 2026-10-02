import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = 'tracking.db'


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    _init_schema(conn)
    return conn


def _init_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions(
             session_id TEXT PRIMARY KEY,
             source TEXT,
             started_at TEXT,
             ended_at TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             session_id TEXT,
             tag_id INTEGER,
             timestamp REAL,
             angle REAL,
             radius REAL,
             rpm REAL,
             FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_readings_session
        ON readings(session_id)
        """
    )

    conn.commit()
     

def start_session(conn, source):
    session_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        "INSERT INTO sessions (session_id, source, started_at, ended_at) VALUES (?, ?, ?, NULL)",
        (session_id, source, started_at),
    )

    conn.commit()
    return session_id


def end_session(conn, session_id):
    ended_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE sessions SET ended_at = ? WHERE session_id = ?",
        (ended_at, session_id),
    )

    conn.commit()


def log_reading(conn, session_id, tag_id, timestamp, angle, radius, rpm):
    conn.execute(
        "INSERT INTO readings (session_id, tag_id, timestamp, angle, radius, rpm) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, tag_id, timestamp, angle, radius, rpm),
    )

def commit(conn):
     conn.commit()

def get_sessions(conn):
    curr = conn.execute(
        "SELECT session_id, source, started_at, ended_at FROM sessions ORDER BY started_at DESC"
    )
    return curr.fetchall()


def get_readings_for_session(conn, session_id):
    curr = conn.execute(
        "SELECT tag_id, timestamp, angle, radius, rpm FROM readings WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,),
    )
    return curr.fetchall()

