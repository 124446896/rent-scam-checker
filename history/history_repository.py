import sqlite3
from datetime import datetime


class HistoryRepository:
    """History database: saves the results of past checks in a SQLite file.

    Only the result is saved, never the advert text itself (privacy risk from D1).
    In the full design this would be a cloud database like Firestore.
    """

    def __init__(self, db_path="history.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS checks (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       risk_level TEXT NOT NULL,
                       warning_count INTEGER NOT NULL,
                       checked_at TEXT NOT NULL
                   )"""
            )

    def save(self, user_id, report):
        """Saves one check result for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO checks (user_id, risk_level, warning_count, checked_at) VALUES (?, ?, ?, ?)",
                (user_id, report["risk_level"], len(report["reasons"]), datetime.now().isoformat()),
            )

    def list(self, user_id):
        """Returns a user's past checks, newest first."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT risk_level, warning_count, checked_at FROM checks WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        return [{"risk_level": r[0], "warning_count": r[1], "checked_at": r[2]} for r in rows]