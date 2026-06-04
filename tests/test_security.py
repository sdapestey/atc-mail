from atc_mail.config import DEFAULT_ALLOWED_SENDER_DOMAINS, get_allowed_sender_domains
from atc_mail.security import is_own_mailbox, sender_allowed


def test_default_sender_domains():
    domains = get_allowed_sender_domains()
    assert "tmoviles.com.ar" in domains
    assert "retesar.com" in domains
    assert "americantower.com" in domains
    assert DEFAULT_ALLOWED_SENDER_DOMAINS == (
        "tmoviles.com.ar,retesar.com,americantower.com"
    )


def test_sender_allowed_domains(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    assert sender_allowed("Jose <jose@tmoviles.com.ar>")
    assert sender_allowed("NOC <noc@americantower.com>")
    assert sender_allowed("X <x@retesar.com>")
    assert not sender_allowed("other@gmail.com")
    assert not sender_allowed("user@tmoviles.com")


def test_sender_blocked_own_mailbox(monkeypatch):
    monkeypatch.setenv("MAIL_USER", "bot@americantower.com")
    assert is_own_mailbox("Bot <bot@americantower.com>")
    assert not sender_allowed("Bot <bot@americantower.com>")
