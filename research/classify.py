"""Classification rules for the forward deployed engineer posting sample.

These are the rules behind every posting percentage in the book (Sections 1.2, 1.3 and 17.1). They are kept
here, in the public repository, so a reader can audit them and re-run them against postings they collect
themselves. The posting text itself is not published (it belongs to the employers); `postings-index.csv`
holds only identifiers and the 0/1 result of each rule.

Usage, against your own collection (a JSON list of {company, source, title, location, url, text}):

    python research/classify.py my_postings.json --out my-index.csv --collected 2026-10-18
    python research/analyze_index.py my-index.csv

Pipeline, in order:
  1. include_reason(): keep individual-contributor engineering titles; drop aggregators, managers, strategists,
     executives and non-engineering roles. Each excluded posting records why.
  2. dedupe groups: postings at one company are the same role when their titles match once location
     qualifiers are removed ("FDE - London" == "FDE - Paris"), or when their text is identical.
     The first posting of each group (in collection order) represents it.
  3. strip_boilerplate(): remove the job-title phrase and benefits, equal-opportunity, pay and office-policy
     sentences, so that, for example, "health insurance" doesn't count as the healthcare sector.
  4. Each TAXONOMY regex is matched, case-insensitively, against the stripped text: 1 if it matches anywhere.
"""
import argparse
import csv
import json
import re
from pathlib import Path

# --------------------------------------------------------------------------- 1. inclusion

AGGREGATORS = {"jobgether"}  # re-posts other employers' roles under its own name, once per country
EXCLUDE_TITLE = re.compile(
    r"manager|recruiter|product|strategist|engagement|program|director|gtm|leadership|partner manager|"
    r"accelerator|data scientist|head of|\brvp\b|vice president|deployment lead|engineering lead|"
    r"finance engineer", re.I)
ENGINEERING_TITLE = re.compile(r"engineer|developer|architect|technical staff|deployed staff|\bfde\b", re.I)


def include_reason(company, title):
    """Return (included, reason). reason is '' when included."""
    if company.lower() in AGGREGATORS:
        return False, "aggregator"
    m = EXCLUDE_TITLE.search(title)
    if m:
        word = m.group(0).lower()
        if word == "finance engineer":
            return False, "non-engineering (finance specialist)"
        return False, f"non-IC title ({word})"
    if not ENGINEERING_TITLE.search(title):
        return False, "non-engineering title"
    return True, ""


# --------------------------------------------------------------------------- 2. duplicates

REGION_WORDS = set("""
emea apac latam anz amer noram nyc sf bay area us usa uk u s united states kingdom europe southern east
asia middle india japan korea south singapore australia germany france spain sweden netherlands brazil mexico
argentina canada switzerland ireland doha uae tokyo seoul london paris munich zurich madrid sydney seattle boston
atlanta chicago charlotte raleigh new york city san francisco washington dc d c remote speaking based
""".split())
# words that look like places in some location field but name a distinct role in a title
NOT_LOCATION = {"engineer", "engineering", "government", "public", "sector", "federal", "commercial", "intel",
                "health", "civilian", "national", "security", "early", "career", "mandarin", "german",
                "french", "spanish"}


def location_vocabulary(posts):
    words = set(REGION_WORDS)
    for p in posts:
        words.update(re.findall(r"[a-z]+", (p.get("location") or "").lower()))
    return words - NOT_LOCATION


def role_title(title, loc_words):
    """Title with location-only qualifiers removed, lower-cased: 'FDE - London' -> 'fde'."""
    segs = re.split(r"\s+[-–—]\s+|\s*[(),]\s*|-(?=[A-Z][a-z]+$)", title)
    keep = []
    for s in segs:
        w = re.findall(r"[a-z]+", s.lower())
        if keep and w and all(x in loc_words for x in w):
            continue
        keep.append(s)
    return re.sub(r"\W+", " ", " ".join(keep).lower()).strip()


def dedupe_groups(posts, included):
    """Return a list of group ids (int, 1-based) aligned with posts; 0 for excluded postings."""
    loc_words = location_vocabulary(posts)
    parent = list(range(len(posts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first = {}
    for i, p in enumerate(posts):
        if not included[i]:
            continue
        keys = [("title", p["company"], role_title(p["title"], loc_words)),
                ("text", p["company"], re.sub(r"\s+", " ", p.get("text", "").lower()).strip())]
        for k in keys:
            if k in first:
                a, b = find(i), find(first[k])
                parent[max(a, b)] = min(a, b)
            else:
                first[k] = i
    ids, out = {}, []
    for i in range(len(posts)):
        if not included[i]:
            out.append(0)
            continue
        root = find(i)
        ids.setdefault(root, len(ids) + 1)
        out.append(ids[root])
    return out


# --------------------------------------------------------------------------- 3. boilerplate

TITLE_PHRASES = re.compile(
    r"forward[\s-]*deploy(ed|ment)?(\s+(software|ai|infrastructure|reliability|security|enablement))?"
    r"(\s+engineer(s|ing)?)?|\b(agent |ai |partner |early access )?deploy(ed|ment) (engineer(s|ing)?|strategists?|"
    r"leads?|staff)\b|\bfd(s)?es?\b", re.I)
BOILERPLATE = re.compile(
    r"insurance (plan|coverage|benefit)|(health|medical|dental|vision|life|disability)( and \w+)? insurance|"
    r"\bdental\b|\b401\(?k\)?|paid (time off|leave|holidays|parental)|parental leave|\bpto\b|\bbenefits?\b|"
    r"\bperks\b|wellness|stipend|pet insurance|\b(hsa|fsa|hra)\b|fertility|vacation|travel(ing)? to other offices|"
    r"intra-office travel|company offsites?|equity (package|grant)|\bequal (employment )?opportunit|\beeo\b|"
    r"without regard to|regardless of (race|gender|age|sex)|protected (veteran|class|characteristic)|"
    r"reasonable accommodation|disabilit(y|ies)|pay transparency|salary range|base (pay|salary)|"
    r"compensation|on-target earnings|\bote\b|e-verify|privacy (notice|policy)|"
    r"specified as onsite|from an office|in[- ]office|office culture|hybrid (work|workplace|role|schedule|model)|"
    r"days (a|per) week (in|at|from) (the|our|an|one of our) office|return to office|"
    r"relocation (assistance|support|package)|"
    r"visa sponsorship|export[- ]control|^\s*compliance\s*:?\s*$|job posting compliance|immigration compliance|"
    r"data protection regulation|consumer privacy act|export administration|deemed export|government licen[cs]e", re.I)


def strip_boilerplate(text):
    """Drop the job-title phrase and every sentence or line that is benefits, EEO, pay or office policy."""
    kept = []
    for seg in re.split(r"\n+|(?<=[.!?;])\s+|\s+[•·]\s+", text or ""):
        if seg.strip() and not BOILERPLATE.search(seg):
            kept.append(seg)
    return TITLE_PHRASES.sub(" ", "\n".join(kept))


# --------------------------------------------------------------------------- 4. requirements

# id, name, regex (case-insensitive), evaluated against strip_boilerplate(text)
TAXONOMY = [
    ("R01", "Python proficiency", r"\bpython\b"),
    ("R02", "TypeScript/JavaScript & full-stack web", r"typescript|javascript|react|node\.?js|full[- ]?stack|frontend|front-end"),
    ("R03", "SQL & data modeling", r"\bsql\b|postgres|data model|schema|data warehouse|bigquery|relational"),
    ("R04", "Data pipelines / ETL / Spark", r"\betl\b|elt\b|pipeline|spark|airflow|dbt\b|ingest|streaming|kafka"),
    ("R05", "APIs & system integration", r"\bapis?\b|integrat|\brest(ful)?\b|graphql|webhook|\bsdks?\b"),
    ("R06", "Cloud platforms (AWS/GCP/Azure)", r"\baws\b|\bgcp\b|azure|google cloud|cloud (platform|infrastructure|provider)"),
    ("R07", "Containers, Kubernetes, IaC, CI/CD", r"docker|kubernetes|\bk8s\b|terraform|ci/cd|containers?|helm|infrastructure as code|devops"),
    ("R08", "LLM application development", r"\bllms?\b|large language model|generative ai|genai|gpt|claude|foundation model"),
    ("R09", "Prompt & context engineering", r"prompt|context engineering|system prompt"),
    ("R10", "RAG, retrieval, vector search", r"\brag\b|retrieval|vector|embedding|semantic search|search relevance"),
    ("R11", "Agents, tool use, orchestration", r"\bagents?\b|agentic|tool[- ]use|function calling|orchestrat|langgraph|langchain|multi-agent"),
    ("R12", "MCP (Model Context Protocol)", r"\bmcp\b|model context protocol"),
    ("R13", "Evaluation & quality measurement", r"\bevals?\b|evaluation|benchmark|test harness|golden (set|dataset)|quality metrics|llm[- ]as[- ]a[- ]judge"),
    ("R14", "Guardrails, safety & responsible AI", r"guardrail|safety|responsible ai|hallucinat|red[- ]team|jailbreak|pii"),
    ("R15", "Observability, monitoring & reliability", r"observab|monitor|logging|tracing|reliab|incident|on[- ]call|sre\b|uptime|latency"),
    ("R16", "Fine-tuning / ML fundamentals", r"fine[- ]tun|machine learning|\bml\b|model training|pytorch|reinforcement|deep learning"),
    ("R17", "Security, auth & compliance", r"security|secure|\bauth(n|z|entication|orization)?\b|\bsso\b|oauth|compliance|soc ?2|hipaa|fedramp|clearance|rbac|encryption"),
    ("R18", "Customer discovery & requirements", r"discover|requirements|scop|understand (their|customer)|business problem|use cases?|workflows?"),
    ("R19", "Stakeholder communication & exec presence", r"communicat|stakeholder|executive|c-suite|\bpresent|storytell|articulat|non-technical"),
    ("R20", "Ownership, ambiguity & bias to action", r"ownership|ambigu|scrappy|bias (for|to) action|autonomy|autonomously|self-starter|fast-paced|end-to-end|zero to one|0 to 1"),
    ("R21", "Rapid prototyping & demos / POCs", r"prototyp|proof[- ]of[- ]concept|\bpocs?\b|\bdemos?\b|pilot|mvp"),
    ("R22", "Production deployment & hardening", r"\bproduction\b|\bdeploy(s|ed|ing|ment|ments)?\b|\bship(s|ped|ping)?\b|harden|go[- ]live|\blaunch"),
    ("R23", "Product feedback loop to core eng", r"feedback|product (team|roadmap)|inform (the )?roadmap|core (product|platform)|reusable|productiz"),
    ("R24", "Technical writing & enablement", r"documentation|playbook|technical writ|best practices|enablement|workshop|training|knowledge base|runbook"),
    ("R25", "Domain/industry context (regulated)", r"financial services|healthcare|life sciences|public sector|government|defense|insurance|regulated"),
    ("R26", "Travel & on-site embedding", r"(?<!\w)travel(?!\s+(software|industry|tech|and hospitality|& hospitality|booking))|on[- ]site|onsite|customer site"),
    ("R27", "Performance, cost & latency optimization", r"cost|latency|throughput|optimi[sz]|token|performance"),
    ("R28", "Distributed systems & backend architecture", r"distributed (systems?|computing|services)|\bback[- ]?end\b|microservices?|system design|(software|systems?|backend|service|solution) architecture"),
    ("R29", "Debugging & troubleshooting in customer env", r"debug|troubleshoot|root cause|triage|unblock"),
    ("R30", "Delivery against measurable value", r"\broi\b|business (value|impact|outcomes)|\bkpis?\b|success metrics|milestones?|measurable (value|impact|outcomes|results|business)|time[- ]to[- ]value|value realization"),
    ("R31", "Data platforms (Databricks/Snowflake/lakehouse)", r"databricks|lakehouse|delta lake|snowflake|unity catalog|ontology|foundry"),
    ("R32", "Voice / multimodal AI", r"\bvoice\b|speech|audio|multimodal|computer vision|telephony|\bivr\b"),
    ("R33", "Delivery management, SOWs & project plans", r"statement of work|scopes? of work|\bsow\b|project plans?|milestones?|acceptance criteria|critical path|dependencies|delivery plan"),
    ("R34", "Adoption & change management", r"change management|adoption|onboarding|drive usage"),
    ("R35", "Customer enablement & teaching", r"workshops?|train(ing)? (customers|users|teams|operators)|teach|enablement|code-with|knowledge transfer|instructor"),
    ("R36", "Vendor AI platforms & SDKs (multi-provider)", r"bedrock|vertex|azure openai|ai foundry|agents? sdk|responses api|agent skills?|sub-?agents?|multi[- ]provider|model[- ]agnostic|claude api|openai api|anthropic api|gemini"),
    ("R37", "AI-assisted engineering (coding agents)", r"claude code|cursor|github copilot|ai coding|coding agents?|ai-assisted (coding|development)|agentic development"),
    ("R38", "Document & multimodal AI", r"multimodal|\bocr\b|document (processing|understanding|intelligence|extraction)|\bpdfs?\b|images?|vision models?"),
    ("R39", "Identity & permission-aware access", r"\bsso\b|okta|entra|saml|oidc|identity|permissions?|access control|least privilege"),
    ("R40", "Technical leadership & design review", r"mentor|tech(nical)? lead|design reviews?|architecture reviews?|code reviews?|lead (a )?(team|pod)|\bpods?\b|technical direction"),
    ("R41", "AI security assessment & red teaming", r"red[- ]team|jailbreak|adversarial|prompt injection|ai security"),
    ("R42", "Ontology & semantic modeling", r"ontology|knowledge graph|semantic (layer|model)|data model(l)?ing|object model"),
    ("R43", "Regulatory & compliance frameworks", r"gdpr|hipaa|soc ?2|fedramp|iso ?27001|eu ai act|\bpci\b|\bsox\b|compliance|regulatory|\bgrc\b"),
    ("R44", "Incident response & postmortems", r"incidents?|on[- ]call|postmortems?|post-mortems?|root cause"),
]

# Extra per-posting facts cited in the book (Chapters 1 and 17)
EXTRA = [
    ("aws", r"\baws\b|amazon web services"),
    ("azure", r"\bazure\b"),
    ("gcp", r"\bgcp\b|google cloud"),
    ("clearance", r"clearance"),
]
YEARS_RX = re.compile(r"(\d{1,2})\+?\s*(?:(?:-|to|–)\s*\d{1,2}\s*)?\+?\s*years", re.I)
TRAVEL_WINDOW_RX = re.compile(r"[^.\n]{0,60}travel[^.\n]{0,60}", re.I)
TRAVEL_NUM_RX = re.compile(r"(\d{1,3})(?=\s*(?:%|(?:-|–|to)\s*\d{1,3}\s*%))")

_COMPILED = [(rid, re.compile(p, re.I)) for rid, _, p in TAXONOMY] + [(k, re.compile(p, re.I)) for k, p in EXTRA]


def classify(text):
    """Return {column: value} for one posting's raw text."""
    body = strip_boilerplate(text)
    row = {k: int(bool(rx.search(body))) for k, rx in _COMPILED}
    years = sorted({int(m) for m in YEARS_RX.findall(body) if 0 < int(m) < 20})
    travel = sorted({int(x) for w in TRAVEL_WINDOW_RX.findall(body) for x in TRAVEL_NUM_RX.findall(w)
                     if 0 < int(x) <= 100})
    row["years_stated"] = ";".join(map(str, years))
    row["travel_pct_stated"] = ";".join(map(str, travel))
    return row


COLUMNS = (["company", "title", "location", "url", "source", "collected", "included", "exclusion_reason",
            "dedupe_group", "representative"] + [rid for rid, _, _ in TAXONOMY] + [k for k, _ in EXTRA]
           + ["years_stated", "travel_pct_stated"])


def build_index(posts, collected="unknown"):
    """One row per collected posting, in collection order. No posting text."""
    inc = [include_reason(p["company"], p["title"]) for p in posts]
    groups = dedupe_groups(posts, [ok for ok, _ in inc])
    seen, rows = set(), []
    for p, (ok, why), g in zip(posts, inc, groups):
        rep = ok and g not in seen
        seen.add(g)
        row = dict(company=p["company"], title=p["title"].strip(), location=(p.get("location") or "").strip(),
                   url=p.get("url", ""), source=p.get("source", ""), collected=p.get("collected", collected),
                   included="y" if ok else "n", exclusion_reason=why, dedupe_group=g or "",
                   representative="y" if rep else "n")
        row.update(classify(p.get("text", "")))
        rows.append(row)
    return rows


def write_index(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("postings", help="JSON list of {company, source, title, location, url, text}")
    ap.add_argument("--out", default="postings-index.csv")
    ap.add_argument("--collected", default="unknown", help="collection date for postings without one")
    a = ap.parse_args()
    posts = json.loads(Path(a.postings).read_text(encoding="utf-8"))
    rows = build_index(posts, a.collected)
    write_index(rows, a.out)
    print(f"wrote {len(rows)} rows to {a.out}")


if __name__ == "__main__":
    main()
