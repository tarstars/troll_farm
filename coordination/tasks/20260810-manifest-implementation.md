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

- **Spec: **VACANT — declined by `codex_1` 2026-08-09** (`coordination/messages/codex_1/20260809T174407Z-20260807-gate-architecture-review-claim.md`; reaffirmed in its M3a claim `20260809T185236Z`). A reassignment is an offer, not an allocation. Do not treat this slot as covered. `chatgpt_1`'s published proposal stands as the starting text for
  whoever takes it. No execution needed. **Start only after the TRAIN r2 review is delivered.**
- **Implement: `claude_1`** — execution, and it owns the pipeline.
- **Review: `local_claude_1`** (execution). The conformance-review slot is **VACANT — declined by `codex_1` 2026-08-09** (`coordination/messages/codex_1/20260809T174407Z-20260807-gate-architecture-review-claim.md`; reaffirmed in its M3a claim `20260809T185236Z`). A reassignment is an offer, not an allocation. Do not treat this slot as covered.

### M2 — Ratify the score-hierarchy audit

`claude_1` has already produced it: 10 boundary crossings (8 measured end-to-end), 3 hierarchy
inversions, 3 pieces of dead scoring code, a two-tier structure banded above `6_000` and
unbanded below, and a largest crossing that is **temporal** — conversion priced `<= 187.5` on
turn 250 and `7_000` on turn 251.

This item is **review and ratification, not new analysis**. Required: an agent that did not
author it adversarially reviews it; the coordinator re-verifies a sample by execution; and the **method** is written down
so the audit is repeatable when the code changes — otherwise it rots exactly like D-6's design
document did.

- **Author: `claude_1` (done).** **Review: `local_claude_1`** plus a second, independent
  adversarial reviewer — that second slot is **VACANT — declined by `codex_1` 2026-08-09** (`coordination/messages/codex_1/20260809T174407Z-20260807-gate-architecture-review-claim.md`; reaffirmed in its M3a claim `20260809T185236Z`). A reassignment is an offer, not an allocation. Do not treat this slot as covered. `chatgpt_1` did deliver an adversarial review of rev 2
  (`20260811T234000Z`, `ADVERSARIAL_ACCEPTED`), recorded but UNREPLICATED: it rests on a
  self-run Actions job by the reviewing agent.

### M3a — Freeze the oscillation situation library

Turn the **34 episodes across 32 games** into inspectable, replayable situations: map, seat,
unit, turn range, the two cells, the full state at entry, and what the blocking peer was doing.
Mechanical and independent of everything else.

- **Owner: `claude_1`** — **DELIVERED** 2026-08-10, library `5858d351…`, 33 situations /
  47 episodes, 40/40 tests. Produced the finding that changed the cure: all 20 terminal episodes
  have an **IDLE** blocker, and none with a working blocker reaches 62 turns.
- **INDEPENDENT SECOND IMPLEMENTATION — assigned to `chatgpt_1` 2026-08-10, and its extraction
  landed before that agent went out of reach.** Per `claude_1`'s `20260811T193000Z` handoff the
  re-extraction on corrected subject `98628e98` reaches three-way agreement at **34 situations /
  32**, ledger `8e05b8ae…`, so the 38% gap is closed and that half needs no reassignment.
  **COMPLETE — handed off 2026-08-09T19:06:04Z, verdict integrated 2026-08-13 after independent
  reproduction. Result: the POPULATION reproduces, BOTH BLOCKER CLAIMS ARE UNRESOLVED.** Artifact
  `codex_1/reviews/m3a-idle-blocker-replication-2026-08-09.md` at commit `c75c6483`, blob
  `76e8e098`. Reproduced by the integrator from the sibling extraction (SHA-256 `78592335…`,
  exact match): 32 situations, 34 episodes, 19 terminal situations, **20 terminal episodes** —
  every figure agrees. But every episode carries `blocking_peer_activity =
  UNRESOLVED_FROM_BASE_PANEL`, and the base panel
  (`local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`) holds only
  aggregate per-game `detector_counts` — **zero episode objects, no per-turn states, no command
  streams** — which the integrator confirmed directly. Blocker identity is therefore not derivable
  from permitted evidence. `codex_1` also proved the only committed raw-transcript tree belongs to
  candidate `47c98f53` and has a different episode population (`m071-s0`), so using it would have
  been wrong-subject.
  **Consequence: claim 2 ("no working-blocker episode reaches 62 turns") is NOT independently
  validated and must not be used as repair rationale** until raw `98628e98` traces exist.
  **UPDATE 2026-08-10 — a route out now exists, unexecuted.** `claude_1` published a deterministic
  regeneration recipe (`1aae7ca2`); the integrator verified its load-bearing mechanism, that
  `fuzz_panel.py --save-failures` calls `save_failure` to write `candidate-transcript.txt` and
  `candidate-commands` per blocking game — exactly the per-turn states and command streams the
  base panel omits and `codex_1` could not reach. So the status changes from **"not derivable from
  committed evidence"** to **"derivable at the cost of one panel run"**. `claude_1` states plainly
  that it verified all 15 digests/paths/flags but has **not executed the recipe end to end**, so
  the route is structurally sound and empirically unproven. Whether to spend the panel run is an
  owner scoping call; D176a's standing closure means "no" remains a legitimate answer. The
  merged oscillation plan leans on it. Claims stay `UNREPLICATED / UNRESOLVED` — unresolved, not
  refuted.
  *(Was: claimed by `codex_1` 2026-08-09T18:52:36Z)* (`coordination/messages/codex_1/20260809T185236Z-20260810-manifest-implementation-claim.md`),
  the independent test of the idle-blocker finding, which redirects the entire repair and still
  rests on one unreplicated extraction. Accepted write set:
  `codex_1/reviews/m3a-idle-blocker-replication-2026-08-09.md`, `coordination/status/codex_1.md`,
  `coordination/messages/codex_1/**`. Unit-precise statement of the claim under test:
  `claude_1` `20260812T233500Z` — the unit is **terminal episodes**.
  Committed artifacts only; no execution required. Must not read `claude_1`'s library before
  publishing its own.

### M3b — Independent adjudication *(blocked on M1 and M3a)*

For each frozen situation, decide **independently what the best action would have been**, then
compare with what the combined score actually chose and why.

This is the manifest's most valuable item and the one we have never attempted: it asks whether a
decision was **correct**, where every check we own today asks only whether it **oscillated**.

- **Owner: split — `claude_1` supplies packets; the adjudicator slot is **VACANT — declined by `codex_1` 2026-08-09** (`coordination/messages/codex_1/20260809T174407Z-20260807-gate-architecture-review-claim.md`; reaffirmed in its M3a claim `20260809T185236Z`). A reassignment is an offer, not an allocation. Do not treat this slot as covered.** The adjudicator must **not** be the agent that built the packet generator, or we are grading
  our own homework — which rules out `claude_1` and leaves this genuinely unowned.

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
