# D11 fixed-recipe catalog — development result (2026-07-20)

## Decision

**Recipe 7 (`2/3/1/2`) is the only promising fixed alternative, but it narrowly fails the frozen
training-completion gate.  Do not promote a fixed recipe or build a static map selector yet.
Test a bounded recipe-7-to-recipe-6 funding fallback on the same reused development block.**

No resident, submission candidate, holdout, or Arena state changes.

## Complete execution

The frozen catalog completed all 768 planned exact-engine games:

- reused seeds 0--7;
- both seats;
- six opponent continuations (`resident`, `gold_adaptive`, `compact_gold`,
  `norx_native_three`, `legend_balanced`, and `mybot`);
- all eight actor-trained recipes.

The primary unit is a map seed.  Both seats and all opponents are averaged before recipe
ranking.  Absolute margins against the local mechanisms are not treated as Arena estimates.

## Recipe ranking

| Recipe | Requested worker | Mean margin | Delta vs recipe 6 | Worst opponent delta | Training completion |
|---:|---|---:|---:|---:|---:|
| 7 | `2/3/1/2` | **-12.91** | **+16.24** | **+0.13** | **91/96 (94.79%)** |
| 6 | `2/2/0/2` | -29.15 | 0.00 | 0.00 | 96/96 |
| 5 | `1/2/0/2` | -66.77 | -37.63 | -65.00 | 96/96 |
| 4 | `1/3/0/1` | -67.49 | -38.34 | -66.44 | 95/96 |
| 2 | `2/2/1/1` | -81.64 | -52.49 | -74.81 | 96/96 |
| 1 | `1/2/1/1` | -90.51 | -61.36 | -86.31 | 96/96 |
| 3 | `2/2/2/1` | -103.67 | -74.52 | -96.25 | 89/96 |
| 0 | `1/1/1/1` | -132.67 | -103.52 | -130.69 | 96/96 |

Recipe 7 is not exploiting one friendly opponent: its mean deltas from recipe 6 are +25.56
against `compact_gold`, +0.13 against `gold_adaptive`, +9.25 against the field proxy, +31.75
against `mybot`, +20.38 against the native three-worker policy, and +10.38 against the current
resident continuation.

The result also validates the trained recipe conditioning.  Recipe identities do not collapse
to one common policy: margins span 119.76 points from recipe 0 to recipe 7, and their movement,
harvest, chop, and funding trajectories differ substantially.

## Why fixed recipe 7 does not pass

The predeclared fixed-recipe rule required at least 95% training completion.  Recipe 7 completed
91/96 games (94.79%), missing the gate by one game.  Its five failures were concentrated in
three map/seat states:

| Seed / seat | Opponent(s) | Recipe-7 delta from recipe 6 |
|---|---|---:|
| 0 / 1 | `compact_gold`, `gold_adaptive`, `resident` | -99, -122, -56 |
| 4 / 0 | `resident` | -23 |
| 5 / 0 | `resident` | -37 |

In every failure the starter spent the game requesting the expensive worker, never chopped,
never planted, and ended with zero wood.  This is a funding deadlock, not weak execution by a
successfully trained hybrid.  Recipe 6 trained in all five matching cells.

Successful recipe-7 training is nevertheless often intentionally late: median turn 50, p75 62,
p90 134, maximum 201.  A blanket early downgrade could remove much of the +16.24 advantage, so a
deadline sweep must measure full continuations rather than infer value from training speed.

## Portfolio result

The map-only hindsight oracle improves the best fixed recipe by +7.91 mean margin, but all of
that gain comes from only two of eight maps:

- seed 0 selects recipe 4 for +23.83 over recipe 7;
- seed 4 selects recipe 6 for +39.42;
- recipe 7 wins the other six maps.

Only recipe 7 wins at least two maps, so the frozen diversity condition fails.  A static map
selector is therefore not supported.  The inadmissible opponent-aware cell oracle is larger
(+15.49), reinforcing the old conclusion that opponent labels create a misleading information
ceiling.

## Next hypothesis

Start with recipe 7, but if it is still unbuilt at a fixed deadline, change the requested target
to recipe 6.  This is observable, deterministic, and cheap.  It directly attacks the five
funding deadlocks while preserving recipe 7 whenever it has already trained.  Evaluate broad
deadlines on the same reused block; freeze at most one rule before any disjoint test.

## Evidence

- protocol: `d11-recipe-catalog-development-protocol-2026-07-20.md`;
- row data: `d11-recipe-catalog-development-seeds0-7.tsv`, SHA-256
  `9bd2e0ec8413ef2bfa911b3b94f8efffafab1b16def988f7a349d6611d0218b9`;
- multilevel analysis: `d11-recipe-catalog-development-2026-07-20.json`, SHA-256
  `1db31ec9666d546322c690d6742797af57015446410133b079388d2427f676c9`.

