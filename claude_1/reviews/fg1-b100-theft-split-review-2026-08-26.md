# F-G1 review — codex_1's b100 theft-split read (commit `8f00a140`)

- Reviewer: claude_1 · Date: 2026-08-26 · Gate: **F-G1**, one round budgeted, round **spent**
- Under review: `codex_1/farm/b100_theft_split.py`, `codex_1/farm/b100-theft-split-2026-08-26.md`
- My checks: `claude_1/reviews/tg1_fg1_checks.py --corpus <the pinned corpus>`

## Verdict: ACCEPT-WITH-EDIT

The stop is right. The report's four rows are right to the unit. But the sentence that frames them
is wrong, and it is the sentence a reader would act on.

## The stop is right

I re-derived every cell of the four-row table straight from the corpus: final scores, our banana
plants and harvest units, theirs. All eight numbers match. The harvest count sums the referee's
singular and plural spellings (`harvested 1 BANANA` / `harvested 3 BANANAs`,
`data/scripts/parse.py:196`), which is the correct total in units, not a double count.

And the attribution genuinely cannot be done here. A processed row holds final command counts,
successful plant totals, training turns, six score snapshots and the final inventory — no per-turn
commands, no tree identity, no harvest ownership. Every map starts with banana trees either side
may harvest, so an opponent's banana total cannot be split into "ate ours" and "grew their own".
The five-turn abort sensor is likewise not reconstructible. The card says stop in exactly this
case. **DEAD CONDITION MET is confirmed.**

## The defect: "all four b100 ladder games" — the b100 played 98

The b100 (agent `6590083`, submission `41081195`) has **98 distinct ladder games** recorded, with
final scores, in a source the card explicitly allows:
`data/analysis/live-agent-6553250/owner-banana-factory-b100-reconvergence-checkpoint-20260802T162907Z.json`
(plus its 16:00Z initial checkpoint, whose 10 games are a subset). **The corpus holds 4 of those
98** — and the 4 it holds are from the *initial* checkpoint, taken when the bot's ladder score was
still 0.0 at rank 130. They are the first games it ever played, not a sample of its career.

That matters for the one thing this read still can say. Across all 98 games the b100's mean margin
is **+4.6** with **49 losses** and a worst game of **−348** — a bot that wins narrowly and loses
catastrophically, which is how a 12.99 arrives next to the parent's 23.3. The four-game slice in
the report shows one 386–486 loss and cannot show that shape at all.

## The exact edits

- **E1 —** replace "All four b100 ladder games are in the hash-pinned corpus" (handoff and report)
  with: *the b100 played 98 recorded ladder games; the corpus holds 4 of them, all from the first
  batch, and the table below covers only those 4.*
- **E2 —** add the one attributable fact the card is entitled to, from the checkpoint file named
  above: 98 games, mean margin +4.6, 49 losses, worst −348. No attribution, no farm claim — a
  count, from a permitted source, that the theft question can be reopened against later.

With E1 and E2 the read is complete and Track F's answer stands as: **the split cannot be measured
from what we kept.** If the owner wants it measured, that is a new card, and it needs replays with
per-turn commands — which we did not keep for these games.
