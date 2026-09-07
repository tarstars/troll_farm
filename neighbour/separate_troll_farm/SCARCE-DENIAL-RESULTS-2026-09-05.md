# Scarce-fruit denial: development success, fresh confirmation failure

## Decision

**Do not publish.** The enabled two-worker variant won the missing putibuzu development game,
but the prospective six-block comparison did not confirm improved strength. Both it and V439
went 1/0/5; the candidate won none of the four rank-seven/eight blocks and worsened margin on
five of six blocks. The predeclared selection rule failed. No threshold was weakened afterward.

The experiment establishes a useful mechanism, not a champion: releasing both workers and
denying scarce wild fruit can stop an opponent's expansion when its opening requires that fruit.
It does not establish that the fixed two-worker opening, latched fruit focus and greedy production
controller are broadly sufficient. Production remains V543; seventh place is not achieved.

## Implementation and verification

`SCARCE-DENIAL-DESIGN-2026-09-05.md` preceded implementation. Claude supplied a bounded read-only
patch (18 turns, 353.019 seconds, reported USD 1.543506); the primary agent reviewed, applied and
tested it. Prompt and raw response are archived under the preceding capital-release working root.
No delegated file write, platform action or Codex subagent was used.

The exporter adds a checked boolean `--resource-denial` option, false by default. The enabled
policy latches V439's initial plum/lemon selector and adds the scarce-kind bonus inside the live
production comparison, excluding owned trees. It applies while the opponent has at most two
workers or the unit already occupies the tree. Converting the old wood-rate units to the current
point-rate units changes the coefficient from 900 to 360000; integer rounding remains that of
the new controller. It is added after the rate division, not counted as bankable resources.

The rule does not replace the separate dead `chop_cell` opponent-crop bonus. Existing trip
feasibility, ownership protection, cell reservation, first-hire talents and persistent goals are
unchanged. In particular, a previously chosen chop goal is not rescored every turn; the new rule
does not solve stale commitments, future opponent actions or joint optimization across workers.
The enabled artifact is a two-worker ablation, not the default-four selected production source.

Seven added Rust fixtures exercise live target reversal, unrelated kind, owned-source exclusion,
third-enemy suppression, the on-tree exception, distinct worker reservations and focus reset/
latching. The full suite passed **456 tests in 171.15 seconds**, including 27 Rust fixtures under
eight mode/ceiling/denial combinations (216 nested fixtures). Targeted tests passed 51/51.

The disabled export matched all 900 previous cap2 commands. Readable and compact enabled exports
matched on those 900 inputs, with first control divergence on turn 3 on each map. All 1,200 official
development commands and 3,570 fresh-confirmation commands matched the respective exact local
programs. There were zero explicit runtime/protocol diagnostics and no retries in sixteen games.
The audits also made 160 repeatable startup/first-turn/exit trials, plus 30 preflight control trials.
Local startup measurements are not a reproduction of platform timing.

## Reused three-block development screen

Exact cap2 repeated identically against putibuzu in game 901541609: scores, inventories, ranks,
workforce, duration, normalized initial input and both command streams matched the archived game.
Each candidate initial state matched its existing cap2 reference.

| Opponent / seed / seat 0 | Cap2 parent | Cap2 + denial | Margin change |
|---|---:|---:|---:|
| putibuzu / 2609051701 | 203–263 L | 179–86 W | +153 |
| delineate / 2609051102 | 201–556 L | 137–154 L | +338 |
| Pony / 2609051603 | 286–156 W | 240–133 W | -23 |

Parent: 1/0/2, one point, mean own 230.00, opponent 325.00, margin -95.00, wood 55.67.
Enabled: 2/0/1, two points, mean own 185.33, opponent 124.33, margin +61.00, wood 44.67.
Game IDs are 901541620, 901541626 and 901541632 respectively. No failure is excluded.

Putibuzu no longer hires its second worker (previously turn 68), finishing with one wood to our
43. Delineate stops at two workers instead of three and banks 31 wood to our 33. The timing of
our first chop is 9/5/5, versus 5/5/5 for cap2: choosing the right trees matters more here than
chopping as early as possible. V439's older putibuzu win also used a carry-one second worker;
the original blanket capacity diagnosis did not explain that specific map.

This screen met the predeclared advancement condition, so the separate fresh protocol was
written before opening any of its six maps. These three development maps never became holdout.

## Fresh six-block confirmation

`SCARCE-DENIAL-CONFIRMATION-2026-09-05.md` fixed sources, opponents, seats, seeds, order, budget
and selection criteria. The authenticated pre-run board verified putibuzu rank 7, tonigineer 8,
norxondor_gorgonax 2 and Pony 60, with the same fixed agent identities used in collection.

| Opponent / seed / seat | V439 | Enabled | Margin change |
|---|---:|---:|---:|
| putibuzu / 2609054701 / 0 | 196–271 L | 178–289 L | -36 |
| putibuzu / 2609054702 / 1 | 216–257 L | 189–277 L | -47 |
| tonigineer / 2609054801 / 0 | 232–241 L | 218–277 L | -50 |
| norxondor / 2609054201 / 1 | 200–296 L | 183–325 L | -46 |
| Pony / 2609054601 / 0 | 231–59 W | 178–67 W | -61 |
| tonigineer / 2609054802 / 1 | 120–219 L | 127–149 L | +77 |

| Policy | W / D / L | Points | Mean own | Mean opponent | Mean margin | Mean wood |
|---|---|---:|---:|---:|---:|---:|
| V439 | 1 / 0 / 5 | 1 | 199.17 | 223.83 | -24.67 | 43.50 |
| Enabled | 1 / 0 / 5 | 1 | 178.83 | 230.67 | -51.83 | 42.83 |

Each policy goes 1/0/2 in seat 0 and 0/0/3 in seat 1. Per-opponent results are 0/0/2 versus
putibuzu, 0/0/2 versus tonigineer, 0/0/1 versus norxondor and 1/0/0 versus Pony. Mean paired
margin change is -27.17; zero match-point gain and zero target-opponent wins fail selection.

Enumerating all 46,656 empirical six-block bootstrap samples gives a mean margin-change interval
of [-52.67, +15.83] at the 2.5/97.5 percentiles. All observed outcome differences are zero, so
their bootstrap interval degenerates to [0,0] and the one-sided paired sign-randomization p is 1.
**That is not evidence of universal equivalence**: resampling cannot create unobserved outcome
flips. Six fixed-opponent blocks provide very limited uncertainty information and no unseen-policy
coverage or rank conversion. These maps are now consumed and must not be reused as holdout.

On both fresh putibuzu maps the opponent can and does hire on turn 1; starting fruit/iron stock
differs materially from the scarce development opening. This limits what cutting later trees
can do to that first purchase. It does not justify a post-hoc map selector trained on these six
results. The current candidate's broad production/coordination limitations remain unresolved.

## Familiar local panel

One 192-pair panel used the same eight maps, two seats and twelve proxy families. All V439 baseline
columns match the archived cap2 panel, including complete commands. No critical, unclassified or
other command issues were reported in the enabled games; all finish with two workers.

| Policy | W / D / L | Points | Own | Opponent | Margin | Wood |
|---|---|---:|---:|---:|---:|---:|
| V439 | 173 / 5 / 14 | 175.5 | 238.46 | 110.56 | 127.90 | 44.29 |
| Cap2 | 157 / 1 / 34 | 157.5 | 203.74 | 132.67 | 71.07 | 49.08 |
| Cap2 + denial | 157 / 2 / 33 | 158.0 | 193.79 | 118.84 | 74.95 | 46.78 |

Paired point changes versus cap2 by map: 0, -1, -0.5, -1, +1, +2, +1, -1. Detailed opponent-specific
W/D/L, points, both scores, margins, workforce and issue counts are in `panel-analysis.json`.
This is a familiar regression panel, not evidence of real named-agent fidelity.

## Other finding and next direction

`TRAIN-EGRESS-FINDING-2026-09-05.md` documents a separate verified rules mistake: legal MOVE out
of the shack can precede TRAIN in the same turn. The wrong source comment was corrected, but
the gameplay timing fix was deliberately not bundled into this experiment.

Next: restore a trustworthy production baseline only with direct comparative evidence, and
evaluate integrated economy/coordination or existing reusable learning components. Do not keep
escalating the same fixed denial coefficient or publish a merely higher-scoring local variant.

## Artifacts and identity

All new artifacts are below `/data/separate_troll_farm-working/scarce-denial/2026-09-05/`:
`denial/`, `disabled-control/`, source manifests, binaries, frozen panel runner and TSV;
`field-plan.json`, `field/`, `references.json`, `export-audit.json`, `field-analysis.json`;
`confirmation-plan.json`, `confirmation/`, `confirmation-analysis.json`, analysis scripts/logs,
the pre-confirmation board, build/test/panel logs and the training-egress probe.

Enabled compact: 36,185 UTF-16 units, SHA-256
`f545ff7a4454a4d4124fe15b738c19437f4a59dffaa115758baa29aa747d9d18`.
Module: `c94830594d4fc1264d8b869dd3236f1b8ad9d80b1884459d3842cb2ea88b09db`.
Readable: `eab7431edbe16c48cca00cf5ebbe6945c34eeac126f6d69906d5c77f3f2d4268`.
Disabled compact: `316ef154552ae5eb91ef16843bb5e4779f7c2bb9c4de094361a5b6c162f5970a`.

Production `bot.rs`/`submission.rs` and the read-only neighbor are unchanged. No collector,
panel, test or denial-patch Claude process remains pending for this experiment.
