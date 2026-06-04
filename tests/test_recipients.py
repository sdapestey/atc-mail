from atc_mail.recipients import collect_reply_recipients


def test_reply_to_sender_cc_always_notify(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.delenv("MAIL_ALWAYS_CC", raising=False)
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    r = collect_reply_recipients(
        "Sebastian <sebastian@tmoviles.com.ar>",
        None,
    )
    assert len(r.to) == 1
    assert "sebastian@tmoviles.com.ar" in r.to[0].lower()
    assert len(r.cc) == 2
    cc_lower = " ".join(r.cc).lower()
    assert "lucas.gimenez@americantower.com" in cc_lower
    assert "facundo.vergara@americantower.com" in cc_lower


def test_reply_cc_includes_inbound_and_always(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.delenv("MAIL_ALWAYS_CC", raising=False)
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    r = collect_reply_recipients(
        "Jose <jose@tmoviles.com.ar>",
        "Facundo <facundo.vergara@americantower.com>",
    )
    assert "jose@tmoviles.com.ar" in r.to[0].lower()
    assert len(r.cc) == 2
    cc_lower = " ".join(r.cc).lower()
    assert "lucas.gimenez@americantower.com" in cc_lower
    assert "facundo.vergara@americantower.com" in cc_lower
    assert cc_lower.count("facundo.vergara@americantower.com") == 1


def test_reply_cc_excludes_external_gmail(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.delenv("MAIL_ALWAYS_CC", raising=False)
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    r = collect_reply_recipients(
        "Sebastian <sebastian.apestey@americantower.com>",
        "Personal <sdapestey@gmail.com>",
    )
    assert len(r.to) == 1
    assert not any("gmail.com" in c.lower() for c in r.cc)


def test_retesar_sender_allowed_in_to(monkeypatch):
    monkeypatch.delenv("MAIL_ALLOWED_SENDER_DOMAINS", raising=False)
    monkeypatch.setenv("MAIL_USER", "bot@americantower.com")
    r = collect_reply_recipients("User <user@retesar.com>", None)
    assert "user@retesar.com" in r.to[0].lower()
