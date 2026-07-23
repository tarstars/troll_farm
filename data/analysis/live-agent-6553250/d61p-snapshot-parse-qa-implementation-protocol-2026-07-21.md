# D61p snapshot parse/QA implementation protocol (2026-07-21)

## Purpose

Prepare the offline half of the frozen D61p current-field refresh before any platform request. The
entry point consumes exactly one completed immutable snapshot, verifies its acquisition hashes,
parses only game IDs named by that snapshot, freezes resident-game splits, and writes only beneath
the same snapshot. It must not read games merely because they exist in the shared cache and must not
alter the existing 1,302-game raw or processed corpus.

## Input contract

Require:

- snapshot schema `troll-farm-d61p-snapshot-v1`, `complete=true`, and every wanted game classified;
- acquisition manifest and every listed snapshot file present with exact byte count/SHA-256;
- unique game IDs in `games.json`;
- eligible statuses only `fetched`, `already_present`, or `already_present_race`;
- each referenced cache path remains below `data/raw/`, exists, matches the recorded response hash,
  and contains the same numeric game ID; and
- failed acquisition rows remain in QA counts but are never silently dropped from the denominator.

Refuse to run if the snapshot already contains `processed/` or a parse temporary directory.

## Exact parse and QA

For every eligible replay require:

1. nonempty frames, two agent identities, scores/ranks, initial terrain, two shacks, and two initial
   trolls;
2. an official diff-decoded state for the initial state and every resolved turn, with command
   context supplied for implicit chop/growth cancellation and zero unknown diff updates;
3. decoded final inventories equal the trajectory final inventories;
4. final score recomputation exact for nonnegative official scores, with negative crash/timeout
   penalties tagged separately;
5. exact map dimensions/counts, point-symmetric terrain (with shack 0/1 exchange), and
   point-symmetric initial plant records; and
6. unique raw game IDs and unique parsed trajectory hashes.

Write per-game failures and do not abort the remaining parse. The overall QA gate fails on any parse
failure, unexpected score mismatch, unknown update, state/turn mismatch, symmetry failure, or
duplicate.

## Frozen resident splits and sealing

For a parsed game containing resident agent `6561795`, identify the other agent ID. Compute:

- `SHA256("d61p-resident:" + gameId) mod 10`; and
- `SHA256("d61p-opponent:" + opponentAgentId) mod 10`.

Map residues 0--5 to discovery, 6--7 to validation, and 8--9 to confirmation. A resident game is
eligible only when both labels agree; otherwise label it `calibration_only`. A missing/Boss opponent
ID is also calibration-only. Games without the resident are `top_legend_observation`; they do not
become outcome validation evidence merely because a top-20 agent sourced them.

Publish `split_manifest.json` with IDs, identities, labels, and counts but no scores. Write
discovery, validation, calibration, and observation games/trajectories below `processed/open/`.
Write confirmation games/trajectories only below `processed/sealed_confirmation/`. The ordinary QA
summary may expose confirmation counts and integrity status, but no confirmation score, outcome,
command, or trajectory content.

## Volume gates

After QA require:

- at least 80 parsed games containing resident `6561795`;
- at least 15 distinct top-20 source agents represented by a parsed game; and
- at least 75 parsed games sourced from the top-20 cohort.

If the platform exposes less, preserve the completed processed snapshot with `pass=false`; do not
expand the cohort or time window.

## Atomic publication and scope

Build the entire product under a fresh `.processed.tmp` sibling, fsync ordinary files as practical,
then rename it to `processed/` only after all rows are classified and summaries are written. No
D61 option result, PPO checkpoint, candidate score, Arena rank, or selection outcome may be joined
during parsing.

Implementation and tests are local preparation only. Running the collector still requires explicit
authorization, and this protocol authorizes no TestSession, Arena, or submission action.
