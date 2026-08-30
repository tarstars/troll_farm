# Review — T-3 goal-keeping ladder cost: ACCEPT the stop, with one check added

Task `20260827-goal-keeping-ladder-cost`. Reviewer: claude_1, chartered single review round.
Under review: `codex_1/analytics/goal_keeping_ladder_cost.py`, its result JSON and report at
`agent/codex_1@1e7943c8d30cba44b8017a4fdb900dd379b3dc98`.

## Verdict: ACCEPT — under-determined, stop under the charter's dead condition

The report claims exactly what its data supports and no more. The refusal to price a three-point
ladder gap from four games, all of them heavy losses, is the right call, and the report names the
three telemetry fields the hypothesis needs and does not have. I found nothing to send back.

## What I reproduced independently

I re-ran the arm split and the movement measures over the same hash-pinned slice
(`/home/tarstars/prj/troll_farm-codex_1/data/raw/slice`, manifest 212 entries) from my own worktree:

- arms: 208 champion-v6 versus 4 keep-v6 — matches.
- reversals per 100 moves: champion 11.95, keep 16.10 — matches to the reported digits.

## The check the report does not run, and its result

The report's one directional observation (more A-to-B-to-A reversals under keep) has an obvious
confound it does not test: **all four keep games are bad losses, and the report itself shows the
champion walks more in bad losses than in wins.** If reversals rose with losing, the keep number
would be an outcome artifact rather than a rigidity signal. So I split the champion arm the same way:

| group | games | reversals per 100 moves |
|---|---:|---:|
| champion, all | 208 | 11.95 |
| champion, wins | 111 | 11.87 |
| champion, bad losses (margin ≤ −50) | 49 | **11.53** |
| keep rule, all (all bad losses) | 4 | **16.10** |

The champion's reversal rate is flat across outcomes — losing badly does *not* make the champion
reverse more. So the keep arm's 16.10 is **not** explained by its games all being losses. The
directional observation survives the confound. It still cannot be priced from four games, and it
still does not distinguish rigidity from opponent, map or seat mix; this only removes one rival
explanation. I suggest the script report `reverse_per_100_moves` inside each outcome split, so a
future balanced slice gets this for free.

## Two small robustness notes, neither blocking

1. **Arm classification is fail-open.** The script keys the arm off a hardcoded source hash prefix
   (`04e3db43…` = keep, *everything else* = champion), while the manifest already carries an
   explicit `arm` field (`A champion+v6`, `B keep-rule+v6`). On this slice the two agree on all
   212 entries — I checked, zero mismatches — so no number is affected. But if a third bot's games
   ever enter a slice they would be silently counted as champion. Key off `arm`, or fail loudly on
   an unknown prefix.
2. **`turns_with_keep_active` counts `k` non-zero**, folding `k=1` and `k=2` together. That is a
   fair reading of "keep active", but the report should say so where it quotes 1,003 unit-turns.

## What would settle the owner's question

I agree with the report's answer and add one point about where the scarcity comes from. The 208:4
split is not a bad cut of a good pool — it is the two arms' actual ladder exposure. So the missing
ingredient is **more keep-arm ladder play**, not a wider slice of what is already collected, plus
the three absent telemetry fields (goal termination reason, contested-target outcome, per-resource
score deltas). A rerun on today's pool would return the same four games. That is the owner's call
to make, and this task stops until it is made.
