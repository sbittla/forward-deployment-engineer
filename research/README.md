# Forward deployed engineer posting sample: method and data

Every posting figure in the book (Sections 1.2, 1.3 and 17.1) comes from one sample of public job postings
collected on 18 October 2026. This folder lets you check those figures, see exactly how each was produced, and
repeat the method on postings you collect yourself.

| File | What it is |
|---|---|
| `postings-index.csv` | One row per collected posting: identifiers, inclusion decision, duplicate group and a 0/1 column per rule. No posting text. |
| `analyze_index.py` | Recomputes every published figure from the CSV alone and prints the table. |
| `classify.py` | The rules: inclusion, duplicate removal, boilerplate removal and the requirement patterns. Runs on raw text. |
| `scrape.py` | The collector used for the sample (public job-board APIs). |
| `test_classify.py` | Pins the false-positive fixes and checks that the CSV reproduces the book's numbers. |

**Licensing.** Posting text belongs to the employers, so it isn't published here. The CSV holds only what
identifies a posting (company board name, title, location, public URL, source) and the results of the rules. The
code in this folder is under the repository's code license.

## Reproduce the book's numbers

```bash
python research/analyze_index.py          # prints the sample funnel, the requirement table and the extra figures
python -m pytest research -q              # 14 tests, including two that check the CSV against the book
```

No network access or posting text is needed. The numbers are *computed*: keyword matches over the text of each
posting, rounded half up to one decimal place in the table and to whole percentages in the book.

## Collection

- **Date.** One run of `scrape.py` on 18 October 2026. Per-posting timestamps weren't recorded, so every row
  carries the run date in `collected`; the boards' own posting dates weren't collected.
- **Sources.** The public, unauthenticated job-board APIs of three applicant-tracking systems:
  Greenhouse (`boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true`), Lever
  (`api.lever.co/v0/postings/{board}?mode=json`) and Ashby (`api.ashbyhq.com/posting-api/job-board/{board}`).
- **Boards queried.** 146 company boards (53 Greenhouse, 14 Lever, 80 Ashby), listed in `scrape.py`: companies
  known in October 2026 to hire forward deployed or deployment engineers, plus AI-native companies likely to. Boards
  that don't exist or have no matching posting return nothing. Postings were found on 50 boards.
- **Title filter.** A posting is collected when its title matches
  `forward[\s-]*deploy|deployment engineer|\bFDE\b|deployed engineer` (case-insensitive).
- **Collection-time filters.** Postings with under 400 characters of text are dropped, and so is a second posting
  with the same company, title and location.
- **Not covered.** Companies that recruit only through their own careers sites, including most consultancies and
  systems integrators (the book uses their published role descriptions instead, and doesn't count them here),
  and LinkedIn or other job sites.

Result: 464 postings from 50 companies.

## Inclusion and exclusion

The book counts **individual-contributor (IC) engineering roles**. `include_reason()` in `classify.py` applies these
rules to the title, in order; the CSV's `exclusion_reason` column records which rule fired.

| Rule | Excluded | Why |
|---|---|---|
| Aggregator board (`jobgether`) | 37 | Re-posts other employers' roles, unnamed, once per country |
| Title names a non-IC or non-engineering function: manager, recruiter, product, strategist, engagement, program, director, GTM, leadership, partner manager, accelerator, data scientist, head of, RVP, vice president, deployment lead, engineering lead | 73 | Not an IC engineering role |
| Title names no engineering role (engineer, developer, architect, technical staff, deployed staff, FDE) | 17 | For example "Forward Deployed Banker" or "Forward Deployed Consultant" |
| "Finance engineer" | 3 | Harvey's Forward Deployed Finance Engineers are former investment professionals, not software engineers |
| **Included** | **334** | |

Interns, new graduates and senior, staff and principal engineers are included: they're IC engineering roles.
OpenAI's Deployment Leads are excluded as a delivery-lead role, although Chapter 1 quotes their posting.

## Duplicate removal

Many roles are posted once per city. Two included postings at the same company are one role when either:

1. their titles match once location-only qualifiers are removed ("Forward Deployed Engineer - London" and
   "Forward Deployed Engineer - Paris" are one role; "... - US Government" and "... - Healthcare" are not), or
2. their text is identical after lower-casing and collapsing whitespace.

A qualifier is location-only when every word in it is a place or region word: one of the words in the posting
location fields, or a fixed list (EMEA, APAC, NYC, SF and so on). Words that name a distinct role are never treated
as locations, even when they appear in a location field: government, public sector, federal, commercial, intel,
health, national security, early career and the language names in "Spanish-speaking" and similar.

Each group gets a `dedupe_group` id, and its first posting in collection order is the `representative` that
enters the denominators. Result: **157 unique roles at 44 companies**. All percentages are shares of these 157.

## Boilerplate removed before matching

`strip_boilerplate()` splits the text into lines and sentences and drops every one that matches the `BOILERPLATE`
pattern, then removes the job-title phrase. Removed:

- **The title phrase**: "forward deployed (software/AI/...) engineer(ing)", "deployment engineer", "deployed
  engineer", "deployment strategist", "FDE", "FDSE". Otherwise *deploy* in the title counts as production
  deployment in every posting.
- **Benefits**: health, medical, dental, vision, life, disability and pet insurance; 401(k); paid leave, PTO,
  vacation; HSA, FSA, HRA; fertility, wellness, stipends, perks, equity grants; travel budgets for visiting other
  offices and company offsites.
- **Equal-opportunity and legal notices**: EEO, "without regard to", protected classes, reasonable accommodation,
  disability, E-Verify, privacy notices, GDPR or CCPA notices about applicant data, immigration and posting
  compliance notices, and export-control notices (including "U.S. government license" and the "Compliance"
  heading above them).
- **Pay**: compensation, salary range, base pay, on-target earnings, pay transparency.
- **Office policy**: "If the posting is specified as Onsite, you are required to work from an office", in-office
  days, office culture, hybrid workplace, return to office, relocation and visa support.

## Requirement rules

A role counts for a requirement when the pattern matches anywhere in its stripped text. `classify.py` is
authoritative; this table is generated from it and from the CSV.

| ID | Requirement | % of roles | Pattern (case-insensitive) |
|---|---|---|---|
| R01 | Python proficiency | 70.1 | `\bpython\b` |
| R02 | TypeScript/JavaScript & full-stack web | 66.2 | `typescript\|javascript\|react\|node\.?js\|full[- ]?stack\|frontend\|front-end` |
| R03 | SQL & data modeling | 18.5 | `\bsql\b\|postgres\|data model\|schema\|data warehouse\|bigquery\|relational` |
| R04 | Data pipelines / ETL / Spark | 42.7 | `\betl\b\|elt\b\|pipeline\|spark\|airflow\|dbt\b\|ingest\|streaming\|kafka` |
| R05 | APIs & system integration | 66.9 | `\bapis?\b\|integrat\|\brest(ful)?\b\|graphql\|webhook\|\bsdks?\b` |
| R06 | Cloud platforms (AWS/GCP/Azure) | 52.9 | `\baws\b\|\bgcp\b\|azure\|google cloud\|cloud (platform\|infrastructure\|provider)` |
| R07 | Containers, Kubernetes, IaC, CI/CD | 37.6 | `docker\|kubernetes\|\bk8s\b\|terraform\|ci/cd\|containers?\|helm\|infrastructure as code\|devops` |
| R08 | LLM application development | 42.7 | `\bllms?\b\|large language model\|generative ai\|genai\|gpt\|claude\|foundation model` |
| R09 | Prompt & context engineering | 14.6 | `prompt\|context engineering\|system prompt` |
| R10 | RAG, retrieval, vector search | 25.5 | `\brag\b\|retrieval\|vector\|embedding\|semantic search\|search relevance` |
| R11 | Agents, tool use, orchestration | 56.7 | `\bagents?\b\|agentic\|tool[- ]use\|function calling\|orchestrat\|langgraph\|langchain\|multi-agent` |
| R12 | MCP (Model Context Protocol) | 6.4 | `\bmcp\b\|model context protocol` |
| R13 | Evaluation & quality measurement | 41.4 | `\bevals?\b\|evaluation\|benchmark\|test harness\|golden (set\|dataset)\|quality metrics\|llm[- ]as[- ]a[- ]judge` |
| R14 | Guardrails, safety & responsible AI | 20.4 | `guardrail\|safety\|responsible ai\|hallucinat\|red[- ]team\|jailbreak\|pii` |
| R15 | Observability, monitoring & reliability | 42.0 | `observab\|monitor\|logging\|tracing\|reliab\|incident\|on[- ]call\|sre\b\|uptime\|latency` |
| R16 | Fine-tuning / ML fundamentals | 33.8 | `fine[- ]tun\|machine learning\|\bml\b\|model training\|pytorch\|reinforcement\|deep learning` |
| R17 | Security, auth & compliance | 73.2 | `security\|secure\|\bauth(n\|z\|entication\|orization)?\b\|\bsso\b\|oauth\|compliance\|soc ?2\|hipaa\|fedramp\|clearance\|rbac\|encryption` |
| R18 | Customer discovery & requirements | 89.2 | `discover\|requirements\|scop\|understand (their\|customer)\|business problem\|use cases?\|workflows?` |
| R19 | Stakeholder communication & exec presence | 93.0 | `communicat\|stakeholder\|executive\|c-suite\|\bpresent\|storytell\|articulat\|non-technical` |
| R20 | Ownership, ambiguity & bias to action | 86.0 | `ownership\|ambigu\|scrappy\|bias (for\|to) action\|autonomy\|autonomously\|self-starter\|fast-paced\|end-to-end\|zero to one\|0 to 1` |
| R21 | Rapid prototyping & demos / POCs | 37.6 | `prototyp\|proof[- ]of[- ]concept\|\bpocs?\b\|\bdemos?\b\|pilot\|mvp` |
| R22 | Production deployment & hardening | 89.8 | `\bproduction\b\|\bdeploy(s\|ed\|ing\|ment\|ments)?\b\|\bship(s\|ped\|ping)?\b\|harden\|go[- ]live\|\blaunch` |
| R23 | Product feedback loop to core eng | 74.5 | `feedback\|product (team\|roadmap)\|inform (the )?roadmap\|core (product\|platform)\|reusable\|productiz` |
| R24 | Technical writing & enablement | 68.8 | `documentation\|playbook\|technical writ\|best practices\|enablement\|workshop\|training\|knowledge base\|runbook` |
| R25 | Domain/industry context (regulated) | 35.7 | `financial services\|healthcare\|life sciences\|public sector\|government\|defense\|insurance\|regulated` |
| R26 | Travel & on-site embedding | 66.2 | `(?<!\w)travel(?!\s+(software\|industry\|tech\|and hospitality\|& hospitality\|booking))\|on[- ]site\|onsite\|customer site` |
| R27 | Performance, cost & latency optimization | 59.9 | `cost\|latency\|throughput\|optimi[sz]\|token\|performance` |
| R28 | Distributed systems & backend architecture | 48.4 | `distributed (systems?\|computing\|services)\|\bback[- ]?end\b\|microservices?\|system design\|(software\|systems?\|backend\|service\|solution) architecture` |
| R29 | Debugging & troubleshooting in customer env | 35.7 | `debug\|troubleshoot\|root cause\|triage\|unblock` |
| R30 | Delivery against measurable value | 40.8 | `\broi\b\|business (value\|impact\|outcomes)\|\bkpis?\b\|success metrics\|milestones?\|measurable (value\|impact\|outcomes\|results\|business)\|time[- ]to[- ]value\|value realization` |
| R31 | Data platforms (Databricks/Snowflake/lakehouse) | 26.1 | `databricks\|lakehouse\|delta lake\|snowflake\|unity catalog\|ontology\|foundry` |
| R32 | Voice / multimodal AI | 10.8 | `\bvoice\b\|speech\|audio\|multimodal\|computer vision\|telephony\|\bivr\b` |
| R33 | Delivery management, SOWs & project plans | 7.0 | `statement of work\|scopes? of work\|\bsow\b\|project plans?\|milestones?\|acceptance criteria\|critical path\|dependencies\|delivery plan` |
| R34 | Adoption & change management | 47.1 | `change management\|adoption\|onboarding\|drive usage` |
| R35 | Customer enablement & teaching | 28.0 | `workshops?\|train(ing)? (customers\|users\|teams\|operators)\|teach\|enablement\|code-with\|knowledge transfer\|instructor` |
| R36 | Vendor AI platforms & SDKs (multi-provider) | 6.4 | `bedrock\|vertex\|azure openai\|ai foundry\|agents? sdk\|responses api\|agent skills?\|sub-?agents?\|multi[- ]provider\|model[- ]agnostic\|claude api\|openai api\|anthropic api\|gemini` |
| R37 | AI-assisted engineering (coding agents) | 8.9 | `claude code\|cursor\|github copilot\|ai coding\|coding agents?\|ai-assisted (coding\|development)\|agentic development` |
| R38 | Document & multimodal AI | 9.6 | `multimodal\|\bocr\b\|document (processing\|understanding\|intelligence\|extraction)\|\bpdfs?\b\|images?\|vision models?` |
| R39 | Identity & permission-aware access | 9.6 | `\bsso\b\|okta\|entra\|saml\|oidc\|identity\|permissions?\|access control\|least privilege` |
| R40 | Technical leadership & design review | 24.8 | `mentor\|tech(nical)? lead\|design reviews?\|architecture reviews?\|code reviews?\|lead (a )?(team\|pod)\|\bpods?\b\|technical direction` |
| R41 | AI security assessment & red teaming | 3.8 | `red[- ]team\|jailbreak\|adversarial\|prompt injection\|ai security` |
| R42 | Ontology & semantic modeling | 5.1 | `ontology\|knowledge graph\|semantic (layer\|model)\|data model(l)?ing\|object model` |
| R43 | Regulatory & compliance frameworks | 24.8 | `gdpr\|hipaa\|soc ?2\|fedramp\|iso ?27001\|eu ai act\|\bpci\b\|\bsox\b\|compliance\|regulatory\|\bgrc\b` |
| R44 | Incident response & postmortems | 12.1 | `incidents?\|on[- ]call\|postmortems?\|post-mortems?\|root cause` |
| aws | AWS named | 35.7 | `\baws\b\|amazon web services` |
| azure | Azure named | 30.6 | `\bazure\b` |
| gcp | Google Cloud named | 28.7 | `\bgcp\b\|google cloud` |
| clearance | Security clearance mentioned | 28.7 | `clearance` |

**Extra figures.**

- `years_stated`: every distinct year figure in phrases like "5+ years" or "3-5 years" (the lower bound of a range),
  between 1 and 19. The book reports, per figure, how many roles state it, and how many roles state 8 or more.
- `travel_pct_stated`: every percentage in a 60-character window around "travel", including both ends of a range
  ("25-75%"). The book reports the highest stated figure per role.
- Clearance counts any mention: required, preferred or "eligible to obtain".

## How ambiguous wording is handled

- A mention counts whether it's required, preferred or descriptive ("you'll work with healthcare customers"). The
  figures say how often employers *mention* a topic, not how often they require it.
- A company description counts when it's part of the posting text (for example, a list of customer sectors).
- One posting per role: a role posted in nine cities counts once, using the first posting's text.
- No weighting by company: Palantir has 37 of the 157 roles and Databricks 27, so their wording weighs heavily.

## Known false positives and limits

Checked by reading the matched context for the patterns the book cites. Remaining known issues:

- **R22** counts infrastructure deployments ("tooling deployment") as production deployment.
- **R25** counts company descriptions that list government or healthcare customers, even when the role doesn't
  serve them.
- **R26** counts "travel as needed" without saying where; it no longer counts office-attendance policy.
- **R30** can match employer boilerplate such as "the business impact of our employees".
- **R37** counts Cursor's own postings, because the product name is the pattern.
- **R34** counts "adoption of AI" in company mission statements as well as customer adoption work.
- **Boilerplate removal** drops a whole sentence, so a requirement sentence that also mentions benefits or
  compensation is lost.
- **Patterns are English-only.** Postings in other languages are under-counted.
- **One day, one set of boards.** The sample is a snapshot, not a trend or the whole market.

## Changes from the book's version 1.1.0 figures

The first published version (1.1.0) used 249 roles and looser rules. A review found that *deploy* matched the job
title, *architect* and *deliver* matched generic wording, *connector* counted as MCP, *rest* matched "interest",
*enable* matched any enabling, *autonom* matched "autonomous systems", benefits text counted as the healthcare and
insurance sectors, office policy counted as travel, export-control notices counted as government and compliance,
and city-suffixed titles (OpenAI's "FDE - London") escaped duplicate removal. Version 1.1.1 fixes these:

| Figure | 1.1.0 | 1.1.1 |
|---|---|---|
| Unique IC engineering roles | 249 (48 companies) | 157 (44 companies) |
| R22 Production deployment | 100% | 90% |
| R28 Distributed systems and backend architecture | 84% | 48% |
| R05 APIs and integration | 79% | 67% |
| R17 Security and authentication | 71% | 73% |
| R01 Python | 66% | 70% |
| R02 TypeScript or full-stack | 60% | 66% |
| R19, R18, R20 Communication, discovery, ownership | 90% to 94% | 86% to 93% |
| R30 Delivery against measurable value | 78% | 41% |
| R11 Agents and tool use | 55% | 57% |
| R08, R13 LLM application development, evaluation | about 45% each | about 42% each |
| R10 Retrieval, R14 guardrails | about a quarter each | 26%, 20% |
| R09 Prompt and context engineering | about 1 in 6 | about 1 in 7 |
| R12 MCP | 6% (with "connector") | 6% |
| AWS, Azure, Google Cloud | 26% to 31% | 29% to 36% |
| R23 Feedback loop, R24 documentation and enablement | about 80% each | 75%, 69% |
| R26 Travel or on-site | 67% | 66% |
| R25 Regulated sector | 57% | 36% |
| R43 Regulatory frameworks | 44% | 25% |
| R34 Adoption and change management | 64% | 47% |
| Roles mentioning a clearance | 47 (30 Palantir) | 45 (28 Palantir) |
| Roles asking for 8+ years | 14 | 9 |

## Re-collect and re-run

```bash
python research/scrape.py --out postings.json                       # today's postings; keep the file private
python research/classify.py postings.json --out my-index.csv --collected YYYY-MM-DD
python research/analyze_index.py my-index.csv
```

Boards change daily, so expect different numbers. Differences larger than a few points on the same rules are
worth reading: open the postings that flip and check whether the rule or the market changed.
