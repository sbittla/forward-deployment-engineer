# ex48 · Voice agent transcripts: turns, barge-in, latency

**Module:** m08 · **Covers:** R32 Voice / multimodal AI, R15 Observability · **Time:** 50 min

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
