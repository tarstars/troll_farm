# D61p current-field replay refresh — planned protocol (2026-07-21)

## Purpose

The local corpus contains 1,302 exact Arena replays, but its durable collection manifest is still
centered on former agent `6553250`. Current stable resident `6561795` / submission `41015603` has a
one-off 80-game July 20 audit, not an immutable current-field corpus. Before any long D61 PPO run,
refresh real Legend trajectories so local option learning is checked against current opponent
behavior rather than only the reconstructed eight-policy league.

This protocol plans passive public-data collection only. It does not start TestSession, submit
code, trigger Arena games, replace the resident, or consume an Arena comparison slot. Network
execution remains sealed until the user explicitly authorizes collection.

## Immutable acquisition

Do not run the existing collector directly against its mutable singleton manifests. It overwrites
`leaderboard.json`, `players.json`, and per-agent battle lists, which would destroy provenance and
overlap a dirty worktree. First add a snapshot-safe entry point that:

1. writes leaderboard, selected-player manifest, battle lists, request log, failures, and hashes
   below `data/raw/snapshots/<UTC timestamp>-d61p/`;
2. stores replay bodies by immutable game ID in the shared idempotent `data/raw/games/` cache;
3. never overwrites an existing snapshot directory or an existing replay body;
4. records HTTP service, request body hash, response hash, source agent, collection time, and
   source rank for every game;
5. waits at least 0.35 seconds between public requests and uses a 20-second timeout; and
6. writes a final manifest atomically only after every requested game is classified fetched,
   already present, or failed.

## Frozen sampling frame

At the collection-time leaderboard snapshot, request:

- every listed completed battle for stable resident agent `6561795`;
- the ten most recent completed battles for each of the top 20 Legend agents; and
- any completed Boss game visible in those lists.

Deduplicate by game ID. Do not select games from outcomes, worker counts, map geometry, or whether
our resident won. The expected volume is roughly 150--350 unique games, depending on battle-list
retention and overlap.

Maps are retained, but trajectories are the primary target: official map generation is already
exact, whereas current opponent worker funding, renewable cycles, target provenance, and
production/suppression sequencing are the unresolved domain variables.

## Frozen parse and quality gates

Append newly fetched immutable replays to a snapshot-specific parsed product without changing old
rows. Require:

- every fetched body has frames, player identities, initial terrain, and a decodable final state;
- exact command/referee replay reaches every observable intermediate state;
- point symmetry and terrain invariants pass;
- final score recomputation is exact except separately tagged crash/timeout penalties;
- duplicate game IDs and duplicate parsed trajectories are zero; and
- at least 80 complete resident games, 15 distinct top-20 Legend agents, and 75 complete top-Legend
  games survive QA.

If a volume gate fails because the platform exposes fewer battles, preserve the snapshot and stop;
do not expand ranks or time windows post hoc.

## Frozen split contract

Create split labels before any D61 option result is joined:

- resident games: `SHA256("d61p-resident:" + gameId) mod 10`, with 0--5 discovery, 6--7
  validation, and 8--9 sealed confirmation;
- opponent identities: `SHA256("d61p-opponent:" + agentId) mod 10` with the same 60/20/20 mapping,
  keeping every game from one opponent in one split; and
- a game is eligible for a split only when both its resident-game and opponent-identity rules agree;
  disagreement rows remain calibration-only and cannot enter validation/confirmation.

The confirmation manifest is hashed and counts/cohort metadata may be read, but trajectories and
outcomes remain sealed until a separately frozen field-transfer gate reaches them.

## Intended analyses

Use discovery/validation data to produce, in order:

1. current resident rank/battle and failure-mode census;
2. worker-two/three/four timing, exact TRAIN-bill flow, crop provenance, and job-transition census;
3. distribution shift between real states and D40/D61 local state features;
4. coverage of current worker-rich, renewable-heavy, and suppression-heavy opponent trajectories
   by the local opponent population;
5. outcome-blind D61 option eligibility/activation on exact resident replay states; and
6. a prospective field-transfer protocol before PPO or candidate construction.

Replay counterfactuals end at the first changed command. Never treat a recorded opponent
continuation after our hypothetical divergence as an exact causal game result.

## Later active platform gates

Passive replay refresh does not authorize active sampling. If a locally trained candidate later
passes field transfer, request separate explicit authorization for:

1. a small TestSession A/A block to measure current platform nondeterminism;
2. a frozen A/B TestSession block with final-frame verification; and only then
3. one controlled submission and mature Arena reads.

This ordering separates cheap domain observation from noisy, capacity-limited ranking evidence.
