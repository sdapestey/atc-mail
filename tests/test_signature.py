from atc_mail.signature import (
    LOGO_CID,
    get_signature_settings,
    signature_html,
    signature_logo_path,
    signature_text,
)


def test_signature_defaults(monkeypatch):
    monkeypatch.delenv("MAIL_SIGNATURE_NAME", raising=False)
    s = get_signature_settings()
    assert s["display_name"] == "NOC Bot"
    assert s["company"] == "American Tower Corporation"
    assert "Libertador" in s["address_line1"]
    assert "21583591" in s["phone"]
    assert s["email"] == "noc_atc@americantower.com"

    text = signature_text()
    assert "NOC Bot" in text
    assert "American Tower Corporation" in text
    assert "noc_atc@americantower.com" in text

    html = signature_html()
    assert "NOC Bot" in html
    assert "American Tower Corporation" in html
    assert "#D0DDFF" in html
    assert "#FF9A9C" in html
    assert "#A8C5FF" in html
    assert "Calibri" in html
    assert "Times New Roman" in html
    assert "<table" in html
    assert "<br>" not in html.split("NOC Bot")[1].split("</table>")[0]
    assert f"cid:{LOGO_CID}" in html
    assert "linkedin.com" not in html

    assert signature_logo_path() is not None
