import pytest

GOOD = {"FDE_API_BASE_URL": "https://api.example.com", "FDE_API_KEY": "sk-live-123",
        "FDE_TIMEOUT_S": "12.5", "FDE_MAX_RETRIES": "5", "FDE_LOG_LEVEL": "debug",
        "FDE_ALLOWED_TENANTS": " acme, globex ,, initech "}


def test_happy_path(impl):
    s = impl.load_settings(GOOD)
    assert s.api_base_url == "https://api.example.com"
    assert s.api_key.reveal() == "sk-live-123"
    assert s.timeout_s == 12.5 and s.max_retries == 5 and s.log_level == "DEBUG"
    assert s.allowed_tenants == ("acme", "globex", "initech")


def test_defaults(impl):
    s = impl.load_settings({"FDE_API_BASE_URL": "https://x", "FDE_API_KEY": "k"})
    assert (s.timeout_s, s.max_retries, s.log_level, s.allowed_tenants) == (30.0, 3, "INFO", ())


def test_all_errors_reported(impl):
    env = {"FDE_API_BASE_URL": "http://insecure", "FDE_TIMEOUT_S": "-1",
           "FDE_MAX_RETRIES": "eleven", "FDE_LOG_LEVEL": "LOUD"}
    with pytest.raises(impl.ConfigError) as e:
        impl.load_settings(env)
    errs = " | ".join(e.value.errors)
    for var in ("FDE_API_BASE_URL", "FDE_API_KEY", "FDE_TIMEOUT_S", "FDE_MAX_RETRIES", "FDE_LOG_LEVEL"):
        assert var in errs
    assert len(e.value.errors) == 5


def test_retry_range(impl):
    with pytest.raises(impl.ConfigError):
        impl.load_settings({**GOOD, "FDE_MAX_RETRIES": "11"})


def test_secret_never_printed(impl):
    s = impl.load_settings(GOOD)
    assert "sk-live-123" not in repr(s) and "sk-live-123" not in str(s.api_key)
    assert str(s.api_key) == "Secret('****')"
    assert s.api_key == impl.Secret("sk-live-123")
    r = s.redacted()
    assert r["api_key"] == "****" and r["timeout_s"] == 12.5 and "sk-live-123" not in str(r)
