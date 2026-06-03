from atc_mail.recipients import collect_reply_recipients


def test_reply_recipients_from_and_allowed_cc(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    result = collect_reply_recipients(
        "Jose <jose@tmoviles.com.ar>",
        "Sebastian <sebastian.apestey@americantower.com>, NOC <atc.noc.ops@gmail.com>",
    )
    assert len(result) == 2
    assert "jose@tmoviles.com.ar" in result[0].lower()
    assert "sebastian.apestey@americantower.com" in result[1].lower()


def test_reply_cc_excludes_external_gmail(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    result = collect_reply_recipients(
        "Sebastian <sebastian.apestey@americantower.com>",
        "Personal <sdapestey@gmail.com>",
    )
    assert len(result) == 1
    assert "sebastian.apestey@americantower.com" in result[0].lower()
    assert not any("gmail.com" in r for r in result)


def test_reply_recipients_dedupes_from_in_cc(monkeypatch):
    monkeypatch.setenv("MAIL_ALLOWED_SENDER_DOMAINS", "example.com")
    monkeypatch.setenv("MAIL_USER", "bot@example.com")
    result = collect_reply_recipients(
        "A <a@example.com>",
        "A <a@example.com>, B <b@example.com>",
    )
    assert len(result) == 2
