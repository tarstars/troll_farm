# Legend score-25.40 experiment cycle — volume 4 (opened 2026-08-04)

Objective and live state: `docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before
proposing. Volume 3 (`legend-top3-experiment-cycle-vol3-2026-07-30.md`) is frozen after the
owner-directed round-36 simplified E7a deployment.

Per-experiment obligations: one entry here; a CONSTRAINTS bullet for anything closed; a STATE.md
§4 update. The first session ending with this file over 100 KB freezes it and opens volume 5.

<!-- entries below -->

## 2026-08-04 — round-36 settled standing

The owner requested a settled position/game-count read for exact round-36 agent `6594200`,
submission `41090606`. At 16:25:25Z both platform score endpoints agree: **22.81, rank 32/137**,
with **160/160 games complete** and zero pending. The submission-scoped audit records 93W/2T/65L,
mean margin +8.925, 21 catastrophes, negative-margin mass 6,381, zero runtime signals, and clean
identity. Exact checkpoint SHA is `0f476514...`.

This read is recorded without Arena mutation. Round 36 remains active.

## 2026-08-04 — round-36 full replay corpus exported

The 160 settled games for agent `6594200`, submission `41090606`, are now available to agents
without platform access as a sanitized full-frame Git LFS corpus under
`data/shared-lfs/r36-agent-6594200/`. All 160 public replay fetches succeeded, with 86,940 frames
and exact game-ID equality to the settled checkpoint. The 40,006,551-byte staging set compresses
to 5,774,722 bytes at SHA `59f6283b...`; personal/session fields are removed and player names are
replaced by positional placeholders.

Payload commit `936cf577` uploaded successfully. A fresh smudge-disabled clone exposed the exact
LFS pointer and then reproduced the full payload and hash through an exact-path selective pull.
This was read-only with respect to both Arena and the collector-owned `data/raw/games/` cache.

## 2026-08-04 — banana restoration R2 handoff rejected before value testing

Claude's 74,725-byte candidate SHA `f29efd0e...` rebuilds exactly and independently reproduces
its compile, empty-input, 23 detector-test, 7/7 TIER-P, and 8/8 reported TIER-C results. Those
engineering checks are not sufficient: the candidate's own all-green lifecycle trace harvests
two bananas, carries both, then plants at turns 58 and 61 before banking, directly falsifying
I-9's one-seed/surplus-bank rule. The source also lacks the reviewed conversion-or-abandon branch
for an unripe contested mother, and the handoff lacks a complete compilable readable source for
the mandatory research/compact equality gate.

Verdict for exact SHA `f29efd0e...`: **IMPLEMENTATION_INVALID**. Remaining host replay and value
gates stop for these bytes; no Arena mutation occurred. This does not reject bounded banana
production as an algorithm. A successor needs a new hash and non-vacuous regressions for the
failed behaviors. Full report: `banana-restoration-r2-host-review-2026-08-04.md`.

## 2026-08-05 — banana restoration R2 successor rejected before host replay

Claude's 76,386-byte successor SHA `280ed777...` fixes the first handoff's three defects. The exact
source compiles; the new non-vacuous one-seed/surplus-bank, ownership-loss abandon, and
ownership-loss convert regressions and their controls pass; detector self-tests pass 23/23; and a
complete readable source is present.

The successor is still **IMPLEMENTATION_INVALID**. Its conversion predicate estimates chop time
as `ceil(current_health/chop_power)`, ignoring banana growth and health gain during the chop
sequence. A size-2, health-4, cooldown-1 tree with chop power 1 is reported as four turns but needs
five, which can reverse the required strict race against the opponent. The D-8/I-10a conflict also
remains untested: the passing convert fixture starts from a pre-existing mother, so D-8's
own-planted history never applies.

Integrator ruling: after a real ownership flip, an exact feasible I-10a conversion overrides
diagonal-mother protection; discretionary chopping while the mother remains owned is still
forbidden. The next revision needs growth-aware travel/chop simulation and a red/green boundary,
plus an amended detector and a non-vacuous own-planted flip/convert trace with an owned-mother
negative control. Host replay/value gates remain stopped; no Arena mutation occurred. Full report:
`banana-restoration-r2-successor-host-review-2026-08-05.md`.

## 2026-08-05 — banana restoration R2 round 3 still implementation-invalid

Claude's 76,750-byte SHA `2f58edef...` replaces the static chop estimate with the source's exact
tree-transition helpers. Independent rebuild/compile, all eight R-1..R-3 and control checks, the
old-`280ed777...` red result, and 27 detector tests reproduce.

The candidate still stops before host replay/value gates. Its advertised own-planted
flip/conversion t5 is a scripted command stream, not candidate behavior. Running the actual bytes
on that scenario yields PICK, MOVE, PLANT, then resident WAIT through turn 20; there is no flip
response or conversion. The invariant, candidate, and D-8 detector also compare conversion against
different arrival/ripening deadlines and time origins, while the candidate-level R-3 trace does not
exercise growth-added health during chopping.

Verdict: **IMPLEMENTATION_INVALID** for exact SHA `2f58edef...`. Integrator clarification is to use
one absolute-time oracle: conversion completion versus the opponent's earliest executable HARVEST,
with exact travel, growth, fruit production, and action timing. The next revision needs that oracle
in spec/code/regression/D-8 plus candidate-driven own-planted flip/conversion evidence. No Arena
mutation occurred. Full report: `banana-restoration-r2-round3-host-review-2026-08-05.md`.

## 2026-08-05 — banana restoration R2 round 4 fails the first broad host panel

Claude's 77,397-byte SHA `9f5ef833...` materially repairs round 3. The exact rebuild and both
compact/readable compiles pass; 28 detector tests and the one-oracle self-test pass; the real
candidate now plants, observes a real ownership flip, and converts under the strict absolute-time
oracle. Old `2f58edef...` remains RED for the expected feasible-edge and flip-response failures.

The first broad continued-referee panel finds a new terminal injury before replay/value work. On
map `9,854,000`, seat 0, against `gold_adaptive`, worker 2 is full with two wood and alternates
between `(8,4)` and `(8,3)` on turns 34--258 inclusive: 225 turns with no DROP, cargo loss, or
progress. Parent margin +68 becomes candidate -93. This directly falsifies I-19/I-20/I-21 and D-1;
the exact contract was written to prevent this same class of live injury.

Verdict: **IMPLEMENTATION_INVALID** for exact SHA `9f5ef833...`. The banana-live, exact
`897829265`, value, and Arena gates stop. Claude's new pipeline pre-review passes its 24 tests but
also misses this class because its critical-claim list excludes the banking/oscillation invariants;
the finding must enter the permanent failure ledger and a candidate-driven red/green gate. No
Arena mutation occurred. Full report: `banana-restoration-r2-round4-host-review-2026-08-05.md`.

## 2026-08-06 — banana round 5 withdrawn; FSM design requires revision

Claude withdrew 77,299-byte SHA `47c98f53...` before host execution after its new deterministic
120-map/two-seat fuzz gate blocked 141/240 candidate games. The prior mother-forbidden fix removed
one mechanism but not the class: 37 games still exhibited full-cargo coordination failures through
a stationary resident and articulation/occupancy interaction. The panel also exposed fruit-safety,
stall, oscillation, diagonal-chop, lost-fruit, and planting-bound violations. Round 6
`eac2eb36...` cuts the blocking set to 47/240 but is explicitly not a handoff. No host, value, or
Arena work ran for either SHA.

Independent review of Claude's replacement 11-state/six-channel design accepts the design-first
method, latched-mother claim, transit neutrality, lost-worker release, and verification ordering.
It remains **REVISION_REQUIRED**: simultaneous events lack atomic priority; EV7 and the founding
guard use proxy ETA thresholds rather than one exact harvester/chopper survival oracle; parent
slot divergence is causal only on an aligned prefix; and unconditional resident priority conflicts
with the carrier-progress invariant. Post-release veto scope, impossible-commitment exits, and the
exact bounded-enumeration manifest are also open. Full report:
`banana-restoration-r2-fsm-design-review-2026-08-06.md`.

## 2026-08-07 — resident denial scoring: the starter is the denial unit

Read-only source audit answering an owner question ("we choose one of lemon or plum and
concentrate on chopping it out — is that correct?"). Partly: `focus_type` picks ONE species,
by smaller summed BFS distance from OUR shack, frozen for the game; the denial term is then an
additive `900/(1+manhattan-to-opponent-shack)` bonus on top of a `1000*wood/turns` base, not a
clearing phase, with no completion condition and no revision.

Because `wood` is capped by carry capacity and chop turns scale with chop power, the base term
differs ~8x between worker classes while the bonus is identical. Crossover distance — where the
bonus stops outweighing wood efficiency — is **16-21 cells for the starter (1/1/1) but only 1-5
for a trained worker (3/3/3)**. An unassigned division of labour follows: the starter is the
denial unit, the trained worker the economy unit, and the allocation is inverted relative to
capability. Pulled to a size-4 focus tree by the opponent shack, the starter spends 25 turns to
bank one wood; the trained worker would take 9 turns for three. This is a visible mechanism for
the previously measured "pre-fruit denial recovers 18.8 opponent points while forfeiting 81.5
own".

Also recorded: `opponent_trolls <= 2` is already a scale-conditioned abort, so the owner's
proposed give-up rule exists as a trigger; what is missing is a destination, since the abort
falls back to undifferentiated wood maximisation. This qualifies B3.1's "the resident never
conditions on it" — it does condition here, only to switch denial off.

Descriptive only; reopens nothing. N6 already closed the weight ("keep 900"), and H4 closed
denial as bill prevention (`NO_MATERIAL_DENIABLE_BILL`, strict rate 0.0). Source
`fff6669b...` unmodified. Full report: `resident-denial-scoring-audit-2026-08-07.md`;
reproduce with `python3 cgauto/analyze_resident_denial_scoring.py`; drift guard
`tests/test_analyze_resident_denial_scoring.py` (9 tests).
