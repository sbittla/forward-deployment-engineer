# ex84 hints · Workshop, code-with session and knowledge-transfer readiness

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Work in **minutes from midnight**, and convert to `HH:MM` only when you write a row: `f"{m // 60:02d}:{m % 60:02d}"`.
Keep two counters while you build the agenda: the current time, and the minutes since the start or the last break.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- For each objective: reject it if it has no lab, then append concept, demo, lab and the 5-minute check, advancing
  both counters.
- *After* each objective (never in the middle of one), if 90 or more minutes have passed since the last break and
  this isn't the last objective, add a 15-minute break and reset the counter.
- Check the total duration against `total_minutes` at the end.
- **lab_steps_valid:** one regex finds either a backtick-quoted command or one of the observable words.
- **readiness:** for each person, the objectives where quiz ≥ pass mark *and* the lab is done. Invert that into
  objective → list of ready people.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- In the sample, the first objective takes 75 minutes, so no break follows it. After the second, 135 minutes have
  passed, so a break goes in. Check the break after the objective, not after each block.
- No break after the last objective, even if 90 minutes have passed.
- A verify step like "Understand the design" fails: there's nothing a participant can observe.
- `can_operate_without_fde` needs **two** ready people on every objective. One person is a single point of failure.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_agenda` | Break inserted mid-objective or after the last; times not zero-padded |
| `test_agenda_validation` | Total duration not checked; zero-length lab accepted |
| `test_lab_steps` | Empty verify not flagged; observable words matched as substrings of other words |
| `test_readiness` | Quiz pass alone counted as ready (lab ignored); readiness threshold of one person |
