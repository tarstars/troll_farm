# E7a single logical deletion protocol — 2026-08-03

Status: **FROZEN BEFORE CANDIDATE GENERATION**

## Owner rescope

The prior requirement to cut the exact 62,820-byte live source in half is superseded. The
new objective is deliberately modest: delete one real, named block from the exact live bot,
keep the result strictly smaller and readable, and preserve live behavior and rank quality.
There is no fixed percentage target.

## Exact baseline

- Source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- Bytes: 62,820
- SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- Live identity: agent `6590141`, submission `41081503`, latest mature rank 11/131.

## First deletion

Delete the generic greedy action-selection fallback for rosters of three or more friendly
trolls. Preserve the zero-, one-, and two-troll selector byte for byte. For an unexpected
larger roster, return `WAIT` for every friendly troll instead of executing the deleted
general selector.

This is a supported-state deletion, not a strategy change: `can_train` permanently returns
false once two friendly trolls exist (`n >= 2`). The orchard wrapper cannot create trolls.
The candidate must retain that cap exactly.

## Frozen gates

1. The baseline and sacred-source hashes must match their recorded values.
2. The builder must find exactly one roster cap and one exact fallback block, and must make
   only the declared replacement.
3. Candidate bytes must be strictly below 62,820. Identifier renaming, compression and
   formatting-only reduction are forbidden.
4. Rebuilding must be byte-identical. Optimized standalone compilation, empty input, and the
   ten semantic fixtures must pass.
5. The 25 exact live liveness counterexamples must have no unknown update, stderr, or command
   failure. Because the deletion is unreachable on live rosters, candidate command lines must
   be byte-identical to the baseline command lines on every replayed state.
6. On the ordinary 43-map development panel (516 paired tasks), every candidate terminal row
   must equal the baseline row: score, opponent score, terminal turn, second-worker training,
   worker count, liveness and issue classifications. Any behavioral difference rejects the
   deletion as insufficiently proved.
7. Only after the development proof is published may a new collision-audited untouched
   43-map range be locked. It is run once and must retain exact terminal equality, both seats,
   all six opponent families, integrity, training and latency gates.
8. Arena promotion remains serialized through `local_codex_1`. No mutation is allowed before
   the untouched equality gate and promotion preflight pass.

## Evidence boundary

Previously consumed half-size panels may be used for diagnosis but cannot qualify this source.
The new candidate starts from the exact live source, not from any rejected half-size program.
