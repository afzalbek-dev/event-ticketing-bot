# Event Ticketing Bot

Tadbirlar, konferensiyalar va seminarlar uchun HMAC-SHA256 imzosi bilan himoyalangan QR chiptalar yaratuvchi, o'rinlar sig'imini nazorat qiluvchi va takroriy kirishni to'suvchi xavfsiz check-in moduli.

## Xususiyatlari
- **Kriptografik HMAC Imzosi**: Chipta tokenlarini soxtalashtirish yoki o'zgartirish mutlaqo mumkin emas.
- **Takroriy Kirishni To'sish (Anti-Duplicate Check-in)**: Bir marta skanerlangan chipta tizimda saqlanadi va ikkinchi marta o'tishga yo'l qo'yilmaydi.
- **Zal Sig'imi Nazorati**: O'rinlar soni (capacity) to'lganda qo'shimcha ro'yxatdan o'tish avtomatik bloklanadi.
- **CLI & Bot Integratsiyasi**: Chipta yaratish va QR skaner orqali terminalda tekshirish.

## Foydalanish (Python)
```python
from ticket_bot import TicketManager, TicketStorage, TicketSigner, Event

storage = TicketStorage("tickets.db")
signer = TicketSigner("my-secret-key")
manager = TicketManager(storage, signer)

# Tadbir yaratish
storage.save_event(Event("it-meetup", "Tashkent IT Meetup", "2026-11-20", "Hilton", capacity=150))

# Chipta berish
ticket = manager.register_attendee("it-meetup", "Anvar Qosimov", "+998901234567")
print("QR Token:", ticket.token)

# Eshikda tekshirish (Check-in)
result = manager.check_in_by_token(ticket.token)
print(result.message)
```

## CLI
```bash
ticket-bot create-event --id meetup1 --title "AI Meetup" --date "2026-12-01" --capacity 50
ticket-bot issue --event meetup1 --name "Alisher" --phone "+998901112233"
ticket-bot scan "<TOKEN>"
```

## Testlar
```bash
pytest tests/ -v
```

## Litsenziya
MIT
