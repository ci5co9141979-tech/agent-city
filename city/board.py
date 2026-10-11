"""Shared state for the city: a task board and a message log, backed by SQLite.

Every agent talks through here, so the whole conversation is inspectable
(and rendered by dashboard.py).
"""
import json
import sqlite3
import time
from pathlib import Path


class Board:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              category TEXT, title TEXT, role TEXT,
              status TEXT DEFAULT 'open',   -- open | doing | done | failed
              depends_on INTEGER,
              result TEXT, created REAL, updated REAL);
            CREATE TABLE IF NOT EXISTS messages(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts REAL, sender TEXT, recipient TEXT, category TEXT, body TEXT);
            CREATE TABLE IF NOT EXISTS memory(
              key TEXT PRIMARY KEY, value TEXT);
            """
        )

    # ---- tasks
    def add_task(self, category, title, role, depends_on=None):
        now = time.time()
        cur = self.db.execute(
            "INSERT INTO tasks(category,title,role,depends_on,created,updated) VALUES(?,?,?,?,?,?)",
            (category, title, role, depends_on, now, now),
        )
        self.db.commit()
        return cur.lastrowid

    def next_task(self, role):
        """Oldest open task for this role whose dependency (if any) is done."""
        row = self.db.execute(
            """SELECT t.* FROM tasks t LEFT JOIN tasks d ON d.id = t.depends_on
               WHERE t.role=? AND t.status='open' AND (t.depends_on IS NULL OR d.status='done')
               ORDER BY t.id LIMIT 1""",
            (role,),
        ).fetchone()
        return row

    def set_status(self, task_id, status, result=None):
        self.db.execute(
            "UPDATE tasks SET status=?, result=COALESCE(?,result), updated=? WHERE id=?",
            (status, result, time.time(), task_id),
        )
        self.db.commit()

    def tasks(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM tasks ORDER BY id")]

    def pending(self):
        return self.db.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN ('open','doing')"
        ).fetchone()[0]

    # ---- messages
    def say(self, sender, recipient, category, body):
        self.db.execute(
            "INSERT INTO messages(ts,sender,recipient,category,body) VALUES(?,?,?,?,?)",
            (time.time(), sender, recipient, category, body),
        )
        self.db.commit()
        print(f"[{sender} -> {recipient}] ({category}) {body[:140]}")

    def messages(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM messages ORDER BY id")]

    def inbox(self, recipient, category=None):
        q = "SELECT * FROM messages WHERE recipient IN (?, 'all')"
        args = [recipient]
        if category:
            q += " AND category=?"
            args.append(category)
        return [dict(r) for r in self.db.execute(q + " ORDER BY id", args)]

    # ---- shared memory (facts the agents hand to each other)
    def remember(self, key, value):
        self.db.execute(
            "INSERT INTO memory(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value)),
        )
        self.db.commit()

    def recall(self, key, default=None):
        row = self.db.execute("SELECT value FROM memory WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default
