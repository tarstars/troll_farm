# V468 and V469, the chop-target bonuses removed: measured, small, closed — 2026-09-02 (loop iteration 3)

Queue item 1 after iteration 2: the planner's base chop score is already wood per trip turn, so
the only steering toward poor trees comes from two bonuses on top of it. V468 removes the denial
bonus (+900/(1+distance to the enemy shack) for `type_to_cut` trees while the opponent has at most
two trolls); V469 also zeroes the opponent-crop priority (+100/+200 for opponent-planted trees
within six turns). Everything else is V439. Built by `build_v468_chop_targets.py`; development
panel (8 maps, 192 paired games) and, because both were positive at every checkpoint, the 16 fresh
maps (384 paired games). Gate `panel_gate.py`, mechanism `panel_diagnostics.py`.

| candidate | panel | own score at 100 / 200 / 300 | delta at 300 | opponents' delta | wood delta | W/T/L | gate |
|---|---|---|---|---|---|---|---|
| baseline V439 | dev 8 | 85.0 / 169.2 / 238.5 | | | | 173/5/14 | |
| V468 no denial bonus | dev 8 | 93.0 / 176.2 / 247.2 | +8.8 | -2.3 | +0.7 | 177/3/12 | FAIL (+40 not met) |
| V469 no denial, no crop priority | dev 8 | 96.0 / 180.1 / 249.9 | +11.4 | +7.0 | +1.3 | 176/3/13 | FAIL |
| baseline V439 | fresh 16 | 78.7 / 151.8 / 211.2 | | | | 347/13/24 | |
| V468 | fresh 16 | 81.8 / 155.0 / 214.6 | +3.4 | +1.9 | -0.1 | 356/8/20 | FAIL |
| V469 | fresh 16 | 83.3 / 155.9 / 213.7 | +2.5 | +2.3 | 0.0 | 353/7/24 | FAIL |

## What the panels showed

- The gain is harvest time, not wood: on the development panel V468 harvests 69 fruits a game
  against 63 and moves 9 times less, while wood is within one unit of the baseline in every
  panel. The denial detours were costing the starter apple-harvest turns.
- The effect is map- and opponent-dependent. On the fresh maps the own-score gain shrinks to +3.4
  and +2.5, about one standard error of a 384-game mean, and it splits by family: removing the
  bonuses gains 10 to 15 points against the weaker families (resident, norx, silver_boss,
  legend_v8) and loses 7 to 14 against the stronger ones (gold_adaptive, legend_v3, legend_v7),
  where the denial actually slows the opponent.
- Removing the crop priority as well (V469) raises own score slightly more on the development
  panel but hands the opponents wood (+1.7 a game), so its margin is worse than V468's.

## Consequences

1. Item 1 is closed: the second troll's wood per trip is not limited by the target bonuses. The
   wood lever must be more chopping troll-turns (a third troll) or fewer turns per trip, not
   target choice.
2. V468 is a small, safe improvement in own score with the same wood and a better win count on
   both panels. It is not adopted as the development baseline, which is the owner's decision
   under the charter; the owner may want it folded into the next submitted line as a free +3.
3. Next: the harvest talent with an apple reserve (queue item 2 becomes 1), then the mined-iron
   third troll.

## Submission-gate steps run on 2026-09-02 evening (queue item 0, no submission)

The compact upload file `candidate-v468-no-denial-bonus.min.rs` (96,848 UTF-16 units) was run
through the remaining gate steps under the owner's overnight authorization. Results are under
`/data/separate_troll_farm-working/nn/bench/v468-*.json`; V439's readings on the same 400
records (`panel-400-seed2026.jsonl`, both seat orders) are the comparison.

| leg | bot | W / T / L | wins | mean margin seat A, seat B |
|---|---|---|---|---|
| champion of record | V468 | 238 / 81 / 81 | 59.5 % | +13.35, +16.39 |
| champion of record | V439 | 249 / 55 / 96 | 62.2 % | +12.22, +14.06 |
| orchard 6 | V468 | 358 / 11 / 31 | 89.5 % | +49.53, +48.82 |
| orchard 6 | V439 | 377 / 1 / 22 | 94.2 % | +55.05, +53.30 |

Readable-versus-compact audit (`audit_candidate_command_streams.py`, 160 archived V440 games,
agent 6684947, 45,050 turns): 0 games with a changed turn. The readable and compact programs are
the same bot. The `baseline_exact` count is 1 because V468 is compared with V440's recorded
commands, which it is meant to differ from; that column is not part of this check.

Reading: the champion leg is 2.7 points below V439, inside one standard error of a 400-game win
rate (2.4 points), with a better mean margin and 26 more ties; the orchard 6 leg is 4.7 points
below, about two standard errors, with the margin 5 points lower. This matches the fresh-map
finding above: removing the denial bonuses gains against the weak families and gives some back
against the strong ones, and the champion and orchard 6 are strong. V468 is neither a duel
regression nor a duel gain; it is the same bot with +3 own score on fresh maps. Nothing was
submitted; whether to upload it is the owner's call.
