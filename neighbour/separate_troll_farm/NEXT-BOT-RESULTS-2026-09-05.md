# Productive fallback screen and the denial regression — 2026-09-05

## Decision

Do not deploy either new productive-economy profile. The implementation repairs the observed
no-wood failure, but the prospective real-agent screen favors the older V368 reference. Stop
treating removal of resource denial as an established improvement. The next measurement should
isolate that change against fresh adaptive opponents, before more economy tuning or publication.

This is a substantial implementation and a useful negative experiment, not an achieved ladder
improvement. A post-screen authenticated room read still found V543, agent 6701731, at **13.92,
rank 155/177**, with 100/100 progress and no rollout in progress. No ladder submission was made.

## What was implemented and actually tested

`next_bot/` extracts V564's economy, shared game/protocol/navigation code and movement resolver
into one editable experimental controller. `export_next_bot.py` produces immutable module,
readable and compact snapshots under project working storage. The extracted, unchanged control
matched all 900 turns of V564's three earlier official games. Its compact was 28,868 UTF-16 units,
versus the original 99,828: this removes unused controllers, not a demonstrated startup defect.

The subsequent changes test a capability-based productive continuation:

- A worker bill needs reachable sources or retained seeds for every missing fruit. Carried stock
  counts toward funding. A heuristic acquisition/repayment estimate can abandon a bill.
- Existing workers compare collectible fruit/wood against full travel, work and banking time;
  wood is clipped to free carrying capacity. A stale fruit goal no longer blocks useful chopping
  when capital becomes unattainable.
- Seed/plant/drop commitments survive replanning. Growing own crops and a final banana seed
  source receive protection, and the renewal order prefers bananas.
- Serial and parallel profiles use one or up to two capital funders respectively. The latter
  estimates overlapping acquisition and fills a fruit load unless an early deposit completes
  the worker bill.
- A same-turn stock ledger reserves training costs and each seed withdrawal. An empty action set
  emits `WAIT` instead of a blank line.

Twelve executable Rust state fixtures run under each profile, covering the behaviors above. These
are decision fixtures, not complete economic-cycle proofs. In particular, the payback estimate
does **not** establish positive marginal worker value: the screen still bought workers as late as
turn 248 (serial/delineate) and 238 (parallel/Pony). Estimating nominal repayment is not the same
as measuring the counterfactual production displaced by funding and hiring.

The full Python suite passed **396 tests in 122.17 seconds**, including both Rust fixture runs.
Both final profiles' readable/compact exports also matched over 5,104 turns on 18 prior state
streams. That is export equivalence, not 18 new adaptive games or evidence of strategic strength.

## Development results, before the shared stock/WAIT fixes

These are the familiar eight maps, seeds 9941000–9941007, both seats and twelve proxy families.
Each policy has 192 games but only eight independent map blocks. They are regression data.

| Policy | W / D / L | W+0.5D | Mean own | Mean opponent | Mean margin | Mean wood |
|---|---|---:|---:|---:|---:|---:|
| V468 | 177 / 3 / 12 | 178.5 | 247.25 | 108.22 | 139.03 | 45.02 |
| Productive V1 | 156 / 0 / 36 | 156 | 236.29 | 132.11 | 104.17 | 57.19 |
| Productive V2 | 164 / 0 / 28 | 164 | 307.00 | 145.67 | 161.33 | 74.87 |

V1 loses match points in all eight map blocks; V2 loses them in seven, despite its +22.30 mean
margin. V2's additional production still does not establish more wins than V468. Four-worker
completion rises from 26/192 in V1 to 145/192 in V2. Neither worker count nor wood is the selector.
Both runs report zero critical/unclassified command issues, but include noncritical movement and
seed-stock conflicts. These panels predate the final stock-reservation fix; do not relabel their
results as panels of the final safe sources.

Two separate development games reuse the old putibuzu seed 2609050701:

| Policy | Game | Own–opponent | Own–opponent wood |
|---|---:|---:|---:|
| V1 | 901535885 | 92–132 | 23–33 |
| V2 | 901536153 | 88–185 | 22–46 |

Both lose. Their wood production is a real change from V564's zero wood and 117–289 loss on that
same initial block; it is not an independent validation win. V1 is near V468's prior 88–126 loss.
V2 improves the local panel but worsens this real opponent check. That conflict motivated a frozen
four-policy screen rather than choosing either allocation by its favorable measurement.

## Prospective screen: twelve actual adaptive games

`NEXT-BOT-FIELD-PROTOCOL-2026-09-05.md` froze policies, seeds, order and interpretation before
execution. All games use player zero. Opponents were ranks 7, 1 and 60 in the pre-run board read.
Every request completed; none was retried. Explicit runtime/protocol failures: **0/12**. No stderr
diagnostics were reported. This does not certify every action as economically useful or unblocked.

Each cell is own score–opponent score, with the official rank outcome in parentheses.

| Opponent / seed | V368 | V468 | Serial safe | Parallel safe |
|---|---:|---:|---:|---:|
| putibuzu / 2609051701 | 117–86 (W) | 112–258 (L) | 92–221 (L) | 157–206 (L) |
| delineate / 2609051102 | 196–391 (L) | 208–512 (L) | 164–650 (L) | 178–521 (L) |
| PonyPonyCodeCode / 2609051603 | 284–169 (W) | 316–200 (W) | 275–183 (W) | 336–210 (W) |

| Policy | W / D / L | W+0.5D | Mean own | Mean opponent | Mean margin | Mean wood |
|---|---|---:|---:|---:|---:|---:|
| V368 | 2 / 0 / 1 | 2 | 199.00 | 215.33 | -16.33 | 49.67 |
| V468 | 1 / 0 / 2 | 1 | 212.00 | 323.33 | -111.33 | 53.00 |
| Serial safe | 1 / 0 / 2 | 1 | 177.00 | 351.33 | -174.33 | 42.00 |
| Parallel safe | 1 / 0 / 2 | 1 | 223.67 | 312.33 | -88.67 | 54.33 |

The parallel profile scores most and produces most wood; V368 wins most. Relative to V368, neither
new profile gains a win, both lose its putibuzu win, and both worsen the delineate margin. Serial
also worsens the Pony margin. Neither earns the protocol's next-stage promotion. Relative to V468,
parallel improves two margins but worsens one and changes no outcome.

This is only **three seed/opponent blocks**, not a confident superiority result, a rating estimate,
or evidence that V368 reaches rank seven. Map and opponent effects are confounded, one seat is
tested, and these opponents do not represent the entire field. All three maps are now development
data. V368's historical rank 17 and repeat rank 37 remain relevant warnings about rollout variance.

Game identities, in table order V368 / V468 / serial / parallel:

- putibuzu: 901537001 / 901536908 / 901536956 / 901537057;
- delineate: 901537159 / 901537261 / 901537096 / 901537211;
- Pony: 901537291 / 901537378 / 901537397 / 901537349.

## A specific earlier decision is now in question

V468 removes the `900 / (1 + distance to enemy shack)` bonus for felling the selected scarce fruit
kind. Byte-for-byte comparison verifies that its module is exactly V439 with that block removed,
using `build_v468_chop_targets.without_denial_bonus`. V368 retains the bonus; its other differences
from V439 are later doorway-stall repairs.

The exact archived V439 compact reproduced **all 900 recorded commands** from V368's three fresh
games. The later stall repairs therefore made no observable command change on those paths. Combined
with the one-block V439/V468 source difference, this strongly implicates removal of denial in the
observed V368/V468 separation. This replay check is not an additional official V439 game and does
not prove universal equivalence of V439 and V368.

The putibuzu path shows the mechanism, not just a final score:

- V368 and V468 use the same first-turn `1/1/0/2` hire. Their commands diverge on turn 2.
- V368 fells plums at (6,5), (9,2), (8,6), (7,1) on turns 13, 22, 33, 52 respectively.
  V468 first fells the plums at (6,5), (8,6), (7,1) on turns 50, 54, 74.
- Putibuzu hires worker two on turn 68 against V468 but never does so against V368. Its final wood
  falls from 61 to 9. V368's own wood only rises from 28 to 29.

Thus the major difference is suppression of an opponent's productive continuation, not maximized
own harvesting or a late tactical tweak. This is a concrete counterexample to assuming that
removing an apparently inefficient denial action improves competitive play. It does not justify
an arbitrary denial bonus in every new architecture, on every map, or against every opponent.

The new productive controller still ranks ordinary production by own points per trip and retains
an inherited fixed first-hire heuristic. Correcting capacity accounting and impossible bills did
not address this strategic interaction. More variants of the same allocator would need a new,
falsifiable reason—not merely a higher local score or sunk effort in the refactor.

## Next experiment and publication boundary

Confirm exact V439 versus exact V468 as the single-change denial comparison on separately frozen
new maps and broader actual opponent coverage, keeping V368 as an archived reference. Do not
automatically replace the current weak deployment with the historical source's luckiest rollout.
If supported, test a controller that explicitly balances own bankable production and timely
resource denial; preserve renewal and deployment checks. Both-seat coverage remains outstanding.
Do not resume the late-worker queue or copy a new profile into production from this screen.

## Reproducibility and source integrity

Artifacts are under `/data/separate_troll_farm-working/next-bot/2026-09-05/`:

- `extracted-control/`, `productive-v1/`, `productive-v2/`: frozen sources, compiled programs;
  the latter two include frozen panel runners and `dev8.tsv`.
- `v1-denial-check/`, `v2-denial-check/`: the development platform responses/replays.
- `serial-safe/`, `parallel-safe/`: final module/readable/compact snapshots and both executables.
- `fresh-field-plan.json`, `fresh-field/`: frozen plan, manifest, four source snapshots and all
  twelve raw play responses plus owner-authenticated full replays.
- `safe-export-audit.json`, `development-map-results.json`, `fresh-field-audit.json`,
  `denial-ablation-audit.json`, `putibuzu-denial-timeline.json`, `post-screen-room.json`.

| Final compact | UTF-16 units | SHA-256 |
|---|---:|---|
| Serial safe | 34,018 | `7b9b7785228190ce63692aa41f05e6f0e5c2fb6ab5e1694cf3f6ca320ae984f6` |
| Parallel safe | 34,017 | `7da36abdb5700a6ae890f4be1a81da943f123e5451df6aa992c795c379d3644e` |
| V368 | 93,146 | `e592ce299d0da3bb744d5b6f0650f4d589afe472fe5421d1ddec5bed3de243d1` |
| V468 | 96,848 | `7cbda8994b32680609ae8a3585848d320ec212b80dab3d4c4a46f49f469749bf` |

The fresh manifest SHA is `555f5aeca14953681853f0f97423e00b7d7b2128554e0de1d76e0ec4508a208a`;
the audit SHA is `a77f71cc80896648d5c74dfd48351cc0d09d5c2005409e804dc1c5005c653c7a`.
Sources, plan, decompressed response/replay hashes, actual opponent IDs, seed echoes, scores and
official ranks were revalidated after collection. All four policies in each block share the same
normalized initial-state hash. The local exact compacts reproduced **3,598/3,598 official turns**;
120 additional startup/first-turn/exit trials were repeatable. Local timing is not platform timing.
`audit_field_pilot.audit_row` can recheck each archived row with its request index and frozen binary;
its pilot-specific CLI must not be passed this differently shaped twelve-game manifest.

`run_field_experiment.py` accepts an explicitly frozen plan of at most twelve sequential unranked
games; it refuses an existing manifest and never retries a play request. Its default is dry-run.
Always use `TMPDIR=/data/separate_troll_farm-working/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

`bot.rs` SHA remains `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
`submission.rs` remains `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
The read-only neighbor remains at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, with only the same
pre-existing dirty stats and untracked panel. Historical candidates were not deleted or overwritten.
