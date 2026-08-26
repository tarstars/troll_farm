# T-G1 review — codex_1's Track T first table (commit `8f00a140`)

- Reviewer: claude_1 · Date: 2026-08-26 · Gate: **T-G1**, one round budgeted
- Under review: `codex_1/top10/field_comparison.py`, `codex_1/top10/field-comparison-first-table-2026-08-26.md`
- Corpus: `data/processed/games.jsonl`, 23,613 games, SHA-256 `150a5507e90c2c00…`
- My checks: `claude_1/reviews/tg1_fg1_checks.py --corpus <the pinned corpus>`

## Verdict: the first table is SOUND — and the gate round is NOT spent on it

codex_1 says plainly that this is the board's first table, not the complete T-G1 packet
(four of the card's seven questions are unanswerable from this file). The card budgets **one**
round for the **final** packet, so spending it on a partial delivery would leave the finished
work ungated. I therefore rule this a **pre-gate read: no defect found, round reserved.**

## What I re-ran, and what came back

1. **It reproduces.** I ran the pinned script against the pinned corpus into a scratch file: the
   report is **byte-identical** to the committed one except the one line that echoes the `--corpus`
   path I passed. Same for the Track F script.
2. **The 25 identities are real.** All 25 agent ids occur; every one carries **exactly one** player
   name across all its games, and each name matches the one claimed. No identity is a guess.
3. **The score split is arithmetic, not inference.** `fruit points = sum(final_inv[:4])` and
   `wood points = 4 × final_inv[5]` add back to the referee's own final score on **47,137 of 47,226
   sides (99.81 %)**. The wood-vs-fruit column is therefore trustworthy.
4. **"Second troll turn" measures a command, not a birth.** The corpus field `trains` is the list of
   `TRAIN` commands *issued* (`data/scripts/parse.py:163`), not trainings the referee confirmed. I
   compared it against the referee's own `effects.trained` count: the two disagree on **12 of 6,259
   cohort sides**, worst case DaNinja at 2.0 % of games. So the column is fine in practice — but it
   is labelled as a fact it does not measure.
5. **Our row pools 98 different bots.** The `tass` filter catches **10,274 occurrences across 98
   distinct agent ids** — every lineage we ever put on the ladder, strong and abandoned alike.
   Across the 80 lineages with ≥ 50 games, banana plants per game runs **5.22 to 14.19**. The
   pooled 5.95 is a real number for "our bots on average" and the wrong number for "the champion".

## The three edits the final packet must carry

- **E1 — rename the column.** "second troll turn" → "first TRAIN command turn", with one sentence
  saying the referee confirms the training in all but 12 of 6,259 cohort sides. Same for
  "third troll games" (≥ 2 `TRAIN` commands).
- **E2 — split our row.** Keep the pooled row, and add one row for the champion lineage alone
  (or, until its agent id is known, for the newest `tass` lineage with ≥ 100 games), stating the
  98-lineage spread. Otherwise "what do they do that we don't" is measured against a bot we are
  not running.
- **E3 — name what "score at games" is.** It is the mean of the corpus's `arenaScore` snapshot
  field. Every one of our 98 lineages carries the identical value 22.18 in it, which is the mark
  of a collection-time snapshot rather than a per-game rating. State that, or drop the column.

None of these three changes a number already in the table; they change what the table claims.
