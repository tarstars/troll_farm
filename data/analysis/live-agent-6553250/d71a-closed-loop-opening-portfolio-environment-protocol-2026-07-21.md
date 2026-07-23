# D71a closed-loop opening-portfolio environment protocol (2026-07-21)

## Question

Can the exact D61/D62 batch environment represent repeated, species-specific opening source
creation with observable lifecycle memory, while preserving exact D40 control behavior and enough
throughput for a later closed-loop population gate?

D71a is a mechanics/representation preflight. It reads no field outcome, estimates no policy
value, trains no model, constructs no candidate, and performs no platform action.

## Frozen option boundary and actions

Retain D62's natural Train-stage/free-worker-batch boundary. Expose eight actions in fixed order:

1. `balanced`;
2. `harvest`;
3. `renew`;
4. `fell`;
5. `seed_plum`;
6. `seed_lemon`;
7. `seed_apple`; and
8. `seed_banana`.

The first four actions retain exact D61 semantics. A seed action suppresses TRAIN for that one
batch, assigns the first currently free empty worker (normally the starter) one deposited-seed
PICK -> private-cell PLANT job, assigns every other free worker with exact balanced semantics, and
returns at the next natural boundary. The deterministic cell is D40's existing player-favored
domain. Existing jobs continue concurrently.

A seed action is legal only when the requested deposited fruit exists, the first free worker is
empty, a reachable unoccupied/unreserved D40 source cell exists, and no earlier explicit seed job
is still in flight. It remains available after an owned crop exists so a controller can compound
or replace loss. Explicit seed actions may recur; there is no fixed turn, count, species rule, or
outcome feature.

The implementation must be inert on ordinary paths. `balanced` complete episodes must retain exact
D62 terminal/action/state behavior.

## Frozen observation and lifecycle memory

Append 16 finite deployable features to D62's exact 56:

- four explicit source-attempt counts and four successful explicit-source creation counts (8);
- cumulative fruit units harvested by us from own-provenance crops (1);
- cumulative ended own generations, computed as created minus currently live (1);
- cumulative generations created after the first renewable receipt (1);
- current live own generations (1);
- ever-received-renewable indicator (1);
- previous decision was an explicit source indicator (1);
- turns since the last explicit source attempt (1); and
- explicit source job currently in flight (1).

Counts are normalized by fixed constants in code and remain unclipped only where their game bounds
already guarantee finiteness. No seed, opponent label, nickname, future command, terminal result,
or rollout value is exposed.

## Frozen mechanical panels

### Exact anchor

Replay constant `balanced` on the exact 16-task D62 parity prefix beginning at seed 9,801,000 and
require equality to `d62a-balanced-reference-matrix-9801000.tsv` for terminal scores, workers,
crops, action hash, and state hash.

### Representation grid

Use official seeds 9,803,000--9,803,031, both seats, all eight unchanged D40 opponents, and six
fixed mechanics probes:

- `balanced`;
- one probe preferring each of the four seed species whenever legal until four explicit attempts,
  otherwise balanced; and
- `cyclic`, preferring the next legal species in PLUM/LEMON/APPLE/BANANA order until six explicit
  attempts, otherwise balanced.

This is 512 tasks per probe and 3,072 rows. Run the complete matrix twice with 20 threads and
require byte identity. Probe labels are not policies eligible for value comparison.

Record terminal mechanical fields, option/seed decisions, attempts and creations by species,
renewable receipts, ended/reinvested generations, live generations, repeated attempts, attempts
after a prior death, in-flight boundaries, finite-feature checks, legal-mask checks, action/state
hashes. Measure elapsed time and effective CPU use in a separate host-timing sidecar excluded from
the byte-identity comparison. Do not aggregate score or margin by probe.

## Frozen gates

All are conjunctive:

1. exact 16-task balanced anchor parity;
2. complete byte-identical 2 x 3,072 representation matrices;
3. zero illegal/masked action, direct-command, provenance, deposit-prediction, finite-feature,
   reward-identity, option-count, or source-assignment failure;
4. every species action is assigned at least 100 times and creates at least 100 crops;
5. each species probe creates at least one owned crop in at least 99% of its tasks, and cyclic does
   so in 100%;
6. cyclic makes at least two explicit attempts in at least 50% of tasks, observes a prior ended
   generation in at least 32 tasks, and makes a later explicit attempt after death in at least 16;
7. ordinary balanced remains legal in every state, pre-crop ordinary alternatives retain D62's
   lock, and at least two seed actions are legal in at least 50% of pre-crop boundaries;
8. all eight actions occur, every step ends terminal or at a Train boundary, and no task exceeds
   5,000 decisions; and
9. throughput is at least 400 boundary transitions/s with at least 12 effective CPU cores.

## Decision rule

- **Full pass:** freeze this environment as infrastructure and open a separate random
  recurrent-policy/upper-bound population gate on disjoint official maps. Do not start PPO yet.
- **Anchor/integrity failure:** quarantine all non-anchor telemetry and repair only the
  implementation defect before repeating unchanged.
- **Source reachability or lifecycle failure:** close this explicit source action grammar and move
  to a lower-level opening controller; do not relax counts, placement, or action gates.
- **Throughput failure only:** optimize batching without changing semantics or gates.

No branch authorizes value selection, PPO, confirmation access, TestSession, Arena, submission, or
resident replacement.
