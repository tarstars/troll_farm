---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T223526Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T221536Z-20260825-dance-cure-candidate-2-swap-correction.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: c2c69325cf5156d8a4ee0c88bf83f65b014a71b9
artifact_paths: ["claude_1/cure2/c12_idle_with_work.py", "claude_1/cure2/c12-report-2026-08-25.md", "claude_1/cure2/results/c12-idle-with-work.json", "claude_1/cure2/arm-instrument.rs", "claude_1/cure2/arm-ruleoff.rs", "claude_1/cure2/cure2-instrument-config.json", "claude_1/cure2/cure2-ruleoff-config.json", "claude_1/cure2/results/arm-equivalence.json", "claude_1/pipeline/p4b_gate.py", "claude_1/narrate5/narrate5.py"]
created_utc: 2026-08-25T22:35:26Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — a ruling is required before C-12 can close

# C-12 — **`--p4b` is NOT_EVALUABLE on this candidate's wire**, and the accepted computation with the decoder swapped says **per-troll BLOCK / corpus PASS with every figure improved by the rule**

Runner `claude_1/cure2/c12_idle_with_work.py`, report `claude_1/cure2/c12-report-2026-08-25.md`,
packet `claude_1/cure2/results/c12-idle-with-work.json`, at `agent/claude_1@c2c69325`. Two verdict
fields, and I will not collapse them into one.

## 1. I turned the flag on and it could not read the wire

`--p4b` ON on both arms returns **`GATE_UNREADY` with 172 364 evaluator errors each**. That is an
instrument failure, not a verdict, and specifically not a 0.0 % pass. Two independent causes,
measured rather than argued:

1. **Version refusal.** `p4b_gate` reads the branch with `import narrate4` — `p4b_gate.py:387`
   (CLI) and `fuzz_panel.py:2443-2444` (the `--p4b` wiring). These arms narrate **v5**, and
   `narrate4.decode` refuses every non-v4 payload, so every telemetry row of every game is a decode
   error. Positive controls on a real payload off this corpus (`m000:0`, turn 1): **G-A1**
   `narrate4.decode` raises `unsupported NARRATE version 'v5'` — the refusal names the version;
   **G-A2** `narrate5.decode` reads the same bytes cleanly. The gate cannot read this wire and the
   wire is not at fault.
2. **A numerator half dead by grammar.** The definition counts `branch in {H, W}`, and **v5 retires
   `H`** — off-grammar in `narrate5.BRANCH_CODES` (`"PLRWNSX"`), control C-9's pre-committed
   "no `H`". **G-H measured 0 `H` turns** over 76 748. A version-agnostic decoder fixes cause 1 and
   leaves cause 2 standing.

`evaluate_rows` **already takes its narrator as a parameter**; only the two call sites hardcode it.
That is the locus, and naming it is as far as I go: the amendment is yours, and I changed nothing.

## 2. The accepted computation, decoder swapped — the number C-12 should be read on

Everything in `p4b_gate` but the narrator argument (`concrete`, `progress_event`, `maximal_runs`,
W=60, the tripwire, `compare`) is grammar-independent, so I re-drove **your evaluator** with
`narrate5` in its narrator slot — same function, same rows, **nothing restated**. **G-X** requires
its per-unit share to equal an independent tally on all 768 unit lives, and to equal `narrate5`'s
own census; both hold.

| | instrument (rule ON) | ruleoff (rule OFF, α-identical to the champion) |
|---|---|---|
| status | READY, 0 errors | READY, 0 errors |
| corpus idle share | **0.3818 %** | **0.7323 %** |
| per-troll maximum | **11.50 %** (`m101:0` u0) | **95.00 %** (`m059:0` u2) |
| unit lives above the 1.5 % bar | **25 / 384** | **28 / 384** |
| parked-unit episodes (W=60) | **16** | **27** |
| tripwire (run ≥ 45, no episode) | 0 | 0 |
| `compare(ruleoff → instrument)` | **PASS** — `added_unit_keys: []`, 11 removed | — |

**The bar is breached, and not by the candidate.** All 25 above-bar unit lives on the candidate arm
are above the bar on the rule-off arm too; the instrument-only set is **empty**, and the rule-off
arm has three more. The rule adds no above-bar troll on this corpus and removes three, across 7
games (`m059:0`, `m059:1`, `m061:0`, `m063:1`, `m070:1`, `m082:1`, `m110:1`).

## 3. The ruling I need, and will not make myself

"Per-troll idle-with-work share ≤ 1.5 %" reads two ways and they disagree:

- **per-troll** — the candidate arm **BLOCKS**, and so does the arm C-1 proved α-identical to the
  champion, by more. A bar the champion fails does not discriminate this candidate.
- **corpus-aggregate** — 0.3818 % ≤ 1.5 %, **PASS**, on both arms.

Both are published; I rule on neither. For the record my recommendation is that the defensible C-12
statement on this corpus is the **differential** — `compare` = PASS, no added parked unit, every
aggregate improved — but that is a definition change to an accepted gate and therefore yours.
**C-12 is not closed until the reading is ruled.**

## 4. Three things that must travel with the numbers

- **The 16 episodes do not travel alone.** **277 of 384** unit lives on the candidate arm are blind
  to the episode counter (`NONE` available in every 60-turn window), so it looked at 107 lives, not
  384. 268 blind on the rule-off arm. Same shape as the P3 read's orchard guard — a number small
  partly because the instrument was not looking. Longest-run distributions are identical on both
  arms (0 / 8 / 14 / 22 / 199), so the 27→16 difference is in the tail, not a population shift.
- **One figure runs the other way**: 52 candidate-arm unit lives carry at least one forced `W`
  against 49 on the rule-off arm, while total `W` turns fall 562 → 293 and the worst case 95 % →
  11.5 %. Fewer waits, spread slightly wider.
- **Two readings I measured and am NOT offering against the bar.** `W`∪`N` = **87.34 %** is not
  idleness: `N` is "no MOVE", and a `CHOP` is an `N`. Conditioning on a concrete target and no
  progress event does not rescue it (10.51 % vs 11.64 %) — a troll felling a tree over eleven turns
  registers no progress until the tree falls, so productive work counts as idle. **That failure is
  an argument for P4b's shape**: it is exactly why the accepted definition counts 60-turn episodes
  and not a per-turn share. On that invalid metric the candidate is two unit lives worse; I report
  it because it is the one figure in the run that moves against the rule.

## 5. Scope

The candidate arm emits no telemetry by construction and is **not evaluable by any wire-reading
gate**; everything here reaches it through **C-2**'s 240/240 byte-identity in play (**G-2B**) and no
further. Gates G-S / G-2B / G-A1 / G-A2 / G-H / G-X / G-V / G-K5 all pass and are tabulated in the
report. Re-run is byte-identical; the runner deletes its `/tmp` scratch on exit whatever the
outcome. This closes neither G-1 nor the owner's C-5 stop-and-ask, and authorises no Arena action.

This message also discharges my `20260825T221536Z` correction card, whose first deferred item was
C-12 with `--p4b` ON. A replacement card follows.
