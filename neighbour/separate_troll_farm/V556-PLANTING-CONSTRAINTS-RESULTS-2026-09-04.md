# V556 planting-constraint audit result

## Outcome

V543's public planting gap is a policy and crop lock, not a shortage of seeds or usable cells.
Against the three active rating-18+ opponents, V543 produced 53 distinct tree generations and its
opponents produced 183. Opponent production accelerated after turn 100 and was 89% banana; V543's
production slowed and contained no bananas at all.

After V543's fourth worker existed, all 276 audited pre-cutoff states had banked or carried banana
and usable source-orchard geometry. A ripe banana was reachable by a producer on 273 states, but
the producers harvested banana zero times. The six-tree maintenance rule suppressed another tree
on 188 states; the remaining 88 had an open slot, yet the 21 successful post-training plantings
were 19 lemons and two apples. The existing orchard perpetuates the fruit already being harvested
instead of converting the wood pipeline to the much cheaper-to-fell banana.

V556 is a measurement, not a candidate. The audit found no near-free action override: on the 88
top open-slot states, the two producers issued 134 moves, 20 harvests, 15 plants, six drops, and
one wait. A species conversion needs a deliberately valued route, so no Rust or platform artifact
changed and no panel or submission was opened.

## Method

`audit_planting_constraints.py` decodes the frozen 160-game V543 package and retains the same 21
active rating-14+ games as V555: 13 losses, eight wins, and three rating-18+ losses. Plant commands
and before/after states reconstruct distinct tree generations, ownership, species, birth and death.
Every V543 plant command created one distinct generation. Five lower-rated opponent games issued
duplicate or unsuccessful commands, so the audit reports actual generation births separately from
raw command count; the rating-18+ subset has no mismatch.

On each state through turn 275 the audit reproduces R1FA's source geometry: reachable grass on the
own half, at most four path cells from a bank door, with no existing plant or unit. It also
reproduces source capacity for the fixed second- and third-hire bills. Six live own trees are not
treated as an unconditional cap: a missing training source can correctly demand a seventh tree.
Only after the bill has no source shortage does six mean maintenance is saturated.

When planting demand exists, the mutually exclusive state labels are relevant seed absent, eligible cell absent,
seed in the bank, carried-seed travel, or carried seed currently on a valid source cell. Producer
ids are the two lowest own unit ids, matching the Rust controller. Consecutive equal constraints
are collapsed into episodes. Nine focused pytest tests cover geometry, exclusions, constraint
precedence, above-cap training demand, producer identity, banana supply, ownership and reuse, and
episode collapse.

## Distinct planting cadence

| population | V543 generations | opponent generations | V543 banana | opponent banana |
|---|---:|---:|---:|---:|
| all 21 rating-14+ games | 444 (21.14/game) | 795 (37.86/game) | 10 | 704 |
| 13 losses | 263 (20.23/game) | 561 (43.15/game) | 4 | 503 |
| 8 wins | 181 (22.63/game) | 234 (29.25/game) | 6 | 201 |
| 3 rating-18+ losses | 53 (17.67/game) | 183 (61.00/game) | 0 | 163 |

The top subset's time profile identifies compounding rather than an opening draw difference:

| birth turn | V543 generations | opponent generations |
|---|---:|---:|
| 1--100 | 23 | 13 |
| 101--200 | 16 | 91 |
| 201--300 | 14 | 79 |

V543 leads planting early, then falls from 23 generations to 16 and 14 while the opponents rise to
91 and 79. Their 163 bananas are 89.1% of all 183 generations. V543 instead creates 42 lemons,
five apples and six plums. This agrees with the referee economics: every mature species yields four
wood, but a banana has six health against 12 for plum/lemon and 20 for apple.

## Constraint states

| measure through turn 275 | 13 losses | 8 wins | rating-18+ losses |
|---|---:|---:|---:|
| state turns | 3,575 | 2,200 | 825 |
| mean live own trees | 5.49 | 4.90 | 5.56 |
| cap-saturated turns | 1,476 | 685 | 354 |
| cell-absent turns | 13 | 8 | 3 |
| mean refill run after first reaching six | 7.43 | 15.07 | 14.14 |
| post-fourth-worker turns | 1,223 | 784 | 276 |
| those with banana supply | 1,223 | 769 | 276 |
| those with reachable ripe banana | 1,151 | 542 | 273 |
| banana blocked by saturated maintenance | 766 | 375 | 188 |
| banana supply plus an open slot | 457 | 394 | 88 |
| producer banana harvests | 8 | 7 | 0 |

Every loss reached six live own trees. Losses held more live sources than wins and refilled drops
below six twice as quickly, so "cannot maintain the orchard" is the wrong diagnosis. Geometry is
also negligible: it is absent on only 13 of 3,575 loss states. After the fourth worker appears,
banana stock is present on every loss state, but only four of 134 subsequent pre-cutoff plantings
are banana. The top three are the extreme, clean version: banana supply and geometry on 276 of 276
states, no banana harvest, and no banana planting.

The 188/88 top split explains the lock. When six sources live, maintenance refuses an additional
banana. When a slot opens, a producer is normally already harvesting or carrying lemon/apple from
the established source route, so that fruit refills the slot. Merely changing the cap would repeat
V546, which gained 20.27 final score over V543 but inherited the dense controller's 72.9-point
turn-100 deficit against the required V468 baseline.

## Next mechanism

The next candidate translates the useful part of this evidence to the required V468 base without
inheriting R1FA's slow opening. It will preserve exact V468 commands through turn 100 and keep its
two-worker roster, then admit a bounded near-shack banana reserve only after nearby wild wood is
depleted. Bananas will be allowed to mature before the axe uses them. This is not another full
controller handoff, training-bill farm, or unconditional cap increase.

The neighboring read-only project independently records the same candidate mechanism in
`coordination/tasks/20260904-champion-prefix-orchard.md`: exact champion prefix, no third troll,
and a near reserve after wild trees within four bank steps disappear. Its verified inputs are that
a mature banana is worth 16 score at six health and that the median map has 11.5 free planting
cells within two shack steps. That file is a design for an unfinished experiment, not a result;
no neighbor implementation, parameter, output, or worktree change was used here. Its evidence
sharpens the next candidate while V556 supplies the independent live species diagnosis.

## Limits and verification

An empty source cell ignores hidden persistent goal reservations and is therefore an upper bound.
Likewise, a carried seed standing on a valid cell is not called free: planting there may abandon a
better reserved plot or another job. The audit measures state and command availability, not the
counterfactual score cost of diverting a worker. That cost belongs in the paired V468 panel.

- focused tests: 9 passed
- frozen package SHA-256: `ccc45a23ea8ecc17ecb4215d8d52b4993e00c33fb830f6ad0b1786d6c713cbd1`
- audit JSON SHA-256: `9641e256cf2fe3ce6cc3846b756835ae6dd4e6d6c5098d5b83ebdc66f9003bd2`
- archived JSON: `/data/separate_troll_farm-working/archive/2026-09-04-v556-planting-constraints/planting-constraints.json`
- analyzer SHA-256: `825fea0dc8b2c2451eede1e3d46ea77f8990f2ae2591a3f512f377eaf72f5d21`
- neighboring design SHA-256 at read-only HEAD `370fa63c`: `05a90aaf3722e86bec597e3e9517cba3120ff995c60da252d62027e9b28b7185`
- unchanged `bot.rs` SHA-256: `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`
- unchanged `submission.rs` SHA-256: `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
