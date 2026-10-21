from fde_kit import tokenize

SEVERITY_WEIGHT = {"blocker": 5, "major": 2, "minor": 1}


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def cluster(items: list[dict], threshold: float = 0.3) -> list[list[int]]:
    clusters: list[list[int]] = []
    heads: list[set] = []
    for i, it in enumerate(items):
        toks = set(tokenize(it["text"]))
        for c, head in zip(clusters, heads):
            if _jaccard(head, toks) >= threshold:
                c.append(i)
                break
        else:
            clusters.append([i])
            heads.append(toks)
    return clusters


def score(cluster_items: list[dict]) -> float:
    arr_by_customer = {it["customer"]: it["arr"] for it in cluster_items}
    sev = sum(SEVERITY_WEIGHT[it["severity"]] for it in cluster_items)
    return round(len(arr_by_customer) * 10 + sum(arr_by_customer.values()) / 100_000 + sev, 2)


def brief(items: list[dict], top: int = 3, threshold: float = 0.3) -> str:
    groups = cluster(items, threshold)
    ranked = sorted(groups, key=lambda g: (-score([items[i] for i in g]), g[0]))[:top]
    out = ["# Field feedback brief"]
    for n, g in enumerate(ranked, 1):
        its = [items[i] for i in g]
        customers = sorted({it["customer"] for it in its})
        arr = sum({it["customer"]: it["arr"] for it in its}.values())
        counts = {s: sum(it["severity"] == s for it in its) for s in SEVERITY_WEIGHT}
        quote = max(its, key=lambda it: SEVERITY_WEIGHT[it["severity"]])
        if n > 1:
            out.append("")
        out += [
            f"## {n}. {its[0]['text']}",
            f"- Customers: {len(customers)} ({', '.join(customers)})",
            f"- ARR represented: ${arr:,}",
            f"- Severity: {counts['blocker']} blocker, {counts['major']} major, {counts['minor']} minor",
            f"- Score: {score(its)}",
            f'> "{quote["text"]}" — {quote["customer"]}',
        ]
    return "\n".join(out) + "\n"
