# Denial helps some interactions, but restoration alone does not win

## Decision

The isolated six-block confirmation changes **no match outcome**: V439 and V468 both finish
1 win, 0 draws, 5 losses. Denial reduces mean losing/overall margin substantially against the
rank-two and rank-eight agents, but worsens one putibuzu loss. Do not publish a restoration as
the demonstrated route to seventh place, or conclude that denial is useless from its own-score
cost. Keep it as a measured strategic component while repairing renewable production.

Production remains V543, agent 6701731, last freshly read at rank 155/177, rating 13.92 and full
100/100 rollout. No ladder publication occurred. The goal remains unachieved.

## Frozen official comparison

`DENIAL-CONFIRMATION-PROTOCOL-2026-09-05.md` fixed six new blocks, exact policies, player-zero seat,
alternating order and interpretation before execution. The refreshed board confirmed putibuzu
6479779 at rank 7, tonigineer 6505289 at rank 8, and 6480540 at rank 2. The latter's full current
display name is `norxondor_gorgonax`; `norxondor` is the retained short label, not a different agent.
Identity checks use the fixed agent ID, not a display-name alias.

All twelve sequential unranked requests completed. No request was retried. Explicit runtime/
protocol failures: **0/12**. Every pair matched initial-state hashes; raw responses and full replays
matched game identity, scores, official ranks and seed echo. All results are included below.

| Opponent / seed | V439 own–opponent | V468 own–opponent | V439 margin change | Outcomes |
|---|---:|---:|---:|---|
| putibuzu / 2609052701 | 226–168 | 226–168 | 0 | W / W |
| putibuzu / 2609052702 | 200–229 | 192–194 | -27 | L / L |
| tonigineer / 2609052801 | 232–290 | 242–301 | +1 | L / L |
| tonigineer / 2609052802 | 160–244 | 128–277 | +65 | L / L |
| norxondor / 2609052201 | 170–297 | 157–338 | +54 | L / L |
| norxondor / 2609052202 | 279–321 | 272–458 | +144 | L / L |

| Policy | W / D / L | W+0.5D | Mean own | Mean opponent | Mean margin | Mean own wood |
|---|---|---:|---:|---:|---:|---:|
| V439 | 1 / 0 / 5 | 1 | 211.17 | 258.17 | -47.00 | 47.00 |
| V468 | 1 / 0 / 5 | 1 | 202.83 | 289.33 | -86.50 | 45.17 |

Opponent-specific mean margins, V439 versus V468: putibuzu +14.5 versus +28.0;
tonigineer -71.0 versus -104.0; norxondor -84.5 versus -183.5. Each opponent has two maps.
Paired match-point change is zero in every map block. The mean margin change is +39.5, with four
positive blocks, one identical block and one negative block, ranging from -27 to +144.

Six seed/opponent blocks are a small mechanism confirmation, not a rating calibration or a
full-field superiority estimate. The maps are now development data. This study does not turn the
preceding one-map win against putibuzu into a universal denial rule or confirm a top-seven policy.

Game IDs, in table order V439 / V468:

- 901537846 / 901537865;
- 901537884 / 901537872;
- 901537908 / 901537922;
- 901537940 / 901537931;
- 901537948 / 901537974;
- 901537996 / 901537982.

## Where the difference comes from

On the first putibuzu map, final results are identical and both opponents hire on turn 42.
On the second, putibuzu already hires a `2/2/2/2` worker on turn 1 against either policy; V439's
denial does not buy another win and its opponent ultimately banks nine more wood.

On norxondor seed 2609052201, the opponent buys a third worker on turn 142 against V439, compared
with turn 102 against V468. On seed 2609052202, the V468 opponent reaches four workers with hires
on turns 1, 73, 129; the V439 opponent hires only on turn 1 and stays at two. Its wood falls from
87 to 24, but it retains 225 fruit points and still wins 321–279. Our own wood only rises 67 to 68.

This supports the resource-denial mechanism while showing its limit: disrupting worker expansion
does not necessarily prevent an efficient two-worker fruit economy. Our own productive continuation
must improve as well. A larger score in a still-lost game is not the desired end state.

## Opposite-seat instrument validation

The earlier official studies used player zero only. `field_seats.py` now constructs either seat's
request and normalizes reporting to candidate/opponent order, while preserving physical scores,
ranks, agent indices and worker IDs. Identity validation checks both the requested opponent and
the IDE candidate's actual seat. Deduplication and initial-state pairing include seat.

Inventories, wood, fruit, official-rank outcomes, workforce, command statistics, diagnostics and
both command streams are normalized together. Canonical initial input swaps shack/player labels,
not coordinates or worker IDs, and restores plant creation order. Structured JSON inventory
parsing avoids dependence on the viewer's whitespace. `audit_field_pilot.audit_row` now renders
and compares the requested seat instead of silently assuming player zero.

Forty focused tests passed. The complete suite then passed **410 tests in 116.61 seconds**, before
the subsequent renewal gameplay edit. The adapter's player-zero competitive fields also matched
all twelve just-completed schema-one rows. The running confirmation collector had loaded its old
code before these edits; its archived schema-one manifest was not rewritten or relabeled.

A separate, prospectively fixed two-game A/A check used exact V439 in **seat one**, PonyPonyCodeCode
6541377, seed 2609053101. Both games, 901538318 and 901538342, finished candidate-first **211–203**
(physical scores **203–211**), with 52–50 wood and 300 turns. Initial input, both complete command
streams, scores/ranks, workforce and duration were identical. Both exact local command streams
matched all **600 turns**, including twenty repeatable startup/first-turn/exit checks. These are
instrument repetitions, counted as zero additional games in the six-block competitive totals.
They establish this seat-one path, not arbitrary opponent determinism or platform startup timing.

## Integrity and artifacts

All generated artifacts are under
`/data/separate_troll_farm-working/denial-confirmation/2026-09-05/`:

- `pre-run-board.json`, `plan.json`, `field/manifest.json`, twelve raw responses, twelve full
  replays, both exact source snapshots, and `audit.json`;
- `seat-one-aa-plan.json`, `seat-one-aa/`, `seat-one-aa-audit.json`;
- `v439-readable-bot`; the exact compact binaries remain in the prior dated working directories.

V439 compact: 96,985 UTF-16 units, SHA-256
`7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`.
V468 compact: 96,848 units, SHA-256
`7cbda8994b32680609ae8a3585848d320ec212b80dab3d4c4a46f49f469749bf`.
The exact local compacts matched **3,476/3,476 official turns** in the six-block study, with
120 repeatable local startup trials. V439's readable export also matched all six V439 streams.

The neighbor remains read-only at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, with its original
dirty stats and untracked panel preserved. The next gameplay experiment is separately specified
in `RENEWAL-CYCLE-DESIGN-2026-09-05.md`; these official results are not outcomes of that new code.
