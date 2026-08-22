# E4 secure-orchard mother tie audit — frozen protocol

Date frozen: 2026-07-30

## Question

The live secure-orchard initializer ranks eligible home-door mother cells by maximum BFS
distance from the enemy doors and breaks an exact primary tie by lexicographically smaller
cell. Does choosing the other member of that tie change terminal local value?

This is a bounded causal audit of one exhaustive two-way choice. It is not a generic
pathfinding experiment, candidate selector, official-map result, rating estimate, or Arena
predictor.

## Why this survives prior closures

- X1/A2-0b already govern referee equal-best movement RNG.
- D171/D176 permanently close waypoint/detour oscillation work.
- E2 closes immediate bank-door routing and leaves only a small future-conditioned tie.
- N4 owns the resident's general candidate-pair surface.

Secure-orchard mother selection happens once from the static initial geometry, before the
resident pair selector, and the comparator is outside all four surfaces. A result-blind
structural census on reused generated maps found 57/1,000 geometry-eligible seeds and exactly
ten with two equal-best mothers. The existing coverage probe later forces orchard harvests
on nine of those ten seeds, so the tie is not merely dead source.

## Frozen source and transformation

Control is the exact live artifact:

`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`

SHA-256:
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

The alternate is materialized only in a temporary directory. It replaces the unique
secure-orchard mother-sort suffix

```text
.then_with(||a.cmp(b))
```

with

```text
.then_with(||b.cmp(a))
```

exactly once. No persistent source variant, submission artifact, or resident edit is
permitted. Primary enemy-distance ordering and every other byte remain exact.

## Frozen maps and opponents

All maps are reused synthetic Bronze seeds from the historical `0..999` panel. No fresh,
sealed, official, or confirmation map is opened.

Tied-best audit seeds, frozen before any alternate outcome:

```text
31,91,246,364,405,568,598,652,932,966
```

Unique-best negative-control sentinels:

```text
19,28,29,72,86,168,183,200,201,255,266,287,361,382,440,460
```

The value panel uses all six immutable opponents registered by
`cgauto/offline_policy_league.py`:
`motion`, `taskplan`, `race`, `yield`, `ringfix3`, and `chopharvest`.
Every policy/opponent/seed cell contains both seats.

The 16 sentinels run against `motion` in both seats and must be byte-exact between control
and alternate.

## Frozen telemetry

For every policy/opponent/seed/seat record:

- policy and opponent action-stream SHA-256;
- terminal state/outcome, scores, wood, terminal turn, and stall status;
- policy command counts;
- paired margin and wood edge.

For each tied seed record the initial mother set, enemy distances, chosen control/alternate
mother, and static eligibility. Report action divergence by seed, opponent family, and seat.

The exact all-1,000-map weighted delta is computed without rerunning 990 inert maps:

```text
weighted delta = sum(tied seed × opponent paired deltas) / (1000 × 6)
```

The comparator is provably identical on every unique-best/ineligible map, and the sentinel
hash gate tests that boundary dynamically.

## Integrity gates

All must pass before value:

1. exact source hash and exactly one declared replacement;
2. census reproduces 57 geometry-eligible seeds and the frozen ten tied seeds for both
   symmetric seats;
3. all 60 tied seed/opponent cells and both seats complete for both policies;
4. all 16 sentinel control/alternate policy action hashes, opponent action hashes,
   terminal states, and outcome fields are exact;
5. zero malformed commands, stderr, missing rows, duplicate keys, or nonfinite values;
6. jobs-1/jobs-8 complete tied-panel rows are byte-identical after excluding elapsed time;
7. byte-sacred resident remains `fff6669b…`.

## Mechanism gate

`ACTIVE_TIE` requires all:

- at least 6/10 tied seeds have a control/alternate policy action-hash divergence;
- divergences occur in both seats;
- at least four of six opponent families contain a divergence.

Failure returns `TIE_INERT` and value is descriptive only.

## Value adjudication

Compute seed-balanced tied-panel and exact 1,000-map-weighted deltas for margin, own score,
opponent score, and wood, plus seat and family means.

- `KEEP_LEXICOGRAPHIC` if weighted mean margin is nonpositive, either seat mean is negative,
  or the worst family mean is below −1.
- `TIE_RESIDUAL_NONMATERIAL` if `ACTIVE_TIE` passes and weighted mean margin is positive
  but below +1.0, or fewer than four families are positive.
- `TIE_RESIDUAL_MATERIAL_LOCAL` only if `ACTIVE_TIE` passes, weighted mean margin is at
  least +1.0, both seats are nonnegative, at least four families are positive, and the
  worst family is at least −1.

These are local terminal-margin gates, not rating conversion. Even
`TIE_RESIDUAL_MATERIAL_LOCAL` authorizes only review and a separate prospective decision;
it does not select the alternate, open confirmation, build a candidate, or trigger Arena.

## Planned artifacts

- `cgauto/e4_orchard_mother_tie_audit.py`;
- `tests/test_e4_orchard_mother_tie_audit.py`;
- compact JSON and report under `data/analysis/live-agent-6553250/`;
- implementation lock and manifest under
  `local_codex_1/e4-orchard-mother-tie-audit/`.
