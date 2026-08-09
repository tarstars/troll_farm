# 20260810-manifest-implementation: make the bot's intentions legible — four items, allocated

- Status: open — owner-directed 2026-08-10
- Record owner / integrator: local_claude_1
- Manifest: `docs/MANIFEST-score-transparency-2026-08-09.md` (annotated with its own corrections)
- Reviews that shaped this: `chatgpt_1` `20260809T183000Z`, `claude_1` `20260809T223000Z`
- Base commit: 3b6d6405b6d1

## What the reviews changed before we start

Both peers independently corrected the manifest's premise, and the plan reflects the corrected
version, not the original:

- **The bot is not "weights on actions."** It is a pipeline — mode selection, candidate
  generation and filtering, scoring, pair compatibility, forced replacement, post-selection
  movement rewriting, commitment updates. **Weights are roughly a third of the decision.** A
  static intention→number table would document that third and leave the eligibility and
  planner/resolver opacity that caused the oscillation misdiagnoses. **The static bridge is
  therefore demoted, not deliverable one.**
- **Deliverable one is the Decision Packet** (`chatgpt_1`'s proposal, adopted).
- **Point 6's audit is a static-analysis problem, not a reading problem.** Both of the
  coordinator's worked examples were refuted: the chop maximum is 2400 not 3900 (`turns >= 2`
  always; the `.max(1)` is dead), and the band is not caller-set (one call site each, literals
  `6_100.0` / `6_000.0`). Both errors came from reading the right file and reasoning wrongly —
  treating a written bound as attainable, and inferring variability from a parameter's existence.
  **Neither would have been prevented by a bridge.** What would: reachable ranges and call-graph
  facts. That is now a required capability, not a nice-to-have.

## Sequencing — do not disturb the critical path

`20260809-referee-train-repair` r2 is delivered and awaiting `chatgpt_1`'s acceptance review. The
panel is `GATE_UNREADY` until that lands, and **it outranks everything here.** No item below may
delay it.

## Items

### M1 — Decision Packet — *deliverable one*

One code-generated, versioned packet explaining a single turn's decision. Per `chatgpt_1`'s
specification it must expose: modes and candidate generators entered; **every candidate and its
exclusion reason**; intent, semantic target, predicted landing, priority class and score terms;
pair compatibility and stock-rejection reasons; the selected pair and its alternatives; the
command **before and after** resolver rewriting with a typed reason; and realised execution where
an accepted referee exists.

**Added requirement, from the coordinator's own refuted examples:** each score term must carry
its **attainable range** given real input bounds, not merely its value. A packet that had shown
`turns ∈ [2, ∞)` would have prevented the 3900 error outright.

- **Spec: `local_codex_1`** — reassigned 2026-08-12 from `chatgpt_1` (out of reach). `chatgpt_1`
  proposed the packet, and its published proposal stands as the starting text; `local_codex_1`
  owns it from here. No execution needed. **Start only after the TRAIN r2 review is delivered.**
- **Implement: `claude_1`** — execution, and it owns the pipeline.
- **Review: `local_claude_1`** (execution) and `local_codex_1` (conformance to the spec).
  Reassigned 2026-08-12. Note this is now "conformance to the spec it inherited" rather than
  "to its own spec" — a weaker check, since the reviewer no longer authored the intent.

### M2 — Ratify the score-hierarchy audit

`claude_1` has already produced it: 10 boundary crossings (8 measured end-to-end), 3 hierarchy
inversions, 3 pieces of dead scoring code, a two-tier structure banded above `6_000` and
unbanded below, and a largest crossing that is **temporal** — conversion priced `<= 187.5` on
turn 250 and `7_000` on turn 251.

This item is **review and ratification, not new analysis**. Required: an adversarial review by an
agent that did not author it; the coordinator re-verifies a sample by execution; and the
**method** is written down so the audit is repeatable when the code changes — otherwise it rots
exactly like D-6's design document did.

- **Author: `claude_1` (done).** **Review: `local_codex_1` + `local_claude_1`** — reassigned
  2026-08-12 from `chatgpt_1`. `chatgpt_1`'s earlier rounds of this review were delivered and are
  already folded into revision 2; what transfers is the *open* adversarial pass on rev 2, not the
  closed history.

### M3a — Freeze the oscillation situation library

Turn the **34 episodes across 32 games** into inspectable, replayable situations: map, seat,
unit, turn range, the two cells, the full state at entry, and what the blocking peer was doing.
Mechanical and independent of everything else.

- **Owner: `claude_1`** — **DELIVERED** 2026-08-10, library `5858d351…`, 33 situations /
  47 episodes, 40/40 tests. Produced the finding that changed the cure: all 20 terminal episodes
  have an **IDLE** blocker, and none with a working blocker reaches 62 turns.
- **INDEPENDENT SECOND IMPLEMENTATION — assigned to `chatgpt_1` 2026-08-10, and its extraction
  was delivered before the agent went out of reach.** Per `claude_1`'s
  `20260811T193000Z` handoff, the re-extraction on the corrected subject `98628e98` reaches
  three-way agreement at **34 situations / 32**, ledger SHA `8e05b8ae…`, so the 38% gap is
  closed and this slot needs no reassignment. **Still open and reassigned to `local_codex_1`
  2026-08-12: the independent test of the idle-blocker finding**, which redirects the entire
  repair and still rests on one unreplicated extraction. Committed artifacts only; no execution
  required. Must not read `claude_1`'s library before publishing its own.

### M3b — Independent adjudication *(blocked on M1 and M3a)*

For each frozen situation, decide **independently what the best action would have been**, then
compare with what the combined score actually chose and why.

This is the manifest's most valuable item and the one we have never attempted: it asks whether a
decision was **correct**, where every check we own today asks only whether it **oscillated**.

- **Owner: split — `local_codex_1` adjudicates, `claude_1` supplies packets** (adjudicator
  reassigned 2026-08-12 from `chatgpt_1`, out of reach). The adjudicator must **not** be the
  agent that built the packet generator, or we are grading our own homework. `local_codex_1`
  satisfies that: it does not own the packet pipeline.

## Boundaries

Tooling and analysis only. **No bot, candidate, detector predicate, gate, host value protocol,
TestSession, submission, or Arena action.** The resident stays `fff6669b`; the candidate stays
`98628e98`. Any change to `trace_detectors.py` or the acceptance gate is out of scope here and
belongs to Phase 1.

## Why this ordering

The oscillation exercise produced its decisive finding because one agent measured what the
*blocking* troll was doing — a question the brief never asked. That was luck arising from
independence. **M1 exists to make that kind of finding routine rather than lucky**, and M3b is
the first thing that consumes it.
