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
