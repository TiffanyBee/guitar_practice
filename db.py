import sqlite3
from contextlib import closing
DB_PATH = "practice.db"


def get_connection():
    conn = sqlite3.connect("practice.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            length REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL REFERENCES sessions(id),
            name TEXT NOT NULL,
            duration REAL NOT NULL
        )
    """)
    return conn

def save_session(date, length, songs):
    # songs is a list of (name,duration) tupples
    
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute (
                "INSERT INTO sessions (date, length) VALUES (?, ?)",
                (str(date), length)
            )
            session_id = cursor.lastrowid
            for song in songs:
                cursor.execute (
                    "INSERT INTO songs (session_id, name, duration) VALUES (?, ?, ?)",
                    (session_id, song[0], song[1])
                )

def load_sessions():
    with closing(get_connection()) as conn:
        sessions = conn.execute(
            "SELECT id, date, length From sessions ORDER BY id"
        ).fetchall()
        result = []
        for session_id, date, length in sessions:
            song = conn.execute(
                  "SELECT name, duration FROM songs WHERE session_id = ?",
                (session_id,),
            ).fetchall()
            result.append({"id": session_id, "date": date, "length": length, "songs": song})
        return result
        