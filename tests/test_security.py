from atc_mail.config import DEFAULT_ALLOWED_SENDER_DOMAINS, get_allowed_sender_domains
from atc_mail.security import is_own_mailbox, sender_allowed


def test_default_sender_domains():
    domains = get_allowed_sender_domains()
    assert "tmoviles.com.ar" in domains
    assert "americantower.com" in domains
    assert DEFAULT_ALLOWED_SENDER_DOMAINS == "tmoviles.com.ar,americantower.com"


def test_sender_allowed_tmoviles_and_atc(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    assert sender_allowed("Jose <jose@tmoviles.com.ar>")
    assert sender_allowed("NOC <noc@americantower.com>")
    assert not sender_allowed("other@gmail.com")
    assert not sender_allowed("user@tmoviles.com")


def test_sender_blocked_own_mailbox(monkeypatch):
    monkeypatch.setenv("MAIL_USER", "bot@americantower.com")
    assert is_own_mailbox("Bot <bot@americantower.com>")
    assert not sender_allowed("Bot <bot@americantower.com>")


def test_sender_whitelist_override(monkeypatch):
    monkeypatch.setenv("MAIL_ALLOWED_SENDER_DOMAINS", "example.com")
    assert get_allowed_sender_domains() == frozenset({"example.com"})
    assert sender_allowed("a@example.com")
    assert not sender_allowed("a@americantower.com")
