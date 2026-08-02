# progress: 20260802-top-player-final-independent-review

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T12:42:00Z
- Task: 20260802-top-player-final-independent-review
- Branch: agent/claude_1
- Requires acknowledgement: no
- Platform mutation performed: no

## Addendum to the handed-off review — I closed my own open question

The review report is **unchanged** at SHA-256
`78df9d640311cd7a84186e3026be1e4d132ec8ecac213cc8b6a89f7fa84b30dc`; this message adds detail
to one finding rather than amending it. No other conclusion moves.

In the handoff I flagged that "successful-two-worker top20 sides are 1,268" was not
reproducible and asked you for the predicate. Rather than leave that as homework I searched
exhaustively, so the finding is either withdrawn or actionable.

**Result: nothing produces 1,268 or 1,267.** I tried four base predicates —
`roster_final>=3`, `effect_trained>=2`, `train_count>=2`, `second_train_turn` non-null —
against ten modifiers (full-300 games, win, not-loss, seat 0, seat 1, opponent top20,
opponent not top20, `second_train_turn<=151`, `<=200`, none) and every pair of those
modifiers, counted both **per side** and **per distinct game**. No combination lands on the
published figure.

## The two nearest coherent readings

| reading | count |
|---|---:|
| top20 **sides** with `roster_final >= 3` | **1,330** |
| distinct top20-source **games** containing a ≥3-roster top20 side | **1,270** |
| the same, restricted to full 300-turn games — sides / games | 1,256 / 1,197 |
| the same, excluding top20-vs-top20 games | 1,164 / 1,164 |

The published 1,268 is two below the game-level count and sixty below the side-level count.
`1,330 − 1,270 = 60` is exactly the number of top20-vs-top20 games in which **both** sides
scaled, which is the usual place a sides/games mix-up shows up.

Given that the correction adopted in review was `1,267 → 1,268`, a one-unit change, my best
guess is that the intended unit is **games** and two were later dropped — but that is a guess
and I am not putting it in the review. The distribution, for whatever helps you locate it:
`roster_final` over the 2,853 top20 sides is {1: 36, 2: 1,487, 3: 516, 4: 621, 5: 146,
6: 32, 7: 15}.

## What this changes in my verdict

Nothing. The verdict stays `ACCEPT_WITH_CORRECTIONS`, and this remains the least important of
the five corrections — it is a benchmark-context descriptive count, not load-bearing for any
ranked idea. Corrections 1 and 4 are still the two I would not ship without.

What it does change is the ask: instead of "please state the predicate", it is now
**"1,268 appears to be unreachable from the committed package — either name the predicate or
replace the figure with 1,330 sides / 1,270 games."** If the number came from the host cache
rather than the shared corpus, then it is `HOST_ONLY` and should be labelled that way, which
is a cheaper fix than re-deriving it.

## Status

No other work in flight. The review handoff at `cc95a09` awaits your disposition; I have
started nothing new and my write set is unchanged.
