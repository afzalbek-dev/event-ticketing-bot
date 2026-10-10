import pytest
from ticket_bot.models import Event
from ticket_bot.signer import TicketSigner
from ticket_bot.storage import TicketStorage
from ticket_bot.manager import TicketManager


def test_ticket_issue_and_checkin_flow(tmp_path):
    db_file = str(tmp_path / "tickets_test.db")
    storage = TicketStorage(db_file)
    signer = TicketSigner("my-test-secret-key")
    manager = TicketManager(storage, signer)

    # 1. Tadbir yaratish
    ev = Event("devcon2026", "Uzbekistan DevCon 2026", "2026-11-15", "Tashkent", capacity=2)
    storage.save_event(ev)

    # 2. Chipta berish
    t1 = manager.register_attendee("devcon2026", "Javohir Aliyev", "+998901112233")
    assert t1.is_used is False
    assert len(t1.token) > 20

    # 3. 1-marta kirish (Check-in muvaffaqiyatli)
    res1 = manager.check_in_by_token(t1.token)
    assert res1.success is True
    assert "Javohir Aliyev" in res1.message

    # 4. 2-marta o'sha tokenni skanerlash (Rad etilishi shart!)
    res2 = manager.check_in_by_token(t1.token)
    assert res2.success is False
    assert "allaqachon ishlatilgan" in res2.message

    # 5. Sig'im chegarasi tekshiruvi (Capacity limit)
    t2 = manager.register_attendee("devcon2026", "Bobur Mirzo", "+998902223344")
    # 3-chi ishtirokchi qo'shilganda ValueError chiqarishi kerak
    with pytest.raises(ValueError, match="bo'sh joy qolmagan"):
        manager.register_attendee("devcon2026", "Ortiqcha Odam", "+998903334455")

    storage.close()


def test_tampered_token_rejection():
    signer = TicketSigner("secure-key")
    storage = TicketStorage(":memory:")
    manager = TicketManager(storage, signer)

    # Soxtalashtirilgan token
    fake_token = "eyJhbGciOiJIUzI1NiJ9.tampered_signature"
    res = manager.check_in_by_token(fake_token)
    assert res.success is False
    assert "Soxta yoki yaroqsiz" in res.message
