# V555 mature chopper-target audit result

## Outcome

V543 already chooses the best visible mature-tree cycle on 97.6% of comparable chop turns in its
21 active platform games against rating-14+ opponents. The 13 losses contain only ten actionable
miss episodes, six of them material, and not one actionable miss prefers an opponent-planted
tree. The archived platform wood gap is therefore not caused by the mature choppers choosing the
wrong exposed tree often enough to support a candidate.

V555 is a measurement, not a bot candidate. It changed no Rust gameplay source, gate input,
package, or platform agent. No panel or submission was opened.

## Audit population and corrections

`audit_chopper_targets.py` decodes the frozen 160-game V543 replay package, reconstructs every
plant generation from successful `PLANT` commands and state transitions, and labels it natural,
own, or opponent-planted. It retained the 21 non-timeout games whose opponent had rating at least
14.0: 13 losses and eight wins, including three games against rating-18+ opponents.

For each empty-handed power-2/3 worker that was actually chopping a current size-4 tree, the audit
scored all unreserved reachable size-4 trees by:

`wood / (travel turns + remaining chop turns + return turns + one drop turn)`

The first instrumentation pass exposed two invalid assumptions and its output was discarded.
Having chop power does not make a worker's `HARVEST` or `MINE` command a chopper decision, and a
replay `MOVE` coordinate is a per-turn waypoint rather than the planner's eventual tree target.
The final population therefore uses only actual `CHOP` commands on a live mature tree. A selected
tree stays in the comparison even if another worker also targets it; reservations suppress only
alternative trees. Seven focused pytest cases cover cycle cost, selection, reservations, carrying,
waypoint rejection, immature-tree rejection, provenance reuse, and episode collapse.

## Results

| population | mature chop turns | turns with a comparable cycle | selected best | strict misses | actionable misses | episodes | material turns |
|---|---:|---:|---:|---:|---:|---:|---:|
| all rating-14+ | 1,600 | 1,593 | 1,554 (97.6%) | 39 | 29 | 17 | 13 |
| 13 losses | 1,029 | 1,022 | 1,001 (98.0%) | 21 | 21 | 10 | 7 |
| 8 wins | 571 | 571 | 553 (96.8%) | 18 | 8 | 7 | 6 |
| rating-18+ | 162 | 162 | 154 (95.1%) | 8 | 8 | 3 | 3 |

A strict miss has a higher-rate same-state alternative. An actionable miss additionally requires
that the archived alternative tree survive until the projected arrival. Consecutive turns with
the same worker, selected tree, and best alternative collapse to one episode. A material miss
must gain at least 0.05 wood per turn and at least 25% over the selected cycle.

The loss subset's 21 actionable unit-turns collapse to ten decisions in eight games. Their best
alternative provenance is 15 natural and six own-planted unit-turns; it is zero opponent-planted.
Only seven turns across six episodes meet the material threshold. The mean advantage over all 21
loss misses is 0.059 wood per turn. The rating-18+ subset is smaller but agrees: all eight missed
unit-turns, collapsing to three episodes, prefer natural trees.

Across the entire population there is exactly one actionable opponent-planted alternative. It is
a single non-material turn in a game V543 won by four points: the estimated advantage is only
0.028 wood per turn, and the alternative disappears at the projected arrival boundary. That is
not evidence for reopening the already-failed opponent-tree priority branch.

## Interpretation and next question

The same-state optimizer is not perfect, but its residual errors are too sparse and too weak to
explain top opponents banking roughly twice the wood. More importantly, the mature losses do not
show V543 overlooking the opponent orchard. The prior platform profile and this audit together
point upstream: strong opponents create about 3.4 times as many trees, while V543 chooses well
once a mature tree is under its axe.

The next measurement will classify V543's planting constraint on those same replay states: seed
availability, usable empty cells, movement, cooldown, competing work, and training pressure. That
asks why the bot exposes only 17.7 trees against rating-18+ opponents' 61.0 without assuming that
another worker can be funded for free.

This audit is deliberately local and conservative. It does not infer hidden final intent from
`MOVE` waypoints, predict future growth, value fruit or denial, or claim that abandoning a chop is
strategically free. Those omissions make the observed small miss count an upper bound on a safe
mid-chop retargeting opportunity, not a promise of gain.

## Verification and artifacts

- focused tests: 7 passed
- frozen replay package SHA-256: `ccc45a23ea8ecc17ecb4215d8d52b4993e00c33fb830f6ad0b1786d6c713cbd1`
- final audit JSON SHA-256: `cce518ea780340510591a20272ad5761132caefbc74223cfcb8c73ff6e906963`
- archived JSON: `/data/separate_troll_farm-working/archive/2026-09-04-v555-chopper-target-audit/chopper-target-audit.json`
- `bot.rs` SHA-256: `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`
- `submission.rs` SHA-256: `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- frozen panel runner SHA-256: `9ad74518c8692da001e90a7cf259d8713aa96b575e138c3d5ce6de239c3c5cff`
- V468 baseline bridge SHA-256: `0178423a17af97c73ed2b1f7f8530bb0bb028bef16974d2f0aaaf078ce1bfc1e`
