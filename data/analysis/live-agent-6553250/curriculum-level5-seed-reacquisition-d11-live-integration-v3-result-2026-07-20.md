# Curriculum Level 5 D11 live integration V3 result — 2026-07-20

## Verdict

**Reject and close V3.**  Its one-transition own-CHOP witness repairs the immediate V2 failure, but
the new bank exposes that reference retention is persistent rather than one-turn.  Exact parity
holds for 19 complete games, then fails seed 7,700,219 at turn 125 on only channel 101.  The V3 bank
`[7700200,7700264)` is consumed.

The frozen V3 protocol SHA-256 is
`dfb95a39bc2f2c4b6e3cf245940c53f718ffaf8ee33e4d6089ac31b3c5731f80`.

## Static and exact results

V3 is 68,580 bytes, compiles without diagnostics, and has source SHA-256
`40a163cb3c7f97a9618d73bb41f61511382875c37d1ab849a5aa073d40cd1c4a`.  All observation/mask
hashes, phase counts, actions, and commands match through seeds 7,700,200--7,700,218 and through
turn 124 of seed 7,700,219.

At turn 125 phase 0, only channel 101 differs: source/reference encodings are 6/51; in phase 1 they
would be 45/13.  Joint distance localization places the source objective at `(3,1)` or `(2,2)`,
near the default planned crop, while the reference retains an absent objective among
`(6,7)`, `(3,8)`, `(5,8)`, or `(4,9)`.  Channel 93 agrees at 64.  The immediately prior actions are
both MOVE, so this is not a new destruction event.

## Diagnosis

V3 correctly suppresses clearing on the first state after an own CHOP, then consumes the witness.
On the following state the crop is still absent, no new CHOP witness exists, and V3 clears the
coordinate.  The curriculum never performs that generic later clear: an own-removed
`created_crop` remains stale indefinitely unless a later successful own plant overwrites it or a
present tracked crop is subsequently destroyed by the opponent.  Different objectives initially
had equal worker distances, hiding the internal divergence until turn 125.

The missing state is therefore a persistent, observable provenance bit, not another action or
neural defect.

## Next boundary

V4 may replace the one-transition witness semantics with one persistent `own_removed_crop` flag:
set it when own CHOP makes the tracked crop absent; retain the coordinate while the flag is set and
the crop remains absent; reset it whenever the tracked crop exists or a successful pending own
plant establishes a crop.  Everything else remains fixed and a new bank is required.

