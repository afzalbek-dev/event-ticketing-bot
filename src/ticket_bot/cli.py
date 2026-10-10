import argparse
import sys
import json
from .models import Event
from .signer import TicketSigner
from .storage import TicketStorage
from .manager import TicketManager


def main():
    parser = argparse.ArgumentParser(description="Event Ticketing Bot - Chiptalar va kirish nazorati CLI")
    parser.add_argument("--db", default="/tmp/tickets.db", help="SQLite ma'lumotlar bazasi")
    parser.add_argument("--secret", default="super-event-secret", help="HMAC maxfiy kaliti")
    subparsers = parser.add_subparsers(dest="command", required=True)

    event_p = subparsers.add_parser("create-event", help="Yangi tadbir e'lon qilish")
    event_p.add_argument("--id", required=True, help="Tadbir ID")
    event_p.add_argument("--title", required=True, help="Tadbir nomi")
    event_p.add_argument("--date", required=True, help="O'tkazilish sanasi")
    event_p.add_argument("--venue", default="Toshkent", help="Manzil")
    event_p.add_argument("--capacity", type=int, default=100, help="Maksimal o'rinlar soni")

    issue_p = subparsers.add_parser("issue", help="Chipta rasmiylashtirish")
    issue_p.add_argument("--event", required=True, help="Tadbir ID")
    issue_p.add_argument("--name", required=True, help="Ishtirokchi F.I.Sh")
    issue_p.add_argument("--phone", required=True, help="Telefon raqami")

    scan_p = subparsers.add_parser("scan", help="QR kod tokenini skanerlash va tekshirish")
    scan_p.add_argument("token", help="QR koddan o'qilgan token matni")

    args = parser.parse_args()
    storage = TicketStorage(args.db)
    signer = TicketSigner(args.secret)
    mgr = TicketManager(storage, signer)

    if args.command == "create-event":
        ev = Event(args.id, args.title, args.date, args.venue, args.capacity)
        storage.save_event(ev)
        print(f"✅ Tadbir saqlandi: {ev.title} (Sig'im: {ev.capacity})")
    elif args.command == "issue":
        try:
            t = mgr.register_attendee(args.event, args.name, args.phone)
            print(f"✅ Chipta berildi! ID: {t.id}")
            print(f"QR Token: {t.token}")
        except ValueError as e:
            print(f"Xatolik: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "scan":
        res = mgr.check_in_by_token(args.token)
        if res.success:
            print(f"🟢 {res.message}")
        else:
            print(f"🔴 {res.message}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
