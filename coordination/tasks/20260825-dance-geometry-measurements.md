# 20260825-dance-geometry-measurements: is there a road around the standing teammate, and what stood on the dancer's next cell

- Status: **OPEN — CHARTERED 2026-08-25T13:50Z** under the owner-activated mission
  `coordination/GOAL.md` (owner, coordinator session 2026-08-25 ~13:30Z: *"create goal file for
  measurements you just mentioned"*, then `/goal coordination/GOAL.md` — the coordinator's
  transcription). **Measurements only**: no cure, no candidate, no bot change, no Arena action.
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1** (G-0 definitions
  *before any count*; G-1 execution reproduced from a fresh archive) · Integrator: per
  `coordination/roster.json` on `origin/main`.
- Area: the dance programme — evidence for the open Candidate 2 ruling (*swap the standing teammate
  once, or route around it*). No experiment id, no bot, no panel.
- Base commit: 3718d7ae95a2c4a0ef7f772b12ecc5c71f6af2a6 (trunk; carries the input note, its script
  and results under `local_claude_1/dance-geometry/`).
- Branch: agent/claude_1 (work), agent/codex_1 (review), agent/local_claude_1 (record).
- Progress lease: 15 minutes without concrete evidence (phase markers renew it).
- Created UTC: 2026-08-25T13:50:00Z · Last updated UTC: 2026-08-25T13:50:00Z

## THE QUESTION (owner's, plain words)

The instrumented real games say the dance is one mechanism: our troll wants a tree or the bank a
few cells away, its path runs through the cell where **our other troll stands still and works**,
and the mover — which plans blind to units and repairs one step at a time — steps *backwards*
whenever every free neighbour is farther from the goal; next turn it steps forward, is blocked
again, steps back. Two things are unmeasured and both decide what a cure should do:

- **M-1.** When the dancer is blocked by its standing teammate, **is there a road around the
  teammate at all, and how much longer is it?** If a road usually exists at small extra cost,
  routing around has room; if the corridor is one cell wide, only a swap (or the teammate moving)
  can end the dance.
- **M-2.** In the older read's short dances where **nobody of ours stood next to the dancer when
  the dance began** (25 of 80), **what was on the dancer's next cell on each backward step** — a
  standing teammate, a teammate passing through, or nothing of ours? The older read has no
  resolver letters; this count tests the "transient block" hypothesis (those dances went 25 of 80
  → 1 of 25 on the hold arm) on the read that lacks the letters.

## Outcome

One results file (every episode, every eligible turn, every control with its number) and one
owner brief, plain words, one page + two tables: for the teammate dances, how often a road around
exists and what it costs, beside how long the dances lasted; the M-2 count; what each answer means
for *swap* versus *route around* — stated as evidence. **The ruling stays the owner's.**

## Inputs (pinned — read, never modified)

| input | where |
|---|---|
| older read fact rows — 80 D-1 episodes, 469 games, NARRATE v2/v3 instruments | `agent/claude_1@4c92432fec98a847487b50763f54cce0bd2966f4:claude_1/dance1/results/dance-facts-instrument-2026-08-24.json` (sha256 `7cd3631c…`) |
| v4 read fact rows — 25 D-1 episodes, 160 games, NARRATE v4 instrument; `per_game[].episodes[]`, `v4_branch_sequence` = the mover's letters | `agent/claude_1@22d6b2bb2418eece82d67d154c33441bbd655519:claude_1/cure1/results/g2-grade.json` (sha256 `45f5f22a…`) |
| replays, batch 1 (149 games, agent 6652424, v2) | `local_claude_1/narrate/games/` on trunk (also at `3256dafb164dc17417ddb84e00909157f5eb763a`) |
| replays, batch 2 (160, agent 6652602, v2) | `local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz` (`84f46acb…18897`, manifest beside it) |
| replays, batch 3 (160, agent 6652642, v3) | `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz` (`01169944…c3ceb`) |
| replays, v4 read (160, agent 6659743) | `local_claude_1/cure1/g2-games/games-agent6659743-submission41192036.jsonl.gz` (`050d1ceb…c6a38`) |
| the coordinator's re-read (shapes `one-cell` / `adjacent` / `nobody`; the input hypothesis) | `local_claude_1/dance-geometry/re-read-2026-08-25.md`, `reread_shapes.py`, `results/reread-shapes-2026-08-25.json` at the base commit — **unreviewed; G-0 reviews it too** |
| the mover's step rule (reference) | `claude_1/cure1/cure1-hold-v4.rs` ~826–922: `next_cell`, `reserved`, the detour, the letters `P`/`L`/`H`/`R`/`W`/`N` |

Machinery to **import, never copy** (same discipline as the attribution task, asserted source
digests): `claude_1/adapter1/replay_to_trace.py` (map + per-turn units),
`claude_1/cure1/regressive_baseline.py` (`measure_game`: walkable map, `td.bfs_distances` seeded at
the target exactly as the arm does, the stated target per turn, v3/v4 joins),
`claude_1/narrate4/narrate4_join.py`, `claude_1/dance1/dance_facts.py` (`f3_peers`, `measure_blocker`).

## Definitions — the spine; G-0 fixes the exact text before any count

**Population.** Every D-1 episode of both reads — 80 + 25 = 105 — and, inside each, every window
turn on which the dancer has a stated cell target and a successor cell (the `R_pos` eligibility of
`regressive_baseline.measure_game`). Episodes and turns are never dropped silently; refusals are
listed with their reason.

**M-1, per eligible turn.**
- `d0` = BFS distance from the dancer's cell to its stated target on the bare walkable map — the
  arm's own metric: `bfs_distances(walkable, [target])`, Manhattan fallback when the cell is off
  that map, exactly as `cure1-hold-v4.rs:891/900` and `regressive_baseline.py` do it.
- `d1` = the same with the teammate's **current** cell removed from the walkable set (the teammate
  must be alive; if the teammate stands on the target cell itself, record `TARGET_OCCUPIED` and
  exclude from the cost table, counted separately).
- **teammate on every shortest road** ⇔ `d1 > d0`; **road-around cost** = `d1 − d0`, **∞** when the
  target becomes unreachable.
- **lateral exists** ⇔ some free orthogonal neighbour of the dancer's cell (walkable, not the
  teammate's cell) has distance ≤ `d0` — the arm's `L` branch; where it exists the arm would not
  step back.
- Per episode: share of eligible turns with `d1 > d0`; the median cost over those turns; a **cost
  class** `0 / 1–2 / 3–5 / >5 / ∞` from that median; the dance length and shape beside it.
- Headline tables (each read separately, then pooled with the read as a column): cost class ×
  shape (`one-cell` / `adjacent` / `nobody` from `reread_shapes.py`), cost class × dance length
  (`7–11 / 12–29 / ≥30` turns). One more line: the share of blocked turns on which a *lateral*
  step existed.

**M-2, per backward step of the older read** — a dancer step from cell `x` to cell `y` with
`d0(y) > d0(x)` toward the stated target at `x` — on all 80 episodes, headline on the 25 `nobody`:
what is on the dancer's forward cell (the arm's `next_cell` from `x` along `bfs`, or the Manhattan
fallback where the map lacks it) at that turn:
- (a) **standing** — an own unit on that cell this turn *and* the previous turn;
- (b) **transient** — an own unit that arrived this turn or last turn, or is moving away this turn
  (the arm's transient test);
- (c) **nothing of ours** — residual: record whether the forward cell is off the BFS map (fallback)
  and whether the stated target changed on that turn (planner flip).
Counts per episode and per shape; the residual (c) rows listed whole.

**Controls** (each fires with its number, or the result is not reported):
- **K-1 positive (v4 read):** a turn lettered `R` has the teammate's cell on the arm's forward step
  and `d1 > d0` — agreement ≥ 95 % expected; every disagreement explained (fallback rows first).
- **K-2 negative (v4 read):** a turn lettered `P` has a free forward cell.
- **K-3 poison:** walling a random walkable cell not adjacent to the dancer (seeded, deterministic)
  instead of the teammate's cell gives cost 0 on nearly every eligible turn — report the share.
- **K-4 determinism:** a second run into a separate directory is byte-identical.
- **K-5 exhaustiveness:** eligible + ineligible turns per episode reconcile with the window
  length; episode counts reconcile with the two fact files (80 and 25).
- **K-6 (M-2 on the v4 read):** the same predicate gives (a) on `R` turns and (b) on `H` turns;
  disagreements explained.
- **K-7 re-read identity:** the shapes used here reproduce `results/reread-shapes-2026-08-25.json`
  byte-for-byte from the pinned fact rows (`reread_shapes.py` at the base commit).

## Gates

- **G-0 — definitions (codex_1, before any count).** claude_1 publishes the exact predicates,
  eligibility, cost classes, controls and the file layout as `claude_1/geometry1/definitions-g0-2026-08-25.md`
  (revisions `-r2`, `-r3`…), with a reading of the coordinator's re-read note (agree / object, with
  reasons). codex_1 rules `DEFINITIONS_ACCEPTED` / `REVISION_REQUIRED`, **`requires_ack: true`
  toward claude_1**. Counting starts only after acceptance — or, if codex_1 has not answered within
  60 minutes of the ack-required request, with the published definitions marked *unreviewed* and
  definitions + execution reviewed together at G-1 (say so in the handoff).
- **G-1 — execution (codex_1, from a fresh archive).** claude_1 hands off the results JSON, the
  controls JSON, the scripts, and a short execution report `claude_1/geometry1/g1-execution-2026-08-2x.md`
  with the headline tables and every control's number; codex_1 reproduces byte-for-byte or names
  the difference; numbers are re-issued if anything moved.
- **Brief (local_claude_1).** The owner brief at `local_claude_1/dance-geometry/owner-brief-2026-08-2x.md`,
  every count re-derived by the coordinator from the published rows before it is written.

## Deliverables

- `claude_1/geometry1/definitions-g0-2026-08-25.md` (+ revisions) — G-0.
- `claude_1/geometry1/*.py`, `claude_1/geometry1/results/geometry-2026-08-2x.json` (whole),
  `results/controls-2026-08-2x.json`, `results/determinism-2026-08-2x.json`,
  `claude_1/geometry1/g1-execution-2026-08-2x.md` — G-1.
- `codex_1/reviews/dance-geometry-measurements-g0-*.md`, `…-g1-*.md` — rulings.
- `local_claude_1/dance-geometry/owner-brief-2026-08-2x.md` — the deliverable to the owner.

## Acceptance checks

- `python3 claude_1/geometry1/run_geometry.py --inputs <pinned paths> --out <dir>` twice → the
  results files byte-identical (K-4); the run prints every control with its number.
- K-1 ≥ 95 % with every disagreement listed and explained; K-2 100 % or explained; K-3 reported;
  K-5 and K-7 exact.
- The headline tables in the execution report are re-derivable from the results JSON by a reader
  with no other input (the coordinator does this before the brief).

## Exclusive write set

- claude_1: `claude_1/geometry1/**` · codex_1: `codex_1/reviews/dance-geometry-measurements-*.md`
  · local_claude_1: `local_claude_1/dance-geometry/**`, this record, status, `docs/STATE.md` §4.

## Shared read-only paths

- Everything under *Inputs*; `claude_1/adapter1/**`, `claude_1/cure1/**`, `claude_1/narrate4/**`,
  `claude_1/dance1/**` (import only).

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred); `cgauto/submissions/**`; `data/raw/games/`;
  the accepted r3 classification and its results (`claude_1/dance1/results/*`); the cron; the
  resident; any peer's branch by merge.

## Arena authority

Read-only platform access: **not needed**. Platform mutation: **forbidden** — this task needs no
submission, no TestSession, no restore; the goal file authorizes none and the standing
authorization is not invoked.

## Fallbacks (from the goal file)

- claude_1 has not claimed within 30 minutes of the charter → a local Opus subagent builds under
  the coordinator's supervision, same definitions, same gates; codex_1 still reviews.
- codex_1 silent 60 minutes at G-0 → proceed *unreviewed*, joint review at G-1.
- M-2 proves expensive → deliver M-1 alone; M-2 marked **not done**, never "not needed".

## Not in scope

Any bug ruling; any cure or candidate; any change to the accepted r3 classification (the re-read
is a second reading beside it); opponents' reasons; prevalence beyond these two reads; any
statement that a dance "costs" score (not measurable here). **Time box:** 2026-08-26T14:00Z (the
mission's); then what is and is not done is written and the task stops.

## Handoff

claude_1 → codex_1 at G-0 (definitions, ack-required) and at G-1 (execution: full commit, paths,
digests, the controls' numbers); codex_1 → claude_1 + local_claude_1 with the rulings
(ack-required); local_claude_1 → owner with the brief. Every message names its `artifact_commit`
by `git rev-parse` and its files by path.
