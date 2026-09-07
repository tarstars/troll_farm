# Plant selection and renewable-cycle competition

## Decision

The plot-selection defects are repaired and renewable wood is now a competing production job in
the experimental controller. **Do not publish this variant.** It wins the same one of three
development field blocks as its parallel parent, improves only the putibuzu margin, and worsens
the other two. Its extra own score again does not establish extra wins.

The next hypothesis is joint allocation between capital acquisition, timely denial and ordinary
production. Both current harvest-capable workers are capital funders while a third-worker bill
exists; the production comparison runs only after those priorities fail. Merely adding a denial
bonus inside that lower-priority comparison would not guarantee early denial. This is a hypothesis
for a separately designed experiment, not a conclusion that every third worker is undesirable.

Production remains V543. The authenticated post-run room read still showed agent 6701731 at
**13.92, rank 155/177**, fully evaluated. No ladder source was changed or published.

## Implemented mechanism

`RENEWAL-CYCLE-DESIGN-2026-09-05.md` was written before implementation and evaluation.

The old `plant_cell` excluded the requesting worker along with every other occupied cell. The
new fixture showed that when the only legal plot was under that worker, it instead selected the
empty shack. These are distinct bugs: the selector vetoed the worker's legal current plot and
failed to exclude shacks. The Java referee's `engine/task/PlantTask.java` requires grass; shacks
are not legal planting plots. The previous carried-seed fixture supplied a preselected goal and
therefore did not exercise this selector.

The selector now permits its own worker's cell, excludes other workers, and excludes both shacks.
Four added Rust fixtures cover current-cell planting, forbidden plots, a renewable cycle beating
a distant wild tree, and immediately payable wood retaining priority. Before the fix, the
current-cell and renewable-choice fixtures failed under both allocation profiles. Afterward all
**16 Rust fixtures per profile** passed, as did the original export checks.

The production comparison now offers a banana seed job alongside fruit/wood trips. Its net value
subtracts the seed point and charges travel to an actual pickup door, withdrawal, travel to the
plot, planting, maturation to useful carrying size, chopping, return and banking. Growth is fully
charged; the estimate does not assume that another task makes waiting free. Banana is not a
training ingredient. A final banked banana is protected when no reachable live banana source
remains. Existing ten-crop/source/stock limits remain in place.

The implementation retains the earlier planting-time boundary, finite-goal behavior and inherited
opening/funding rules. The cycle estimate is not a forecast of opponent actions or a proven
long-term marginal return. Plot choice can still trade travel against enemy distance, and future
crop theft is not modeled in this new value term. No denial bonus or opening change was bundled
into this experiment.

## Familiar-map regression panel

Exact V439 versus the new parallel renewal export, seeds 9941000–9941007, both seats and twelve
proxy families: 192 games per policy across eight map blocks. The frozen runner completed in
102.842 seconds. This is development/regression data, not a strength gate.

| Policy | W / D / L | W+0.5D | Mean own | Mean opponent | Mean margin | Mean wood |
|---|---|---:|---:|---:|---:|---:|
| V439 | 173 / 5 / 14 | 175.5 | 238.46 | 110.56 | 127.90 | 44.29 |
| Renewal parallel | 165 / 1 / 26 | 165.5 | 334.10 | 150.27 | 183.83 | 82.43 |

The +55.94 margin accompanies **ten fewer match points**. Match points improve on one map and
worsen on seven. The new policy finishes with two/three/four workers in 23/24/145 rows. Critical
and unclassified command issues: zero. Fourteen games contain noncritical blocked moves, with at
most six in a game; 178 are clean. No seed-stock conflict is reported. Ring plant counts average
7.08 versus V439's 5.16; this is the runner's near-bank diagnostic, not total plant count.

The earlier productive V2 panel had 164/0/28 and mean wood 74.87, but that snapshot predates the
shared seed ledger as well as this change. Do not attribute the entire cross-report difference
to renewable-cycle valuation. The old final parallel-safe source remains frozen for a proper
single-change comparison if needed.

## Development check against actual adaptive opponents

Four requests were frozen in `renewal-field-plan.json` before execution. These deliberately reuse
the three already-inspected official screen maps; they are **not fresh confirmation**. Exact V439
was first repeated on putibuzu as a control. No gameplay tuning occurred during the four requests.
All completed without explicit runtime/protocol failures or retries.

V439 game 901539233 reproduced the earlier V368 path exactly: 117–86, 29–9 wood, both full command
streams, inventories, workforce, duration and normalized initial input. This supplies an actual
official control repeat for the previous local V439/V368 path-equivalence observation; it does not
make those policies universally equivalent.

| Opponent / seed | Earlier parallel-safe | Renewal | Renewal margin change |
|---|---:|---:|---:|
| putibuzu / 2609051701 | 157–206 (L) | 177–207 (L) | +19 |
| delineate / 2609051102 | 178–521 (L) | 240–597 (L) | -14 |
| PonyPonyCodeCode / 2609051603 | 336–210 (W) | 301–229 (W) | -54 |

Renewal games are 901539249, 901539261, 901539276 respectively. Their W/D/L is **1/0/2**, W+0.5D
is 1, mean own score 239.33, opponent score 344.33 and margin -105.00. Mean own wood is 59.00.
The earlier parallel-safe figures are 1/0/2, one point, own 223.67, opponent 312.33, margin -88.67
and wood 54.33. Thus renewal increases mean own score by 15.67 but worsens margin by 16.33 and
changes no outcome. The older V368 reference won 2/3, with mean margin -16.33, on these same blocks.

Renewal's own wood is 44, 60, 73 and plant commands are 19, 24, 26. It buys a third worker on
turn 113 against putibuzu and 189 against delineate, and none against Pony. More planting and
more wood are real mechanism changes, but the opponents' productive responses still matter.

These three reused map/opponent blocks provide diagnostic evidence only. Initial states were
reconstructed and matched against the archived games using the new seat-aware adapter. No fresh
holdout or ladder evaluation was opened for this variant.

## Validation and artifacts

After the gameplay changes, the full suite passed **410 tests in 125.00 seconds**. That includes
32 Rust behavior fixtures inside two Python test cases. The new readable and compact programs
matched on 900 earlier recorded input turns. Its exact compact then matched all 900 turns of
its three new official games; including the V439 control, the new field audit covers 1,200/1,200
turns. Forty local startup/first-turn/exit trials were repeatable. None reproduces platform startup.

Artifacts are below `/data/separate_troll_farm-working/denial-confirmation/2026-09-05/`:

- `renewal-cycle/`: module, readable, compact, source manifest, both binaries, frozen panel runner,
  `dev8.tsv`, `dev8-summary.json`, `dev8-diagnostics.json`, `export-audit.json`;
- `renewal-field-plan.json`, `renewal-field/`: four source-checked requests, raw responses,
  owner-authenticated full replays and manifest;
- `renewal-field-audit.json`, `post-run-room.json`.

The compact is 35,085 UTF-16 units, SHA-256
`615e45f965de42de644a9ac354508dab82e7abfe379e8e87deae1f9d67383803`.
Module SHA: `092f8d19c91aeca52c331278ee3891d1d75d82d4fc192c0101deb247991f492f`.
Readable SHA: `5f72dbd3f112df6bce931528964c2018a1f816268c2bb44bbb6af9554be3abf2`.
This is the current **experimental** `next_bot` export, not the selected production policy.
Both earlier safe profiles and every historical source remain archived, not overwritten.

`bot.rs` and `submission.rs` retain the V543 hashes recorded in the preceding reports. The
neighbor remains read-only with its pre-existing dirty files untouched. All new experimental
storage and tool temporary files stayed under the required `/data` working tree.
