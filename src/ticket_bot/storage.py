import sqlite3
import time
from typing import Optional, List, Dict, Any
from .models import Event, Ticket


class TicketStorage:
    """Tadbirlar va chiptalarni SQLite bazasida saqlash."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    capacity INTEGER NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    attendee_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    is_used INTEGER DEFAULT 0,
                    used_at REAL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES events(id)
                )
                """
            )

    def save_event(self, event: Event):
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO events (id, title, date_str, venue, capacity) VALUES (?, ?, ?, ?, ?)",
                (event.id, event.title, event.date_str, event.venue, event.capacity),
            )

    def get_event(self, event_id: str) -> Optional[Event]:
        cur = self._conn.cursor()
        cur.execute("SELECT id, title, date_str, venue, capacity FROM events WHERE id = ?", (event_id,))
        row = cur.fetchone()
        if not row:
            return None
        return Event(*row)

    def save_ticket(self, ticket: Ticket):
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO tickets (id, event_id, attendee_name, phone, token, is_used, used_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.id,
                    ticket.event_id,
                    ticket.attendee_name,
                    ticket.phone,
                    ticket.token,
                    1 if ticket.is_used else 0,
                    ticket.used_at,
                    ticket.created_at,
                ),
            )

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT id, event_id, attendee_name, phone, token, is_used, used_at, created_at FROM tickets WHERE id = ?",
            (ticket_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return Ticket(row[0], row[1], row[2], row[3], row[4], bool(row[5]), row[6], row[7])

    def count_event_tickets(self, event_id: str) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tickets WHERE event_id = ?", (event_id,))
        return cur.fetchone()[0]

    def mark_ticket_used(self, ticket_id: str) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "UPDATE tickets SET is_used = 1, used_at = ? WHERE id = ? AND is_used = 0",
                (time.time(), ticket_id),
            )
            return cur.rowcount > 0

    def close(self):
        self._conn.close()
