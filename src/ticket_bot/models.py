from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    id: str
    title: str
    date_str: str
    venue: str
    capacity: int


@dataclass
class Ticket:
    id: str
    event_id: str
    attendee_name: str
    phone: str
    token: str
    is_used: bool
    used_at: Optional[float]
    created_at: float


@dataclass
class CheckInResult:
    success: bool
    message: str
    ticket: Optional[Ticket] = None
