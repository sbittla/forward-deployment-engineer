import pytest

TEXT = ("Customer ana.ruiz@example.com called from (415) 555-0100 about card 4111 1111 1111 1111. "
        "SSN 123-45-6789. Follow-up to ana.ruiz@example.com or bob@corp.io. Server 10.0.0.255.")


def types(impl, text):
    return [(e.type, e.value) for e in impl.detect(text)]


def test_detect_all(impl):
    assert types(impl, TEXT) == [
        ("EMAIL", "ana.ruiz@example.com"), ("PHONE", "(415) 555-0100"), ("CREDIT_CARD", "4111 1111 1111 1111"),
        ("SSN", "123-45-6789"), ("EMAIL", "ana.ruiz@example.com"), ("EMAIL", "bob@corp.io"), ("IP", "10.0.0.255")]


@pytest.mark.parametrize("text", ["SSN 000-12-3456", "SSN 666-12-3456", "SSN 912-12-3456", "SSN 123-00-4567",
                                  "card 4111 1111 1111 1112", "ip 300.1.1.1", "order 12345"])
def test_negatives(impl, text):
    assert impl.detect(text) == []


@pytest.mark.parametrize("phone", ["415-555-0100", "415.555.0100", "+1 415 555 0100", "1-415-555-0100"])
def test_phone_formats(impl, phone):
    assert types(impl, f"call {phone} now") == [("PHONE", phone)]


def test_luhn(impl):
    assert impl.luhn_ok("4111111111111111") and impl.luhn_ok("5500005555555559")
    assert not impl.luhn_ok("4111111111111112")


def test_offsets(impl):
    for e in impl.detect(TEXT):
        assert TEXT[e.start:e.end] == e.value


def test_mask(impl):
    red, mapping = impl.redact("mail a@b.co and 415-555-0100", mode="mask")
    assert red == "mail [EMAIL] and [PHONE]" and mapping == {}


def test_tokens_consistent_and_restore(impl):
    red, mapping = impl.redact(TEXT)
    assert red.count("[EMAIL_1]") == 2 and "[EMAIL_2]" in red and "[CREDIT_CARD_1]" in red
    assert "ana.ruiz" not in red and "4111" not in red and "123-45" not in red
    assert mapping["[EMAIL_2]"] == "bob@corp.io"
    assert impl.restore(red, mapping) == TEXT
