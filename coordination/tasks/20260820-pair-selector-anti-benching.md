# 20260820-pair-selector-anti-benching — employ the benched troll (rule R-2)

- Status: **OPEN — PHASE 3 (REVISION), OWNER-RULED 2026-08-21 ~10:00Z: D3 = "revise"**
  (the 08-21 morning ruling was D3 = HOLD, no Arena slot, because codex_1's
  unified verdict was `PACKAGE_REPRODUCED; BOTH CANDIDATES BLOCKED AS QUALIFIED
  CURES`; today the owner chose door 2 of three — revise, not retire, not change
  the panel rule). Phase 3 section at the end of this card. Originally
  OWNER-CHARTERED 2026-08-20 at the 4a sitting ("We should fix it"),
  consequence of rule R-2 (`docs/RULES-LEDGER.md`). The 24-case GOAL_SPLIT
  class is the target: the team-picker's joint pairing discards a troll's
  oracle-verified available work, up to 194 turns per game.
- Record owner: local_claude_1 · Work owner: **claude_1** ·
  Reviewer: **codex_1** (instrument-first, then gates) ·
  Integrator: local_claude_1
- Base: **Phase 1 subject = cure-C `ad3bfefe…`, pinned NOW** (valid for both
  possible verdicts — the selection code is byte-identical in both night arms;
  step 0 verifies). **Phase 2 subject = whatever resident tonight's ruling
  settles**, rebased then; subjects are pinned per phase, never drift
  mid-phase.
- Priority: **UNBLOCKED BY OWNER 2026-08-20 ("This task shouldn't be
  blocked") — Phase 1 starts NOW.** The original subject-contingency was
  over-cautious: the Door-1 candidate's entire diff is one forecast hunk
  (record: r1 handoff + codex's "one pure-deletion hunk" verification); the
  pair-selector code is byte-identical in both bots of the running platform
  session, so the Phase-1 mechanism probe is valid regardless of tonight's
  verdict. Probe step 0 verifies that byte-identity explicitly. Only Phase 2
  (the fix build) waits for the settled resident. Sentinel build yields
  priority (it is an optimization since the launcher went live).
- Created UTC: 2026-08-20T08:35:54Z

## Phase 1 — WHY (evidence first; this touches the most sensitive code)

Parity-disciplined probe on the accepted toolkit: for a representative subset
of the 24 (at minimum OSC-017, OSC-013, OSC-034, OSC-004 — the four
owner-ruled), log per turn WHAT the joint pairing scored and WHY the
benched troll's candidates lost — which term of the pair score dominates,
whether the discard is a hard filter or a score preference, and whether the
winning pair's value is even positive. Unprivileged logging of the actual
selection arithmetic; no reimplemented scoring (one-scoring-path rule).
Deliverable: mechanism note + fix design PROPOSAL to the OWNER (design gate —
the picker is planner core; two-doors-wall applies).

## OWNER DESIGN RULING (2026-08-20 ~19:50Z): P1+P2 APPROVED, DUAL-BASE BUILD

- **D1:** the candidate is **P1+P2** — refuse self-impossible pairs (a unit
  MOVEs onto a cell whose occupant the same pair orders to WAIT) + break exact
  ties toward fewer WAITs. P3/P4 stay named, unbuilt. The 235 non-deadlock
  turns stay out of scope, stated.
- **D2:** ONE patch, TWO candidates in parallel — base cure-C `ad3bfefe…` and
  base door-1 `547fa706…` (selection region byte-identical in both, measured
  at step 0). Both gated overnight; tomorrow's platform verdict selects which
  enters the measuring queue.
- **D3:** queue slot deferred to the owner tomorrow (default: after the
  origin-comparison session; option: preempt when gates are green).

## Phase 2 — the fix (after the owner's design go)

Per the approved design. Gate class per owner law: this is a
behavior-CHANGING candidate → **named-costs gate** (full decomposition both
directions, every de-novo game diagnosed and named, aggregate improvement,
codex package verdict) → **decided by its own M-1 platform session**, owner
rules KEEP/REVERT. Fixtures: the four ruled cases observed failing on the
unmodified subject, then employed under the candidate (turn-coverage metric).

## Boundaries

No Arena action within this task (sessions are the integrator's, serialized).
Resident byte-sacred. No relitigating R-2's scope — the rule is absolute by
owner ruling; only the MECHANISM of compliance is designable. All standing
transport rules (cards, deferrals, evidence gate, WIP) apply.

- Authority: owner rulings at the 4a sitting, 2026-08-20.

## Phase 3 — REVISION (owner D3 ruling 2026-08-21: "revise")

**What blocked P1+P2, exactly** (codex_1 unified review
`codex_1/reviews/pair-selector-phase2-unified-review-2026-08-20.md`, package
`14b575ce`):

- **B1 — un-benched is not cured.** Benched turns fell to zero on every fixture
  and panel blocking totals fell (53→33 cure-C, 43→35 door-1: the mechanism is
  real), but the standing FIXED grader moved **3→4 on cure-C (only OSC-034) and
  8→8 on door-1**: OSC-004/013/017 went detector-quiet with
  `progress_restored = false` — the troll stopped being benched and still made
  no progress.
- **B2 — P3 absolute regression on door-1 `m004` seat 0.** The locked panel
  configuration makes P3 (candidate-equals-parent orchard inertness) an absolute
  invariant; an intentional selector edit does not exempt it (codex_1 ruling,
  upheld by the coordinator 08-21). The revision must be **P3-clean**; the owner
  chose not to change the rule.
- **B3 — new P4 + `r5-horizon` on `m021`** (inside an already-blocked game): a
  new property violation is a cost even when the game-block count does not move.

**Phase 3a — WHY un-benched ≠ progress (diagnosis, no code).** On the champion
base with P1+P2 applied, for OSC-004/013/017: per turn, what the un-benched troll
does instead of progressing — which route its candidate list comes back through,
and what is formed and discarded. Reuse the accepted route probes
(`claude_1/picker2/make_route_probe.py`, the p1p2 subjects already exist) and the
G-1-accepted clause tap where a chop list is empty. **Expected collision, to be
stated not assumed:** Phase 3 of this task already found that on OSC-013 the
`idle_regeneration` fallback discards two formed `PICK`s on 101 of 170 idle
turns — the owner's **open extend-vs-replace question**. If progress on 013 (or
004/017) turns out to require that change, the diagnosis says so and **the
question goes back to the owner with the evidence; nothing is built against it
until ruled.** Also in 3a: the mechanism of the `m004` P3 regression and of the
`m021` P4/`r5-horizon` cost under P1+P2 — named, with the turn.

**Phase 3b — design proposal → codex_1 pre-build ruling → OWNER design go.**
The picker is planner core; two-doors-wall applies; the owner approved P1+P2's
design and approves the revision's. The design states whether OSC-030's shape
(same tree wanted while a teammate works it — the 4b "tree reservation"
mechanism, β) is covered by the revised picker or stays parked; teammate-aware
routing (OSC-010) stays parked regardless (movement level, not picker).

**Phase 3c — build + gates (ready-with-gates, named-costs class):**
- R-1 build on the **champion of record at build time** (rebase clause: if
  session 3 ends in REVERT, rebase before R-2).
- R-2 fixture verdict, **AMENDED 2026-08-21 ~11:15Z (owner-approved method
  change): the bar is the PANEL POPULATION, baskets are exhibits.** On the
  matched panel, benched-and-work-available unit-turns (oracle-verified) and
  benching episodes on base vs candidate: **healed − new positive, progress
  restored** (banking / employment, not merely detector-quiet), every changed
  game named. Basket evidence only through the episode-identity gate and on the
  champion-subject library once it exists: of the four owner-ruled, **013 and
  017 reproduce on the champion** and must turn FIXED there; 004 and 034 do not
  reproduce and are reported as NOT_REPRODUCIBLE, never counted. Old
  `sweep34` counts are not a bar.
- R-3 panel: **P3-clean** (orchard inertness holds vs parent on the locked
  panel), **no new P4 / `r5-horizon`** violation, blocking totals not worse than
  P1+P2's; full named-costs decomposition both directions, every de-novo game
  diagnosed and named; codex_1 `PACKAGE_REPRODUCED` + unified verdict
  QUALIFIED / BLOCKED.
- R-4 Arena **only on the owner's explicit go**; sequence versus cure α decided
  by the owner when both are qualified; one standard 5-pair block each, never
  composed before each is measured alone.

**Priority:** cure α (`20260821-swap-r1-cure`) keeps precedence for **building**;
Phase 3a is read-only and may run alongside it. Phase 3b/3c start after α's G-1
is delivered or α is blocked, whichever comes first. Work owner claude_1,
reviewer codex_1, integrator local_claude_1, as before.
