# V439 observed chopping: valid actions, different late resource returns

This is a diagnostic of the unchanged live V439, not a policy comparison. All160 exact-agent
replays and43,263 turns are retained, covering55 opponents; zero frame/decode/alignment failures,
zero missing ratings. Official ranks give95W/0D/65L,95 match points. Mean own/opponent scores
207.4125/200.0625, margin7.35, banked wood45.13125/46.04375. Live agent6704418 was independently
read again this stage: rank28/177, rating23.43. Top-seven remains unachieved.

The Claude-assisted implementation and repair were reviewed before running. Primary corrected
seat identity independent of agent-list order, TRAIN versus unit-command parsing, temporary/output
scope, missing-command guards and ownership accounting. All29 focused tests pass. Source and
decoder-adapter hashes are embedded in `v439-chop-productivity.json`; the frozen input hash is
`2f5a05a8a132fca7edcf9eafbea6f9d8406b8d866753b2f22b0995cb5759c0d5`.

## Findings and limits

Across **25,882 own single-CHOP actor-turns**, there are zero full carriers, zero nonpositive
chopping-power actors, zero absent pre-state plants, and zero ambiguous own actor commands.
The proposed simple explanation of invalid/full-carrier CHOP waste is unsupported. Opponents'
one missing-actor and15 multi-action cases remain counted outside clean-actor statistics.

The replay-rated22–25 band has83 games:42W/0D/41L,42 points, mean own/opponent score
209.1084/219.8434, margin-10.7349, banked wood46.4096/51.1807, zero recorded deployment failures.
Within its41 losses, own/opponent score is202.7317/290.7317 and banked wood46.2927/70.2195.
Own banked wood is similar in the42 wins (46.5238); opponent wood is32.5952 there. Conditioning
on final outcome is descriptive and does not identify the effect of changing a particular action.

For the41 losses, the following counts use straightforward single-CHOP actors only. “Positive
event” means observed same-actor carried-WOOD increase after the turn, **not banked score or a
causal action-value estimate**. Many zero deltas are necessary intermediate hits on a living tree.

| Turn window | Own CHOPs / positive events / wood increase | Opponent CHOPs / positive events / wood increase |
|---|---:|---:|
| 1–100 | 2,273 / 355 / 571 | 860 / 207 / 364 |
| 101–219 | 2,727 / 620 / 835 | 2,142 / 567 / 1,209 |
| 220+ | 1,903 / 413 / 492 | 2,241 / 536 / 1,345 |

Own carried wood per positive event falls from1.61 to1.35 to1.19, while the opponents' increases
from1.76 to2.13 to2.51. Worker capacity, tree size, ownership/roles and simultaneous competition
can explain this; none is isolated by the aggregate table. The report separately retains broad
co-located-opponent-action buckets; these do not mean confirmed opposing CHOP damage. No blanket
“chop less,” “plant more” or “hire more” policy is selected from these figures.

## Secondary checks, explicitly weaker evidence

The historical early-farm helper was run on the same frozen archive, accepting births through
turn150 within Manhattan distance2 of the opponent shack. Its default outcome groups use score
sign, which omit four equal-score wood-tiebreak games. Primary therefore regrouped all160 rows
using official ranks. Within the22–25 band, mean uncontacted opponent generations are4.33 in
wins and6.20 in losses; opponent HARVEST commands on these generations are12.93 versus18.68.
Generation counts are similar (12.64/13.02). This suggests a candidate question about farm
interaction, not a causal diagnosis. The legacy helper does not separate ambiguous simultaneous
PLANT ownership, so its inferred generation attribution must not be treated as an exact oracle.

Observed score margins also do not prove losses were already decided before turn220. Among the
41 eventual band losses, the median margin after turn100 is+20 (all41 observed); after150 it is
+11 (39 still observed); after219 it is-15 (35 still observed,20 behind). These are different
survivor samples and omit unbanked capital. They are not “decisive-turn” counterfactuals.

## Next bounded decision

Claude's interpretation completed (session28707, USD0.1978205). Primary accepts its proposed
next stratification: free capacity1/2/3+, chop power1/2+, opponent co-location, turn window and
official outcome, with plant size/species and example actor-turns. Start with uncontested cells;
report event counts and positive-event wood, not just a pooled average. This can distinguish
composition effects from a within-role trend, not prove a strategy's causal effect.

Primary rejects the proposed larger-tree tiebreak as unjustified. `min(final_size, free_capacity)`
is the actual capacity limit, not an established ranking defect. Code also includes chopping and
return time plus an opponent-near crop bonus, so “nearest tree wins independent of size” is not
an accurate account of the selector. A larger tree cannot by itself increase a capacity-one
carrier's immediate collected wood. The proposed acceptance metrics of wood/tree size also
cannot replace paired outcomes, deployment gates and prospective confirmation in EVALUATION.md.
The crop-denial bonus is another possible contributor, but not yet a demonstrated failure cause.

All **539 regression tests passed in203.02 seconds**, after the new29 focused tests were added.
No agents, audits or test jobs remain active at this checkpoint. No gameplay
change, new planner packaging attempt, platform request or publication follows automatically.
The compiler-microoptimization queue remains paused after three deployment failures.

Evidence root: `/data/separate_troll_farm-working/planning/2026-09-05/`, files
`v439-chop-productivity.{json,log}`, `v439-early-farm-observations.json`, and
`claude-chop-{productivity,audit-fixes,findings}-{prompt.md,response.json}`.
