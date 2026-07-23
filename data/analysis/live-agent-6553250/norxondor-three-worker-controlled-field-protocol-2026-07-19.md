# Three-worker macro controller — frozen deployability and field protocol, 2026-07-19

## Decision being tested

Can the exact `NorxondorThreeWorkerSilver` complete controller be packaged as a legal submission
and retain enough value against current Legend opponents to warrant a later arena transfer?

This is not another search for a terminal upper bound.  The shared-state terminal teacher already
selected this branch on 72/160 held-out roots with 100% precision, +26.081 mean terminal margin,
+15.194 own score, positive mean value for all eight opponent models, and a +12 worst-model mean.
Its unresolved risks are implementation drift, runtime/size, and field transfer.

The arena resident remains immutable during this experiment:
`candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`, agent `6560353`.
No arena submission, source replacement, or `cgauto/api_submit.py` change is authorized here.

## Frozen candidate semantics

The candidate is a behavior-preserving standalone port of the existing research strategy, not a
new parameterization:

- the `SilverBoss` mixed fruit/wood continuation is unchanged;
- all continuation `TRAIN` commands are removed;
- before worker three, the oldest harvest-capable worker funds the largest stage deficit; when
  two workers exist, both fund the two largest deficits with distinct target reservation;
- the replay-derived componentwise affordable talent ladder and its four fixed stage caps are
  unchanged;
- once three workers exist, cooperative funding ends, the continuation regains command control,
  and all further training remains suppressed;
- all target ordering, ties, messages, and stateful sticky-target memory must match the research
  strategy exactly.

The source generator may reuse the resident's already-verified protocol/parser module and compact
whitespace.  It may not alter strategy behavior after any qualification result is observed.

## Stage 1 — standalone qualification

All checks must pass before any controlled platform game:

1. a single Rust 2021 source compiles directly with `rustc -O` and is at most 100,000 bytes;
2. the generated source and formatted development binary are stdout-identical on ten complete
   deterministic protocol streams;
3. the standalone policy and `NorxondorThreeWorkerSilver` emit identical command vectors at every
   observed turn on seeds 0--29, both seats, and all eight frozen local opponent models (480
   complete matches), with stateful memory reset independently per match;
4. every compared match reaches the same terminal state and has zero stderr;
5. measured decision latency has p95 at most 5 ms and maximum at most 50 ms.

Any mismatch fails closed.  Fixes to the parser, adapter, or objectively incorrect port are
allowed only before the first platform game and require rerunning all five checks.  A policy logic
change creates a new candidate and a new protocol.

## Stage 2A — current top-five field smoke

Use only the read/write-neutral `TestSession/play` endpoint through `cgauto/field_panel.py`.
Run one baseline and one candidate game against each frozen named opponent: delineate, wala,
norxondor, escdemon, and laconic (ten games total, candidate always IDE player 0).

Continue to Stage 2B only if all hold:

1. all ten games compile and finish without transport, runtime, timeout, or degenerate-score
   failure;
2. the candidate reaches at least three workers in at least four of its five games;
3. candidate mean own score is not below baseline mean own score; and
4. candidate mean margin is no more than 10 points below baseline mean margin.

The loose margin boundary is only an early safety stop because TestSession maps are unpaired.

## Stage 2B — rank-three pressure panel

If Stage 2A passes, run two further baseline and two further candidate games against each of the
current top three: delineate, wala, and norxondor (twelve games).  Analyze all 22 Stage 2 games
together, giving each top-three opponent three observations per bot and the other two one.

The exact branch earns a separately drafted arena-transfer protocol only if all hold:

1. 22/22 games are valid and the candidate reaches three workers in at least 9/11 games;
2. candidate aggregate mean own score exceeds baseline by at least 8 points;
3. candidate aggregate mean margin exceeds baseline by at least 12 points;
4. candidate wins at least three games and at least two more games than baseline;
5. against no named top-three opponent is candidate mean margin more than 15 points below that
   opponent's baseline mean; and
6. no runtime, timeout, compiler, parser, or command-validity signal appears.

Report raw rows, per-opponent scores/margins/workforce, aggregate means, wins, and bootstrap
intervals.  The fixed thresholds decide the branch; intervals are descriptive and cannot relax
them.

## Stop and continuation rules

- **Stage 1 failure:** repair implementation drift only, or close this standalone representation
  if exact parity/size cannot coexist.
- **Stage 2A failure with normal three-worker activation:** close universal direct transfer and
  use the field rows only to identify which complete-policy mechanism regresses.
- **Stage 2A failure from absent worker three:** inspect live funding feasibility and command
  validity; do not tune talent caps from five games.
- **Stage 2B pass:** freeze the exact source/hash and draft a capacity-controlled arena protocol;
  do not submit automatically.
- **Stage 2B fail with a coherent positive named-opponent family:** retain that family as evidence
  for an opponent-conditioned early macro selector, using a new independent field block.
- **Stage 2B broad failure:** close direct `SilverBoss` continuation transfer and return to a
  deployable closed-loop plan representation rather than another isolated TRAIN wrapper.

