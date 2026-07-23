# D160a exact-resident natural-capital window — frozen protocol

Date: 2026-07-23  
Status: frozen before inspecting all-turn replay states; no platform write authorized

## Why this preflight exists

D159 independently confirms that the resident loses after a viable opening to scaled renewable
economies. That does not make another forced third-worker experiment rational. Prior direct and
late-graft worker policies failed through funding disruption, and a post-D159 fixed-cut scan found
zero bank-affordable third-worker states at turns 75/100/150/200/225. The remaining unresolved
feasibility question is whether short affordability windows exist between those cuts.

D160 reads already cached public replays only. It does not fetch a replay, create a TestSession
game, use a map seed, construct a source, submit, or mutate the resident.

## Frozen corpus and states

- Start from the 200 exact agent-`6561795` game IDs in D159 raw SHA-256
  `97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443`.
- Use only matching immutable bodies already present under `data/raw/games`; missing bodies are
  reported and never fetched inside D160.
- Preserve the exact D23-ID versus independent-suffix partition.
- Decode every official input state, retain states with exactly two own workers and decision turn
  at most 225, and compute referee-exact `n=2` TRAIN bills. Charge IRON exactly when the map has
  IRON terrain.
- A bank window is immediately executable only when deposited inventory covers the whole bill and
  neither player's unit occupies our shack. Also report stock affordability before the shack
  check and `bank + own carry` liquidity as a non-executable upper diagnostic.

## Frozen worker specifications

| Label | `(movement, carry, harvest, chop)` | Purpose |
|---|---:|---|
| `minimal_1101` | `(1,1,0,1)` | cheapest legal production/suppression helper |
| `balanced_2202` | `(2,2,0,2)` | D94 production-grade third worker |
| `hybrid_2212` | `(2,2,1,2)` | adds renewable harvesting ability |
| `carry_2302` | `(2,3,0,2)` | higher logistics capacity |

For each spec and cohort, report game-level stock/liquid/executable activation, first and last
window turns, maximum consecutive executable span, minimum deposited deficit, and the limiting
resource at each game's closest state. Keep catastrophic outcomes descriptive; they are never an
actor input.

## Integrity and decision gates

Require at least 190 cached exact-resident games, at least 110 cached suffix games, every decoded
row to have zero unknown updates, exact resident identity, exact D159 membership, no duplicate game
IDs, and exact terminal score reconstruction except disclosed penalty-only endings.

An active common-map field probe may be designed only if `balanced_2202` has, before turn 200 in
the independent suffix:

1. at least 12 games with an immediately executable deposited-bank window;
2. at least eight games with a consecutive window of two or more decisions; and
3. activation across at least six opponents and both seats.

`minimal_1101` alone cannot open a probe because it does not represent the production architecture
identified by D101/D159. `bank + carry` alone also cannot open a probe because banking would itself
change resident behavior. If the production-grade gate fails, cancel D160 platform games and move
to an exact-resident-fallback funding/controller representation; do not test another opportunistic
TRAIN wrapper.

## Outputs

- deterministic machine result: `d160a-resident-natural-capital-window-result.json`;
- human result: `d160a-resident-natural-capital-window-result-2026-07-23.md`.
