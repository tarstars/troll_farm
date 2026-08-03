# E7a iterative logical deletion protocol — 2026-08-03

Status: **FROZEN BEFORE ROUND-1 CANDIDATE GENERATION**

## Objective

Continue simplifying the exact-qualified 62,278-byte E7a equivalent by deleting one named
logical block per round. Every accepted round becomes the sole parent of the next round. A
round that changes any frozen semantic or live-replay command result is rejected and cannot be
used as a parent.

This is source simplification, not strategy development. There is no percentage target and no
permission to rename identifiers, minify, compress, reformat, or edit the sacred development
source.

## Exact parent

- Source: `local_codex_1/e7a-single-logical-deletion/candidate-e7a-remove-generic-selector.rs`
- Bytes: 62,278.
- SHA-256: `ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2`.
- Provenance: exact on ten fixtures, 7,234 public-live command lines, 516 development tasks,
  and 516 one-shot untouched tasks.

## Ordered deletion rounds

1. **Single-use configurable constructor.** Replace the private `with_policy` constructor,
   which has exactly one call, with the same field initialization directly in `new`. Preserve
   every configured value exactly.
2. **Permanently disabled idle-starter gate.** After round 1 makes the fixed
   `require_idle_starter = false` value explicit, delete that field, its helper function, and
   the short-circuited activation condition. Preserve the activation condition that remains.
3. **Redundant enemy-door-distance recheck.** Initialization admits a mother cell only when
   enemy-door distance is at least 11, and the only constructor fixes the later threshold at
   11. Delete only the stored duplicate distance/threshold and the later identical recheck.
4. **Fixed enemy-ETA configuration.** The sole executable constructor fixes
   `minimum_enemy_eta` at 8. Replace its one comparison with literal 8 and delete the field and
   initializer; do not change the comparison operator.
5. **Fixed worker-speed configuration.** The sole executable constructor fixes
   `minimum_worker_speed` at 1. Replace both helper arguments with literal 1 and delete the
   field and initializer; preserve the helper logic.
6. **Fixed idle-harvest switches.** The sole executable Yamo factory enables idle harvest and
   leaves its clock-only switch disabled. Delete both fields and their assignments, and retain
   the resulting condition `endgame && all candidates are WAIT-like` exactly.
7. **Fixed door-unblocking switch.** The sole executable Yamo factory enables door unblocking.
   Delete its field and assignments and preserve the unblocking call unconditionally.
8. **Fixed partial-bank-transit switch.** The same factory enables partial-load transit to the
   bank. Delete its field and assignments and preserve the guarded banking predicate without
   the constant-true conjunct.
9. **Fixed ordinary idle-regeneration switch.** The same factory enables ordinary idle
   regeneration. Delete its field and assignments and pass literal `true` at its one ordinary
   policy call; retain the separate function argument because a special endgame call passes
   `false`.
10. **Disabled non-persistent regeneration mode.** The same factory enables persistent
    regeneration. Delete its field, assignments, and false-mode cleanup/early-return branches;
    preserve the enabled arguments and conditions as constant true.
11. **Zero-valued opponent-arrival penalty.** The sole executable factory fixes
    `opponent_eta_penalty` to zero. `yamo_chop_candidates` therefore returns immediately after
    optional protected-tree filtering. Delete the unreachable opponent-distance/risk calculation,
    the field, and its argument plumbing; preserve candidate construction and protected-tree
    filtering exactly.
12. **Disabled preferred-only opening mode.** `TUNED_CARRY` fixes `require_preferred` to false.
    Delete that field and both unreachable true branches in initial second-troll selection and
    training-deadline fallback. Preserve the ordinary preference/extra-ETA logic and strongest-
    affordable fallback.
13. **Disabled movement-first tie mode.** `TUNED_CARRY` fixes `prefer_movement_ties` to false.
    Delete the field and the unreachable movement-first tuple, preserving the exact chop-first
    tuple from the false branch.

Later rounds require another named invariant recorded before their candidate is generated.

## Per-round gates

1. Parent SHA-256 and every exact replacement count must match the round manifest.
2. The candidate must rebuild byte-identically and be strictly smaller than its parent.
3. Standalone optimized compilation and empty input must pass.
4. All ten frozen semantic fixtures must match exact live E7a.
5. All 7,234 commands on the 25 immutable public liveness-counterexample games must match exact
   live E7a, with zero unknown updates or stderr.
6. Only a candidate passing all five gates may become the next parent.

## Accumulated-candidate gates

After the declared rounds, run the full 516-task development equality panel once. If exact, a
new collision-audited 43-map range may be remotely locked and run once for untouched equality.
No intermediate round consumes an untouched range. Arena remains unchanged because a
behavior-exact simplification has zero expected rating gain under the no-churn rule.

## Safety boundary

Keep `rust/src/bin/yamo_orchard_live.rs` byte-exact at SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`. Do not format any
locked source. Searches and collision audits remain tightly scoped and must not recurse through
the owner's huge mounted repositories.
