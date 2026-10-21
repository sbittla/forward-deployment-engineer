import pytest
"""Vectors for the java variant were produced by compiling and running reference/CustomerSigner.java."""
import base64
import hashlib
import hmac
from datetime import datetime, timezone

TS = datetime(2026, 10, 16, 9, 30, tzinfo=timezone.utc)
Q1 = {"status": ["open"], "limit": ["50"]}
Q2 = {"q": ["late delivery *urgent*", "a~b"], "customer name": ["O'Brien & Sons"]}
BODY2 = '{"note":"Ünïcödé ok"}'.encode("utf-8")

JAVA_CANON_1 = ("GET\n/v1/shipments\nlimit=50&status=open\n"
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n20261016T093000Z")
JAVA_SIG_1 = "zvc9YMWLCBMRVY2pMQnn+n1V2nK/UAn9l/lCdggGrRc="
JAVA_CANON_2 = ("POST\n/v1/shipments/SH%2042/notes\n"
                "customer%20name=O%27Brien%20%26%20Sons&q=a~b&q=late%20delivery%20%2Aurgent%2A\n"
                "9927610121bf0877f608518c640ab4dc1f00c26ceae7e16f36954ad7b2717cb7\n20261016T093000Z")
JAVA_SIG_2 = "YCxdd4fMXx17LH36IY6fug1W5ykGn/NjnR0adCiJmic="


def test_rfc3986(impl):
    assert impl.rfc3986("a b*c~d/e") == "a%20b%2Ac~d%2Fe"
    assert impl.rfc3986("Ü") == "%C3%9C" and impl.rfc3986("-_.~") == "-_.~"
    assert impl.encode_path("/v1/shipments/SH 42/notes") == "/v1/shipments/SH%2042/notes"


def test_java_vectors(impl):
    assert impl.canonical_request("get", "/v1/shipments", Q1, b"", TS) == JAVA_CANON_1
    assert impl.canonical_request("POST", "/v1/shipments/SH 42/notes", Q2, BODY2, TS) == JAVA_CANON_2
    h1 = impl.sign_headers("get", "/v1/shipments", Q1, b"", TS, "AK1", "s3cr3t-key")
    assert h1 == {"Authorization": f"NWS1-HMAC-SHA256 Credential=AK1, Signature={JAVA_SIG_1}",
                  "X-NWS-Date": "20261016T093000Z"}
    h2 = impl.sign_headers("POST", "/v1/shipments/SH 42/notes", Q2, BODY2, TS, "AK1", "s3cr3t-key")
    assert h2["Authorization"].endswith(JAVA_SIG_2)


def test_go_variant(impl):
    h = impl.sign_headers("get", "/v1/shipments", Q1, b"", TS, "AK1", "s3cr3t-key", variant="go")
    expected_hex = base64.b64decode(JAVA_SIG_1).hex()
    assert h == {"authorization": f"NWS1-HMAC-SHA256 Credential=AK1, Signature={expected_hex}",
                 "x-nws-date": "20261016T093000Z"}


def test_cpp_variant(impl):
    canon = impl.canonical_request("get", "/v1/shipments", Q1, b"", TS, variant="cpp")
    assert canon == ("GET\n/v1/shipments\nlimit=50&status=open\n"
                     "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855\n1792143000")
    h = impl.sign_headers("get", "/v1/shipments", Q1, b"", TS, "AK1", "s3cr3t-key", variant="cpp")
    sig = base64.b64encode(hmac.new(b"s3cr3t-key", canon.encode(), hashlib.sha256).digest()).decode()
    assert h == {"Authorization": f"NWS1-HMAC-SHA256 Credential=AK1, Signature={sig}", "X-NWS-Date": "1792143000"}


def test_unknown_variant_and_unicode(impl):
    ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        impl.canonical_request("GET", "/", {}, b"", ts, "rust")
    with pytest.raises(ValueError):
        impl.sign_headers("GET", "/", {}, b"", ts, "k", "s", variant="python")
    assert impl.rfc3986("ü ~*") == "%C3%BC%20~%2A" and impl.encode_path("/a b/ü") == "/a%20b/%C3%BC"
    assert impl.canonical_query({}) == ""
