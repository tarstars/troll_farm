# E5 on-site ripeness-wait audit — frozen protocol

Date frozen: 2026-07-30

## Question

When the exact resident is already standing on an unripe fruit tree, its fruit candidate
is a zero-motion `MOVE`; conflict resolution turns that command into `WAIT`. Would
removing only that on-site unripe candidate—thereby selecting the resident's next-best
ordinary task—improve terminal local value?

This is not a generic idle detector, arbitrary WAIT rewrite, ripeness predictor, opening
book, candidate selector, official-map result, rating estimate, or Arena predictor.

## Prior boundary

B3.6 classified 20 observed `opening_ripeness_wait` episodes as fate-benign and closed the
broad `idle_with_work` detector at a genuine ceiling no greater than 0.6 point/game.
It did not intervene on the exact live candidate set, measure displacement by the
next-best task, cover farmer-phase uses of the same function, or price terminal causal
value. E5 asks only that remaining question.

D176 continues to close generic waypoint/detour oscillation. N4 owns general candidate
pairs. E5 changes one pre-existing candidate's eligibility under one exact observable
state and may not expand into either surface.

## Frozen source and temporary transforms

Control is the exact live artifact:

`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`

SHA-256:
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

The alternate is temporary and changes the unique `fruit_candidates` guard from:

```text
plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell)
```

to:

```text
plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell)||plant.cell==unit.cell&&plant.fruits==0
```

exactly once. It does not force an action: the unchanged resident selector chooses its
next-best compatible candidate and replans again next turn.

A temporary diagnostic control adds stderr-only telemetry where a zero-landing `MOVE` on
a live, zero-fruit plant becomes `WAIT`. Its stdout must remain exact. No persistent
probe, alternate, submission artifact, or resident edit is permitted.

## Frozen panel

All maps are reused generated Bronze seeds `0..59`. No fresh, sealed, official, or
confirmation map is opened.

The value panel uses all six immutable local opponents from
`cgauto/offline_policy_league.py`: `motion`, `taskplan`, `race`, `yield`, `ringfix3`, and
`chopharvest`. Every seed/opponent/policy cell contains both seats:

```text
60 seeds × 6 opponents × 2 policies × 2 seats = 1,440 games
```

Seeds `0..7` against `motion` additionally compare raw control with the stderr probe in
both seats.

The E4 child-process-only deterministic runtime is reused because `motion` has a
wall-clock RHEA loop and randomized Rust collections. Monotonic observations advance by
one ms and child `getrandom`/`getentropy` use a fixed stream. No bot source byte changes.

## Frozen telemetry

For each control/alternate seed/opponent/seat:

- policy and opponent action-stream SHA-256;
- first common-state action divergence, including both command lists;
- matching diagnostic wait event: turn, unit, cell, plant item, size, cooldown, and
  selected target;
- terminal state hash, outcome, scores, wood, turn, and stall reason;
- policy and opponent command counts.

Report diagnostic waits as events and consecutive unit-level episodes. Report value
deltas for paired margin, own score, opponent score, and wood edge, overall, by seat, by
opponent family, and conditional on activated cells. Activated-subset value is descriptive
because activation is post-policy.

## Integrity gates

All must pass before value:

1. exact control hash; exactly one alternate replacement and one declared probe injection;
2. raw/probe stdout, opponent streams, terminals, and outcomes are exact on all eight
   sentinel seeds in both seats;
3. all 360 seed/opponent value cells and both seats complete for both policies;
4. zero malformed commands, unexpected stderr, missing rows, duplicate keys, or
   nonfinite values;
5. every first policy divergence has an exact common prefix and is explained by a control
   diagnostic event for a live zero-fruit on-site plant;
6. complete jobs-1/jobs-8 value, sentinel, and divergence rows are byte-identical after
   excluding elapsed time and the declared job count;
7. analyzer self-test, focused tests, and sacred-source SHA `fff6669b…` pass.

Any failure returns `UNIDENTIFIABLE`; no value verdict may be inferred.

## Mechanism gate

`ACTIVE_WAIT` requires all:

- at least 20/360 seed/opponent cells diverge in at least one seat;
- at least five divergent seat-games in each seat;
- at least four of six opponent families contain a divergence.

Failure returns `WAIT_INERT`; value is descriptive only.

## Value adjudication

Primary value is the seed/opponent-balanced whole-panel alternate-minus-control paired
margin. Compute both seat means and six family means.

- `KEEP_RIPENESS_WAIT` if whole-panel mean margin is nonpositive, either seat mean is
  negative, or the worst family mean is below −1.
- `WAIT_RESIDUAL_NONMATERIAL` if `ACTIVE_WAIT` passes and mean margin is positive but
  below +1.0, or fewer than four families are positive.
- `WAIT_RESIDUAL_MATERIAL_LOCAL` only if `ACTIVE_WAIT` passes, mean margin is at least
  +1.0, both seats are nonnegative, at least four families are positive, and the worst
  family is at least −1.

Even `WAIT_RESIDUAL_MATERIAL_LOCAL` authorizes only peer review and a separate prospective
decision. It does not persist the alternate, build a candidate, open another map range,
or trigger Arena.

## Planned artifacts

- `cgauto/e5_ripeness_wait_audit.py`;
- `tests/test_e5_ripeness_wait_audit.py`;
- compact JSON and report under `data/analysis/live-agent-6553250/`;
- locks and manifest under `local_codex_1/e5-ripeness-wait-audit/`.
