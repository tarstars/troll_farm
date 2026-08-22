# E7 `typeToCut` per-map audit — frozen protocol

Date frozen: 2026-07-31

## Question

The exact resident chooses LEMON or PLUM once from the initial map by minimizing the sum
of home-shack BFS distances to that species, then applies the choice all game as the
early denial bonus. Does choosing the other species improve terminal local value, and
what is the exhaustive per-map hindsight ceiling?

This is a binary upstream policy audit, not a general tree-target, candidate-pair,
denial-weight, feature-selector, opening-book, rating, or Arena experiment.

## Prior boundary

H13 verifies that the resident faithfully reproduces yamo's published `typeToCut` design
and finds no field concentration gap, but does not causally compare species on common
maps. N6 closes the denial bonus weight at 900. N4 owns general candidate pairs. E7 changes
neither candidate enumeration nor the weight: it flips only the once-per-game species.

## Frozen source and transformation

Control is:

`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`

SHA-256:
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

The temporary alternate replaces the unique live initialization:

```text
self.type_to_cut=Some(MoisanBot::focus_type(view));
```

with:

```text
self.type_to_cut=Some(match MoisanBot::focus_type(view){PlantKind::Lemon=>PlantKind::Plum,_=>PlantKind::Lemon});
```

exactly once. No persistent source, submission, or resident edit is permitted.

## Frozen panel

Use reused generated Bronze seeds `0..59`, all six immutable opponents from
`cgauto/offline_policy_league.py`, both policies, and both seats:

```text
60 seeds × 6 opponents × 2 policies × 2 seats = 1,440 games
```

No fresh, sealed, official, or confirmation map is opened. Reuse E4's temporary
child-process deterministic clock/entropy runtime; no bot source byte changes.

## Frozen telemetry

- Reproduce the control species independently from initial geometry for both seats.
- Policy/opponent action-stream and terminal-state hashes.
- First common-state action divergence and changed target species where identifiable.
- Terminal margin, own/opponent score, wood, turn, outcome, and command counts.
- Overall, seat, family, and seed means for flip-minus-control.

The exhaustive per-map hindsight oracle first averages the flip delta across all six
opponents for each seed, then chooses CONTROL or FLIP once for that seed. It may not choose
separately by opponent or seat. Report leave-one-family-out evaluation descriptively.

## Integrity gates

1. Exact source hash and exactly one reversible transformation.
2. Independent geometry reproduces one LEMON/PLUM choice for every seed and symmetric
   seats agree.
3. All 360 seed/opponent cells and both seats complete for both policies.
4. Any inactive cell is exact in policy/opponent streams, terminal, and outcome.
5. Every first divergence has an exact common prefix; no opponent leads the policy.
6. Zero malformed commands, unexpected stderr, missing/duplicate rows, or nonfinite values.
7. Complete jobs-1/jobs-8 value, divergence, and oracle rows are byte-identical after
   excluding job count.
8. Focused tests, self-test, and sacred source `fff6669b…` pass.

Failure returns `UNIDENTIFIABLE`.

## Mechanism gate

`ACTIVE_FOCUS` requires at least 30/360 divergent seed/opponent cells, at least ten
divergent seat-games per seat, and at least four active families. Failure returns
`FOCUS_INERT`.

## Value adjudication

Direct FLIP is material only if whole-panel mean margin is at least +1.0, both seats are
nonnegative, at least four families are positive, and the worst family is at least −1.

The per-map hindsight residual is material only if its seed-balanced gain is at least
+1.0, at least 12/60 seeds prefer FLIP, both selected-policy seat means are nonnegative,
and at least four leave-one-family-out family means are positive.

- `KEEP_TYPE_TO_CUT` if the hindsight residual is not material.
- `HINDSIGHT_RESIDUAL_ONLY` if hindsight is material but direct FLIP is not.
- `FLIP_MATERIAL_LOCAL` only if direct FLIP passes every direct gate.

Hindsight is an upper bound, not a deployable selector. Even a positive verdict authorizes
only peer review and a separate prospective decision; it does not persist a source,
train a selector, open maps, build a candidate, or trigger Arena.

## Planned artifacts

- `cgauto/e7_type_to_cut_audit.py`;
- `tests/test_e7_type_to_cut_audit.py`;
- compact result/report under `data/analysis/live-agent-6553250/`;
- locks/manifest under `local_codex_1/e7-type-to-cut-audit/`.
