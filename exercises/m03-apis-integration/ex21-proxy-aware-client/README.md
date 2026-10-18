# ex21 · Proxy-, CA- and allowlist-aware client for customer networks

**Module:** m03 · **Covers:** R26 On-site embedding, R05 Integration, R17 Security · **Time:** 45 min

## Scenario
Day one inside a bank: every outbound connection goes through an authenticated corporate proxy, TLS is
intercepted with the bank's own root CA, and the firewall team only opens egress to an explicit allowlist. Your
laptop demo fails with `SSL: CERTIFICATE_VERIFY_FAILED`. FDEs who can diagnose this in minutes instead of days
are worth their weight in gold.

## Your task
`NetworkPolicy.from_env(env: Mapping)` reads:

- `HTTPS_PROXY` / `https_proxy`, `HTTP_PROXY` / `http_proxy` (upper-case wins)
- `NO_PROXY` / `no_proxy`: comma list; entries match exact host, domain suffix (`.corp.local` or `corp.local`
  matches `api.corp.local`), or `*` (bypass everything). Ports in entries (`host:8443`) match only that port.
- `REQUESTS_CA_BUNDLE` then `SSL_CERT_FILE` → `ca_bundle`
- `FDE_EGRESS_ALLOWLIST`: comma list of host patterns (`api.anthropic.com`, `*.corp.local`). Empty ⇒ allow all.

Methods:
- `proxy_for(url) -> str | None` — proxy by scheme unless NO_PROXY matches.
- `check_egress(url)` — raise `EgressDenied` if the host is not allowlisted (`*.x.com` matches subdomains, not `x.com`).
- `diagnose(url) -> list[str]` — human-readable lines, exactly in this order:
  `"egress: allowed"` or `"egress: DENIED by allowlist"`, then `"proxy: <url>"` or `"proxy: direct"`, then
  `"ca_bundle: <path>"` or `"ca_bundle: system default"`.
- `opener()` — a `urllib.request.OpenerDirector` with a `ProxyHandler` configured from the policy (proxies for
  http/https, plus `no` from NO_PROXY).
