# Curriculum Level 5 D11 live-integration protocol — frozen 2026-07-20

## Question and boundary

Can the accepted K2 actor be surrounded by a complete referee-facing parser, exact D11
observation/mask construction, sequential two-worker controller, action formatter, and TRAIN
bookkeeping while preserving the curriculum ABI, the turn-time gates, and the 100,000-byte
single-source limit?

This experiment freezes recipe 6, `(movement=2, carry=2, harvest=0, chop=2)`, as the production
default solely to qualify integration.  An audit-only command-line argument may select any of the
eight already frozen recipes so one implementation can be checked across the D11 stream.  Neither
the default nor that audit switch is an autonomous plan selector.  A complete pass therefore does
not create an Arena candidate and does not authorize submission.

The actor payload, K2 implementation, compiler flags, and inference gates are unchanged.  The K2
source anchor is `cd81cb3b1d10eacdf3f58f645dc6798b60e8ee4b6dae0d669bff8b7d6a4e683c`; its standalone result
is `curriculum-level5-seed-reacquisition-d11-kernel-k2-result-2026-07-20.md`.

## Frozen live semantics

The sole generated Rust 2021 source must:

- parse the exact CodinGame static map and per-turn inventory, plant, and unit protocol without an
  external file, crate, network request, or diagnostic output;
- store map cells in the fixed 22x11 observation canvas while retaining the actual width/height for
  navigation and commands;
- precompute the exact curriculum all-pairs BFS distances and unwalkable-target parking cells once;
- reproduce all 104 D11 observation channels, all 13x11x22 legal-action mask entries, fixed
  nearest/source/crop-cell tie breaks, u8 quantization, and previous-action/decision-phase fields;
- treat referee turn 1 as curriculum step 0; cap the 240-turn training horizon fields after turn
  240 so a 300-turn Arena process cannot underflow;
- attempt `TRAIN 2 2 0 2` until the default target worker exists, then make the two lowest-id own
  workers the phase-0/phase-1 actors; emit `WAIT` for any unexpected additional own workers;
- build both worker decisions from the same referee state, changing only decision phase and
  previous-action plane between them, exactly as `Level3Env::step` does;
- track the planned BANANA crop, successful own planting, renewable harvest count, and score at
  training from consecutive official states and the prior selected actions; and
- format MOVE/HARVEST/CHOP/DROP/MINE/PLANT/PICK with the selected unit id and canonical species.

No resident fallback, third worker, opponent-specific switch, collision patch, high-level recipe
selection, or policy modification is allowed in this integration experiment.

## Phase A — source construction and static accounting

Generate exactly one readable standalone source by replacing only K2's binary parity/benchmark
harness with the frozen live wrapper.  Report separately:

- the 46,496-byte standard-base64 payload;
- K2 inference code plus payload;
- parser/state/navigation bytes;
- observer/mask/tracker bytes;
- command/TRAIN/main-loop bytes;
- audit-only bytes; and
- complete source bytes and SHA-256.

The complete generated UTF-8 source must be strictly below 100,000 bytes, compile directly with
`rustc --edition=2021 -O`, and produce no compiler diagnostic.  Generation is byte-reproducible.

## Phase B — exact interactive ABI parity

Only a Phase-A pass opens one interactive audit on exact D11 seeds `[7700000,7700064)`.  For each
seed, use `level2_recipe(seed)` as the audit target and run the exact
`crop-first-funded-trio-repeated-pressure-reacquire-180` environment until its normal terminal.

Before each reference decision, hash the complete observation and legal mask independently with
64-bit FNV-1a.  The live process receives only the normal referee text state and must report its
phase-ordered observation hash, mask hash, selected flattened action, and normally formatted
command.  Require:

- exact hash equality for every observation and mask in every phase;
- every selected action legal and every command exactly equal to the frozen action decoder;
- exact one-phase-before-training and two-phase-after-training sequencing;
- no missing/extra turn, crash, timeout, stdout corruption, or stderr byte; and
- at least one successful train, crop creation, renewable harvest, and opponent crop-destruction
  event in the aggregate audit.

Hashing is only a transport check: the production path constructs the same arrays and invokes the
same K2 actor.  K2 itself is not regenerated or retuned from this result.

## Phase C — complete-process timing and 300-turn safety

Only a Phase-B pass opens one fixed production-mode process screen on 16 exact generated maps,
both seats, with the standard local referee protocol and a waiting opponent.  Run all 300 input
turns even after curriculum turn 240.  Require 32/32 clean processes, 300/300 command lines per
process, no stderr, at least one legal command for every own worker on every turn, and no invalid
TRAIN syntax.

On the Phase-B interactive run, time complete response latency from the flushed turn block through
the complete output line.  Initialization plus the first response must be <=1,000 ms.  After the
first turn of every process, require p95 <=45 ms and every response <=50 ms.  These include parsing,
observation/mask construction, one or two K2 forwards, formatting, IPC, and flushing.

## Verdict and next boundary

Any source, compile, ABI, legality, process, or timing failure closes this exact integration
attempt and requires a new written hypothesis; no threshold or seed revision is allowed.  A
complete pass accepts the fixed-recipe live skeleton and opens a separately frozen autonomous
recipe/first-move selector followed by layered field qualification.  Arena remains unauthorized.

## Frozen anchors

- K2 qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`;
- K2 actor source SHA-256:
  `cd81cb3b1d10eacdf3f58f645dc6798b60e8ee4b6dae0d669bff8b7d6a4e683c`;
- payload SHA-256:
  `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`;
- model/evaluation implementation SHA-256:
  `1a855753a145a764d6c3c7d526335c88f5773113f8c32e98376708faed2baf92`;
- Level-3/4/5 ABI SHA-256:
  `245fd4c8cd48861d40a7a600f65527c6b88fa53a22dc55f00ce5b5196d9555f6`;
- release library SHA-256:
  `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`.

