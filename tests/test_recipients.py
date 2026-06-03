from atc_mail.recipients import collect_reply_recipients


def test_reply_recipients_from_and_cc(monkeypatch):
    monkeypatch.setenv("MAIL_USER", "atc.noc.ops@gmail.com")
    result = collect_reply_recipients(
        "Jose <jose@tmoviles.com>",
        "Sebastian <sebastian.apestey@americantower.com>, NOC <atc.noc.ops@gmail.com>",
    )
    assert len(result) == 2
    assert "jose@tmoviles.com" in result[0].lower()
    assert "sebastian.apestey@americantower.com" in result[1].lower()


def test_reply_recipients_dedupes_from_in_cc(monkeypatch):
    monkeypatch.setenv("MAIL_USER", "bot@example.com")
    result = collect_reply_recipients(
        "A <a@test.com>",
        "A <a@test.com>, B <b@test.com>",
    )
    assert len(result) == 2
