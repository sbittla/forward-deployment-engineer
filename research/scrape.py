"""Pull Forward Deployed Engineer postings from public ATS job-board APIs.

Sources: Greenhouse boards API, Lever postings API, Ashby posting API.
Output: a JSON list of {company, source, title, location, url, text}; default ./postings.json.
This is the collector used for the book's 18 October 2026 sample. Boards change daily, so a re-run collects a
different sample: classify it with classify.py and compare with analyze_index.py. Don't commit the output to a
public repository; the posting text belongs to the employers.

    python research/scrape.py --out postings.json
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TITLE_RE = re.compile(r"forward[\s-]*deploy|deployment engineer|\bFDE\b|deployed engineer", re.I)

GREENHOUSE = [
    "anthropic", "scaleai", "databricks", "gleanwork", "cresta", "samsara", "airtable",
    "anduril", "shieldai", "brex", "figma", "stripe", "vercel", "datadog", "mongodb",
    "elastic", "gitlab", "twilio", "intercom", "asana", "notion", "rubrik", "abnormalsecurity",
    "chime", "affirm", "robinhood", "coreweave", "lambdalabs", "togetherai", "fireworksai",
    "runwayml", "assemblyai", "deepgram", "observeai", "moveworks", "hightouch", "dbtlabsinc",
    "tecton", "pinecone", "weaviate", "zapier", "retool", "watershed", "flexport", "rippling",
    "applied", "appliedintuition", "nuro", "verkada", "gusto", "faire", "mercury", "plaid",
]
LEVER = [
    "palantir", "mistral", "jobgether", "thinkahead", "anysphere", "zoox", "shieldai",
    "veeva", "netflix", "spotify", "attentive", "hive", "outreach", "kraken",
]
ASHBY = [
    "openai", "cohere", "sierra", "decagon", "harvey", "hebbia", "writer", "modal",
    "baseten", "langchain", "elevenlabs", "perplexity", "ramp", "hatch", "certa", "Cape",
    "parafin", "truelogic", "replit", "cursor", "cognition", "glean", "vanta", "linear",
    "llamaindex", "pydantic", "temporal", "supabase", "clay", "rogo", "basis", "tennr",
    "abridge", "ambiencehealthcare", "eudia", "legora", "unify", "11x", "artisan", "rilla",
    "distyl", "distylai", "tribe", "tribeai", "invisible", "turing", "sola", "rasa",
    "assembled", "cartesia", "vapi", "bland", "retellai", "hume", "anterior", "commure",
    "notable", "hippocratic", "ironclad", "spellbook", "evenup", "eve", "crosby", "factory",
    "imbue", "adept", "character", "runway", "suno", "pika", "luma", "together", "fireworks",
    "arize", "braintrust", "galileo", "humanloop", "weights-and-biases", "wandb", "scale",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 fde-research"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None


def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<li[^>]*>", "\n- ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def greenhouse(slug):
    d = get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
    out = []
    for j in (d or {}).get("jobs", []):
        if TITLE_RE.search(j.get("title", "")):
            out.append(dict(company=slug, source="greenhouse", title=j["title"],
                            location=(j.get("location") or {}).get("name", ""),
                            url=j.get("absolute_url", ""), text=clean(j.get("content"))))
    return out


def lever(slug):
    d = get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    out = []
    for j in d or []:
        if TITLE_RE.search(j.get("text", "")):
            parts = [j.get("descriptionPlain", "")]
            for l in j.get("lists", []):
                parts.append(l.get("text", "") + "\n" + clean(l.get("content", "")))
            parts.append(j.get("additionalPlain", ""))
            out.append(dict(company=slug, source="lever", title=j["text"],
                            location=(j.get("categories") or {}).get("location", ""),
                            url=j.get("hostedUrl", ""), text="\n\n".join(parts).strip()))
    return out


def ashby(slug):
    d = get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
    out = []
    for j in (d or {}).get("jobs", []):
        if TITLE_RE.search(j.get("title", "")):
            comp = (j.get("compensation") or {}).get("compensationTierSummary", "")
            out.append(dict(company=slug, source="ashby", title=j["title"],
                            location=j.get("location", ""), url=j.get("jobUrl", ""),
                            text=(j.get("descriptionPlain") or clean(j.get("descriptionHtml")))
                            + (f"\n\nCompensation: {comp}" if comp else "")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="postings.json")
    out = Path(ap.parse_args().out)
    tasks = [(greenhouse, s) for s in GREENHOUSE] + [(lever, s) for s in LEVER] + [(ashby, s) for s in ASHBY]
    with ThreadPoolExecutor(16) as ex:
        results = list(ex.map(lambda t: t[0](t[1]), tasks))
    postings, seen = [], set()
    for r in results:
        for p in r:
            key = (p["company"], p["title"], p["location"])
            if key not in seen and len(p["text"]) > 400:
                seen.add(key)
                postings.append(p)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(postings, indent=1, ensure_ascii=False), encoding="utf-8")
    by = {}
    for p in postings:
        by[p["company"]] = by.get(p["company"], 0) + 1
    print(len(postings), "postings from", len(by), "companies")
    print(json.dumps(by, indent=0))


if __name__ == "__main__":
    sys.exit(main())
