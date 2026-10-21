# ex21 · Proxy-, CA- and allowlist-aware client for customer networks

**Module:** m03 · **Covers:** R26 On-site embedding, R05 Integration, R17 Security · **Time:** 45 min

## Learning objectives
- Diagnose proxy, TLS-interception and egress problems in customer networks.
- Implement NO_PROXY and allowlist matching correctly.
- Produce a diagnosis the customer's network team can act on.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Proxy-, CA- and allowlist-aware
client for customer networks". Before I write code, teach me corporate proxies, NO_PROXY semantics, custom CA
bundles for TLS interception, and egress allowlists. Use short Python examples that are not the exercise solution.
Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one
wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m03-apis-integration/ex21-proxy-aware-client/starter.py so that test_network.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`EgressDenied`, `NetworkPolicy`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m03-apis-integration/ex21-proxy-aware-client` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Proxy-, CA- and allowlist-aware client for customer networks" as a senior forward deployed
engineer would before it ships to a customer. Specifically: Does '*.x.com' wrongly match 'x.com' or 'evilx.com'? Are
ports in NO_PROXY entries respected? Would the diagnose() output let a network engineer fix the problem without a
call? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
