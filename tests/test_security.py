from atc_mail.config import get_allowed_sender_domains
from atc_mail.security import is_own_mailbox, sender_allowed


def test_sender_allowed_all_when_domains_empty(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.setenv("MAIL_ALLOWED_SENDER_DOMAINS", "")
    assert get_allowed_sender_domains() == frozenset()
    assert sender_allowed("Jose <jose@tmoviles.com>")


def test_sender_blocked_own_mailbox(monkeypatch):
    monkeypatch.setenv("MAIL_USER", "sebastian.apestey@americantower.com")
    assert is_own_mailbox("Sebastian <sebastian.apestey@americantower.com>")
    assert not sender_allowed("Sebastian <sebastian.apestey@americantower.com>")


def test_sender_whitelist(monkeypatch):
    monkeypatch.setenv("MAIL_ALLOWED_SENDER_DOMAINS", "tmoviles.com")
    assert sender_allowed("jose@tmoviles.com")
    assert not sender_allowed("other@example.com")
