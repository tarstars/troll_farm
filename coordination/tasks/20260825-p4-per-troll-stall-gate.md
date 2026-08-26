# 20260825-p4-per-troll-stall-gate: the panel's stall gate learns to see ONE parked troll (P4b)

- Status: **DELIVERED AND CLOSED 2026-08-25T18:45Z.** Wired by claude_1 (`agent/claude_1@31480089`):
  `--p4b` / `--p4b-baseline` on `fuzz_panel.py`, default OFF, report tier (no verdict authority);
  flag-off output identical except the file's own `referee_sha256` and wall time; flag-on champion
  re-run from source reproduces the R-2 baseline 27 / 27 / 16 with differential PASS; 166 + 9 tests;
  `stream_digest()` mtime-independent. codex_1's provenance erratum (decompressed-stream digests)
  integrated on `main` `6a8d4db0`. Named limitations: the baseline is an archive, not a live run;
  no-`games_dir` runs are reproducible but not re-readable; K-5 reported, not asserted, in the
  embedded packet; a `GATE_UNREADY` arm is not refused unless a charter says so. Recorded for the
  owner: P4/P4b cannot see a team that destroyed its own remaining work (`m061`). Candidate 2's G-1
  panel runs with `--p4b` ON. Earlier status follows.
- Status (18:2xZ): **G-1 ACCEPTED 2026-08-25T18:08Z — integration ordered 18:2xZ.** G-0 r1
  `DEFINITIONS_ACCEPTED` (claude_1, 17:20Z; R-1 unit-keyed differential, R-2 blind population, R-3
  the 45-turn flicker tripwire); G-1 delivered by codex_1 17:42Z (`agent/codex_1@e9103cc2`,
  packet `7039deec…`) and **REPRODUCED byte-identical** by claude_1 (`agent/claude_1@4529de36`;
  poison P-a regenerated field-for-field; K-1 verified off the wire: `m014`/seat 1/unit 2 episode
  5–199). Results: champion **27 parked-unit episodes on 16 of 240 games** (the R-2 baseline);
  Candidate 1 arms 25 (remove `m061`/seat 0 units 0 and 2 — a 61-turn genuine idle that ends at
  the `turn ≥ 100` regeneration clause); **poison P-a BLOCKed** on the added key `m098`/seat 0/unit 0
  while its aggregate fell 27 → 26. K-3 tripwire not fired (max run 33 < 45) → `k = W = 60` stands.
  Orders: claude_1 wires `p4b_gate.py` into `fuzz_panel.py` behind a flag default OFF (flag-off
  byte-identical), Candidate 2's panel with it ON; codex_1 re-issues archive pins as decompressed
  digests (gzip mtime erratum). Recorded: P4/P4b are blind to a team that destroyed its own
  remaining work (`m061`). Task closes when the wiring lands. Original status follows.
- Status at charter: **OPEN — CHARTERED 2026-08-25T16:05Z by owner ruling** ("charter it", coordinator
  session ~15:55Z — the coordinator's transcription).
- Record owner: local_claude_1 · Work owner: **codex_1** (build) · Reviewer: **claude_1** (it
  owns the pipeline; G-0 definitions, G-1 execution from a fresh archive) · Integrator:
  local_claude_1.
- Area: the local test panel's gates (`claude_1/pipeline/fuzz_panel.py:33-44`, gate P4). No bot,
  no Arena.
- Inputs: the defect record — Candidate 1's G-1 (`claude_1/cure1/g1-report-2026-08-25.md`): a
  poison arm that parked a troll for **194 turns** beside a working teammate passed P4, because
  P4 is game-level (no progress for our *side* in a rolling 60-turn window); the interim safety
  net `claude_1/cure1/idle_share.py` (per-troll idle-with-work share, line 1.5 %); the poison arms
  `claude_1/cure1/poison-p-a-*.rs`, `poison-p-b-*.rs` and `poison_arm.py`; the v3/v4 `available`
  field (what the picker offered the troll); the 240-game panel and the 34 fixtures.
- Branch: agent/codex_1 (work), agent/claude_1 (review), agent/local_claude_1 (record).
- Progress lease: 15 minutes without concrete evidence.
- Created UTC: 2026-08-25T16:05:00Z · Last updated UTC: 2026-08-25T16:05:00Z

## THE QUESTION (plain words)

The panel's stall gate asks "did our *team* stop making progress for 60 turns?" — so one troll
standing idle for 194 turns while its teammate keeps working is invisible to it. We need a gate
that asks the question **per troll**: "did *this* troll, with work available to it, do nothing for
a long time?" — and that catches the known poison arm.

## The predicate — the spine; G-0 fixes the exact text

`P4b` per own troll over the panel game: a troll **stalls** when, over a rolling window of `W`
turns (`W = 60` to match P4, or justified otherwise), it makes **no progress event** (the accepted
`progress()` predicate of `dance_facts.py`: nothing chopped, picked, dropped, planted, banked)
**and** it had **available work** on at least `k` of those turns (the panel's oracle: a real
target the picker could have given it — the v3/v4 `available` field where telemetry exists; the
generator's candidate list on the panel). A game **fails** `P4b` if any own troll stalls; the gate
for a candidate is "no new `P4b` failure versus the base arm on the same seed" (the same shape as
P4's "not above base"), every changed game named. Both a per-game boolean and the worst troll's
stall length are published.

**Controls (each with its number):** (K-1, positive) the Candidate 1 poison arm P-a (a troll parked
194 turns) **must fail** `P4b`; (K-2, negative) the champion base arm's panel verdicts: `P4b`
failures listed and bounded (the base does park trolls — R-2's benching class; the count is the
baseline, not zero); (K-3) idle-with-work share cross-check: every troll above 1.5 % on the panel
is either a `P4b` failure or explained; (K-4) determinism; (K-5) exhaustiveness over the 240 games
× seats × trolls.

## Gates

- **G-0 (claude_1, ack-required):** the predicate text, `W`, `k`, the oracle for "available work",
  the base-vs-candidate rule, the controls. `DEFINITIONS_ACCEPTED` / `REVISION_REQUIRED`.
- **G-1 (codex_1 builds; claude_1 reproduces from a fresh archive):** the gate in the pipeline
  behind a flag, the 240-panel run for base and for the Candidate 1 arms (as-built, revised, poison
  P-a/P-b), the controls, determinism; a short report.

## Deliverables

`codex_1/p4b/definitions-g0-2026-08-2x.md`; the code change in `claude_1/pipeline/fuzz_panel.py`
(or a sibling module, per G-0) delivered as a patch under `codex_1/p4b/` for claude_1 to integrate
into its pipeline; `codex_1/p4b/results/*.json`; `codex_1/p4b/g1-report-2026-08-2x.md`;
`claude_1/reviews/p4-per-troll-stall-gate-*.md`.

## Exclusive write set / do not touch

codex_1: `codex_1/p4b/**` · claude_1: `claude_1/pipeline/**` (integration after acceptance),
`claude_1/reviews/p4-per-troll-stall-gate-*.md`. Do not touch: any bot source, `cgauto/submissions/**`,
the resident, the cron, `data/raw/games/`. No Arena action.

## Handoff

codex_1 → claude_1 at G-0 and G-1 (ack-required, full commit + paths + digests); claude_1 →
codex_1 + local_claude_1 with rulings; Candidate 2's G-1 uses `P4b` as soon as it is accepted.
