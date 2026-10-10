import uuid
import time
from typing import Optional, Dict, Any
from .models import Event, Ticket, CheckInResult
from .signer import TicketSigner
from .storage import TicketStorage


class TicketManager:
    """Chiptalarni generatsiya qilish, sig'imni tekshirish va kirish nazorati."""

    def __init__(self, storage: TicketStorage, signer: TicketSigner):
        self.storage = storage
        self.signer = signer

    def register_attendee(self, event_id: str, attendee_name: str, phone: str) -> Ticket:
        event = self.storage.get_event(event_id)
        if not event:
            raise ValueError(f"Tadbir topilmadi: {event_id}")

        current_count = self.storage.count_event_tickets(event_id)
        if current_count >= event.capacity:
            raise ValueError(f"Tadbirda bo'sh joy qolmagan (Sig'im: {event.capacity})")

        ticket_id = f"tkt_{uuid.uuid4().hex[:8]}"
        payload = {
            "ticket_id": ticket_id,
            "event_id": event_id,
            "attendee_name": attendee_name,
            "phone": phone,
        }
        token = self.signer.generate_token(payload)

        ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            attendee_name=attendee_name,
            phone=phone,
            token=token,
            is_used=False,
            used_at=None,
            created_at=time.time(),
        )
        self.storage.save_ticket(ticket)
        return ticket

    def check_in_by_token(self, token: str) -> CheckInResult:
        payload = self.signer.verify_token(token)
        if not payload:
            return CheckInResult(success=False, message="Soxta yoki yaroqsiz QR chipta imzosi!")

        ticket_id = payload.get("ticket_id")
        ticket = self.storage.get_ticket_by_id(ticket_id)
        if not ticket:
            return CheckInResult(success=False, message="Chipta bazadan topilmadi!")

        if ticket.is_used:
            return CheckInResult(
                success=False,
                message=f"DIQQAT: Chipta allaqachon ishlatilgan! (Vaqt: {ticket.used_at})",
                ticket=ticket,
            )

        updated = self.storage.mark_ticket_used(ticket_id)
        if not updated:
            return CheckInResult(success=False, message="Chipta holatini yangilashda xatolik!", ticket=ticket)

        ticket.is_used = True
        return CheckInResult(success=True, message=f"Xush kelibsiz, {ticket.attendee_name}! Kirishga ruxsat.", ticket=ticket)
