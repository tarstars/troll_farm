# V606--V608 starter-isolated delayed mature orchard: carry-two payout ceiling, closed -- 2026-09-05

## Verdict

V606--V608 kept exact V468 behavior through turn 100 and activated a harvest-free, typed,
size-four orchard lane on the trained axe from turn 101. The isolation mechanism worked: V607
made tracked worker plots inert only in the inherited planner's cloned view, kept real-state
lifecycle decisions, removed V606's extra inherited harvest and crop-chop work, and had zero
movement issues. It did not improve the economy. V607 scored +0.00/-6.04/-5.79 at turns
100/200/final, banked 1.04 less wood, and went 15/0/9 against V468's 19/1/4. V608's cap-eight
arm was identical to cap-six in every selected TSV field and every command stream.

The referee rule explains the failure. Wood is awarded only when a tree dies, and any amount
beyond the killing trolls' free carry capacity is discarded. V607's `3/2/0/2` axe can therefore
collect only two of a size-four tree's four wood. It pays the mature tree's full health and travel
cost but throws away half the intended payout. V607 emitted 8.88 more chop commands, ran 9.67
turns longer, and still banked less wood. No arm entered the frozen 192-game panel, fresh maps,
duels, packaging audit, or platform publication.

## Candidate family

`build_v606_starter_isolated_delayed_orchard.py` derives all arms from V595 and reuses the tested
V603 typed lifecycle machinery with three material changes:

- the opening enumeration is capped at harvest power zero, retaining V468's exact
  `TRAIN 3 2 0 2` at median turn 6;
- worker intervention is disabled before turn 101, so the complete command stream through turn
  100 is identical to V468;
- tracked crops are felled directly at size four, with no harvest-talent bill or worker harvest;
- seeds come only from bank fruit above a one-fruit reserve;
- worker plot attempts are typed and reconciled against the real state;
- V607/V608 clone the planner view and set tracked plants' health and fruit to zero, leaving the
  plant objects present so their cells remain occupied while removing them from V468's targets;
- the inherited planner runs on that optional clone, while reconciliation, late-game rules,
  worker routing, felling, and plant recording all use the real view.

| arm | plot cap | starter isolation | compact UTF-16 units |
|---|---:|---|---:|
| V606 | 6 | no, timing control | 97,783 |
| V607 | 6 | yes | 97,782 |
| V608 | 8 | yes | 97,782 |

V606 and V607 normalize to exact equality after changing the isolation Boolean. V607 and V608
normalize to exact equality after changing the cap. All readable programs compile, and their
compact forms remain at least 2,217 UTF-16 units below the platform limit.

## Behavior smoke

Each arm ran map seed 9,941,000 in both seats against all 12 frozen opponent families: 24 paired
games per arm. Deltas are candidate minus exact V468, whose mean score was
94.67/160.67/215.46 and whose mean wood was 53.21.

| arm | turn 100 | turn 200 | final | candidate W/T/L | wood delta | opponent score delta | decision |
|---|---:|---:|---:|---:|---:|---:|---:|
| V606 control | +0.00 | -5.38 | -4.88 | 15/0/9 | -0.67 | +32.17 | reject |
| V607 isolated cap 6 | +0.00 | -6.04 | -5.79 | 15/0/9 | -1.04 | +31.75 | reject |
| V608 isolated cap 8 | +0.00 | -6.04 | -5.79 | 15/0/9 | -1.04 | +31.75 | reject |

All arms matched V468's worker count, train specification, train turn, and every command through
turn 100. Median first divergence was turn 101. Mean changed command turns were 166.08 for V606
and 166.71 for V607/V608. V606 had two rows with one noncritical blocked move each; both isolated
arms had zero issues, critical issues, or unclassified issues. The gate failure is not a jam.

The cap-eight panel is byte-for-byte behaviorally identical to cap six across all 24 games. The
sixth live slot is never the active limiter: available seed, completed fells, or remaining time
stops expansion before a seventh plot can change a decision.

## Isolation effect

The isolation Boolean does materially change the intended boundary. Full-game commands per role
show what it removed:

| command | V606 starter | V607 starter | isolation delta |
|---|---:|---:|---:|
| `CHOP` | 130.88 | 102.25 | -28.63 |
| `HARVEST` | 3.29 | 2.25 | -1.04 |
| `PLANT` | 5.25 | 3.96 | -1.29 |
| `MOVE` | 112.29 | 147.67 | +35.38 |

V606's real tracked plots remain visible to V468, so the starter helps service them. V607's inert
planner plants remove that attraction: starter harvests return almost to V468's 2.00 and the two
noncritical movement blockages disappear. Yet V607 loses another 0.92 final score and 0.37 wood
relative to V606. Shared servicing was inefficient, but it occasionally added carrying capacity
or damage at a mature fell; removing it exposes the worker's payout mismatch rather than creating
new income.

## Carry-capacity mechanism

The isolated arm's aggregate stream is active, legal, and economically worse:

| per-game measure | V468 | V607 | delta |
|---|---:|---:|---:|
| score | 215.46 | 209.67 | -5.79 |
| wood | 53.21 | 52.17 | -1.04 |
| game turns | 272.46 | 282.13 | +9.67 |
| all `CHOP` commands | 182.79 | 191.67 | +8.88 |
| all `MOVE` commands | 275.67 | 278.71 | +3.04 |
| all `WAIT` commands | 11.00 | 19.38 | +8.38 |
| all `DROP` commands | 38.71 | 33.88 | -4.83 |
| worker `PLANT` commands | 8.58 | 11.21 | +2.63 |

The lower observed wood per chop is 0.272 for V607 versus 0.291 for V468. The candidate creates
more worker plots and performs more damage, but waits for full maturity, makes fewer deposits,
and cannot carry the full result.

The authoritative Java referee and the Rust parity engine agree: on the killing chop the referee
loops over the tree's size and adds wood only while a participating troll has free capacity; any
remaining wood disappears with the dead plant. With one carry-two axe, every size-four fell banks
at most two wood. The usual full-payout mature efficiencies therefore halve for this worker: a
size-four banana needs three power-two chops for at most two collected wood, plum/lemon six, and
apple ten. V607's worker plant stream includes 6.38 bananas, 2.75 lemons, and 2.08 apples per game,
so the expensive non-banana cases amplify the mismatch.

This provides a new, narrow precondition for another mature-orchard attempt: the worker must have
carry capacity three or four, and the extra lemon training bill must be measured independently.
A capability-only control is required because changing the second-worker specification also
changes train timing and the turn-100 checkpoint. Only if that prefix cost recovers can the
isolated mature lane exploit the larger death payout.

## Verification and integrity

- focused builder tests: 12 passed, covering harvest-zero training, activation boundary, role
  slot, typed reconciliation, real-versus-masked views, reserve, cap normalization, standalone
  compilation, and compact limit;
- complete repository suite: 250 passed in 64.20 seconds;
- canonical runners, build logs, panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v606-v608-starter-isolated/`;
- V606/V607/V608 runner SHA-256:
  `5828ce01ed3c102f5c5ea02531020365b8b8c605671cc7b92247a6da555063a9` /
  `3d1b02c872d55509d8ea35dc24c12d063813b0f5f1cfb8e4b3e0cb9baafb6ff5` /
  `f5f6379732de0701d0c0b066456fe8d61c2d91d466bff7ee1bdf72164e621240`;
- panel SHA-256:
  `5f799a935cb4d4fee72c05dd4de071a5c7e93eadd0ed51ee99a4875f6430c78e` /
  `ca1e58a6164cb9b4f8b87742d7d8f2a2d2e6cbfc2278d1d734c962f18db139e9` /
  `3e9739bcbbc70a33e91a9ae2a7ada44c583d8ce5e9cbdede97d219fdd0fa2396`;
- gate SHA-256:
  `891cd02253e9297e1521de1ef239ac53d98a326d442f7a5cce06678b3a0ca127` /
  `bf488b31134ca7c5acbde8e10b4d8ebffe699852d6f9ff403dc560a9ac8733bf` /
  `547dc967d7d9a708408673394d32063e009a01bd3476443e3ec32e01cb54df77`;
- diagnostics SHA-256:
  `e6d470e76ea0c6951f4d2f4c2370aa3755032d3334d1df71c5d802857ca393c1` /
  `465216d90f7872439682f3906f328ff80cc88015e62d248af4bce2a8be17eea6` /
  `8b764e765604ed1bd1da03eee0ce17efa63cd06e5d77dfd5cdc53f15e4670b4e`;
- module SHA-256:
  `e15b235963e746ee85f50c66528a47a3539700e03e96f6d8557ee712b714de8d` /
  `07d8956e2c327fc6d9012c0b2e40296621db5d2b706d38c6058f43e6b41a6c4f` /
  `9cc7692c22477c949ae73277337952de792f875dc20660a3e1458e7e9782228b`;
- compact SHA-256:
  `2a59e42e447fff07dde0ee98ee087d80e14000217979cc451d64d81c0fa2564f` /
  `37a0a284ff05525193c096b2274837709b671baae30694bc9e9dae1ba907f18d` /
  `f70da5fa0894a3c92a32dc7a5559ef7bc163dcc547cb76ec6428d4da83c332d2`;
- builder/test SHA-256:
  `561391b7be64a170bedefcd8f70946f8deb7a898bfd66e6c308525171948ec12` /
  `dab511749628a29714efca287fd8f2f79ead8a8afd91f8099b541141e6336d2b`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, retaining its pre-existing
  modified `data/processed/stats.json` and untracked
  `data/panels/top5-ab-20260902T115338Z.json`.
