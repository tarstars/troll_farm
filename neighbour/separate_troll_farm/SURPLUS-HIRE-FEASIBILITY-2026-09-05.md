# Surplus-funded third hire: the stock premise does not occur

Verdict: **do not implement the proposed zero-detour surplus-hire wrapper** on the strength
of these data. Across all160 exact V439 archived games,43,263 audited turns and41,879
two-worker pre-action states, **zero states** can already afford any proposed specialist.
There are also zero eligible states for the fixed2/2/0/2 worker. All160 maps contain iron.
Buckets with >=60/120/180 turns remaining are consequently also zero.

This is a necessary-condition census, not a competitive candidate test. It rules out the
stock premise on this archive, not every possible hiring economy or unseen game. No policy
was built, no adaptive comparison or platform request was spent on this unactivated idea.

## What was counted

Exactly two current own workers; spec movement1..3/capacity2..3/harvest0/chop2..3.
Cost base2: PLUM2+ms², LEMON2+cc², APPLE2, IRON2+chop² (iron charged on iron maps).
The fixed2/2/0/2 bill is6PLUM6LEMON2APPLE6IRON,14 banked score points, not20.
Actual indices are PLUM0/LEMON1/APPLE2/BANANA3/IRON4/WOOD5; map iron is `+`.
No score is assigned to iron. No travel, crowding, same-turn spending, seed reservation,
future income, opponent reaction or early ending is modeled. Eligibility alone would not
prove a positive return; here even that necessary condition is absent.

The official archive outcome groups reconstruct95W/0D/65L from ranks, not score signs.
Physical seat comes from agent.index, not list order. Archive hash, exactagent6704418,
160 unique games, full state/command alignment, both command streams and official outcomes
are checked fail-closed. Deadline buckets use301-turn, not hindsight recorded game length.

## Delegation and corrections

Claude strategic proposal70186 completed USD1.1469935; census4134 completed USD0.6543495.
Primary verified/corrected:

- V439 permits at most two units, not necessarily exactly two on arbitrary games. Its opening
  can already select one capacity3/chop2+ specialist. It cannot add a second hired specialist.
- The selector has a general greedy fallback for three or more workers after its two-unit
  joint-selection case. Extra workers are not inherently left without commands.
- Banked affordability does not prove positive expected return. Nearest-tree travel is not a
  multi-trip repayment bound; conditioned older third-hire gains do not prove all hires pay.
- Do not restore the historical universal nonnegative turn100/200-score gate. Those are
  diagnostics under EVALUATION.md, not mandatory selection conditions.
- Claude correctly caught an incorrect IRON5 hint in the primary prompt; IRON is4, WOOD5.
  The implementation uses the verified constants. Primary corrected its hindsight horizon,
  empty-group summary, exact-agent guard, missing-command checks and invalid-stock handling.

New audit_surplus_hire.py and13 fixture cases pass, with50 passing across the related audit
suite. The previously completed full562-test suite covers the frozen home-growth integration;
it predates these new standalone audit files. Working evidence:
`/data/separate_troll_farm-working/planning/2026-09-05/v439-surplus-hire-feasibility.{json,log}`.

## Next substantive decision

Revisit whole-economy alternatives, particularly the archived V564 artifact, under the current
outcome/deployment contract. Its old early-score gate is not authority, but its large final score
is not proof of ladder strength either. Verify exact artifacts and competitive evidence before
freezing any new comparison; no such platform schedule has been authorized by this census.
