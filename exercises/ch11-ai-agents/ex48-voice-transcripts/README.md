# ex48 · Voice agent transcripts: turns, barge-in, latency

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R32 Voice / multimodal AI, R15 Observability

## Learning objectives
- Turn a voice call event log into segments, turns and latency metrics.
- Measure response latency, barge-ins and silences.
- Report conversational quality in numbers a contact-centre lead understands.

## Scenario
Voice-agent FDE roles (contact centres, healthcare intake, drive-through ordering) live and die by conversational
latency and interruption handling. The customer says "the bot feels slow and talks over people". Turn that feeling
into numbers from the call event log.

## Events
`{"t": seconds, "speaker": "caller"|"agent", "type": "start"|"end"|"text", "text": str}` — `start`/`end` bound a
speech segment; `text` events carry the transcript for the segment currently open for that speaker.

## Your task
1. `segments(events) -> list[Segment(speaker, start, end, text)]` — sorted by start; texts of a segment joined with
   a space. Ignore an `end` with no open segment; an unclosed segment ends at the last event time.
2. `turns(segs) -> list[Segment]` — merge consecutive segments by the same speaker (gap irrelevant), joining text
   with a space.
3. `response_latencies(segs) -> list[float]` — for each agent segment that starts after a caller segment ended
   (and the previous segment overall was the caller's), `agent.start - caller.end`, rounded to 3 dp.
4. `barge_ins(segs) -> list[float]` — times when a caller segment starts while an agent segment is in progress
   (`agent.start < caller.start < agent.end`).
5. `call_metrics(events, silence_threshold=3.0) -> dict` with keys `latency_p50`, `latency_p95` (nearest-rank
   percentile; `None` if no latencies), `barge_in_count`, `agent_talk_ratio` (agent talk time / total talk time,
   3 dp), `long_silences` (count of gaps between consecutive segments, any speaker, longer than the threshold).
6. `to_transcript(turns) -> str` — `"Caller: ...\nAgent: ..."`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch11-ai-agents/ex48-voice-transcripts`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch11-ai-agents/ex48-voice-transcripts`: all 6 pass.
- **Tests:** `test_voice.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Metrics come from one call's clean, ordered event log. Production handles missing and
  out-of-order events and clock skew between telephony and speech services, aggregates percentiles across many calls,
  and treats recordings and transcripts as personal data under the customer's retention policy.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Voice agent transcripts: turns,
barge-in, latency". Before I write code, teach me voice agent pipelines (ASR, LLM, TTS), conversational latency,
barge-in, and turn-taking metrics. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex48-voice-transcripts/starter.py so that test_voice.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Segment`,
`segments`, `turns`, `response_latencies`, `barge_ins`, `call_metrics`, `to_transcript`. Constraints: Python 3.11+,
the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not
modify the tests or fde_kit. When you're done, run `pytest exercises/ch11-ai-agents/ex48-voice-transcripts` and show
me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Voice agent transcripts: turns, barge-in, latency" as a senior forward deployed engineer
would before it ships to a customer. Specifically: Are unclosed segments and stray end events handled? Is
nearest-rank percentile implemented exactly? Which metric best captures 'the bot talks over people'? Rank findings
by customer impact, quote the line for each, and say which ones a test should catch.
```
