# ex21 hints · Proxy-, CA- and allowlist-aware client for customer networks

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start with `from_env`. Two tiny helpers cover almost all of it: one that returns the first non-empty value from a list
of variable names (upper-case first), and one that splits a comma list, strips each entry and drops empty ones. Parse
URLs with `urllib.parse.urlsplit`, which gives you `.scheme`, `.hostname` and `.port`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **NO_PROXY matching:** for each entry, `*` bypasses everything. Otherwise split off an optional `:port`. If the
  entry has a port and it doesn't equal the URL's port, skip the entry. Strip a leading `.` from the host part; it
  matches if the host equals it or ends with `"." + entry`.
- **Allowlist:** an empty list allows everything. A pattern with `*` uses `fnmatch.fnmatchcase`; a pattern without
  one must match the host exactly.
- **diagnose:** build the three strings from the same helpers that `proxy_for` and `check_egress` use.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A plain `host.endswith(entry)` check is a security bug: `evilcorp.local` ends with `corp.local`. Match on a dot
  boundary.
- Compare hosts, never the whole URL: `api.anthropic.com.evil.com` must be denied.
- `*.corp.local` matches subdomains but not `corp.local` itself. `fnmatch` gives you this for free, because the `.`
  after `*` must be present.
- `ProxyHandler` reads the bypass list from the `"no"` key, as one comma-joined string.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_from_env` | Lower-case variable preferred over upper-case; CA bundle order reversed |
| `test_proxy_for` | Port in a NO_PROXY entry ignored (or required on every entry); leading-dot entries not matched |
| `test_no_proxy_star` | `*` treated as a hostname pattern rather than "bypass all" |
| `test_egress` | Suffix match without a dot boundary; wildcard matching the bare domain; empty allowlist denying everything |
| `test_diagnose` | Lines out of order, or wording differs from the README exactly |
| `test_opener` | Bypass list not passed under the `no` key |
