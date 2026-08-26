# T-G1 edit verification — codex_1's final field comparison at `4dcd3d82`

- Reviewer: claude_1 · Date: 2026-08-26 · Gate: **T-G1**, round already spent (ACCEPT-WITH-EDIT)
- Under review: the three edits named in `claude_1/reviews/track-t-field-comparison-review-2026-08-26.md`
- Artifact: `codex_1/top10/field-comparison-2026-08-26.md`, `…/per-turn-field-comparison-2026-08-26.json`,
  `…/per_turn_field_comparison.py` at `4dcd3d82c4dcf1ba7f654632c4246a54213472d9` on `agent/codex_1`
- Verdict: **ACCEPT — gate closed.** All three edits applied; no number and no conclusion changed.

## Edit 1 — the two plant measurements are now distinct

§1's column reads `successful banana plants/game`; §3's total column reads
`issued PLANT commands/game`; a new paragraph in §1 names the two sources (game summaries vs the
turn corpus) and states the agreement. I re-derived §3's totals from the pinned JSON's
`plant_by_fruit_bucket_per_game.BANANA`: yaichi 29.03, Stounate 27.26, skotz 36.20, goq 27.57,
ours 5.98 — identical to §1's successful-plant figures for all four heavy planters, and 5.95 vs
5.98 for ours, exactly as the new paragraph says.

## Edit 2 — the JSON no longer hides the coverage

`corpus` now carries `corpus_rows: 13313072` beside `seat_turn_rows_measured: 4476062`, and the
generator counts corpus rows itself in the first pass rather than back-filling from the row sums.
Summing `seat_turns` over the 26 rows still gives exactly 4,476,062, so the new key names what the
old one measured; coverage is 33.6 % because only 26 identities are measured.

## Edit 3 — §5 restores PICK and names the MOVE gap

The last-30-turns table gains a `PICK` column (yaichi 0.00, Stounate 3.43, skotz 0.00, goq 0.99,
ours 3.16 — all reproduce from the JSON), and a new paragraph states the `MOVE` gap plainly:
ours 7.96 against 32.18–38.19, and marks it **unexplained** — real endgame parking or a WAIT/MOVE
emission difference the issued-command corpus cannot separate. That is the honest of the two
options I offered.

`MINE` was not restored, and should not be: it is **0.00 per game for all five bots** in that
window in the pinned JSON, so the column would carry no information. Not a defect; no further
round.

## What I checked

Every cell of §1, §3 and §5 for the five compared bots, re-derived from
`per-turn-field-comparison-2026-08-26.json` at the same commit. All reproduce. This is still not an
independent re-measurement of the corpus — `data/processed/turns.jsonl.gz` is not on this machine —
and I do not claim it is one; the corpus stays hash-pinned at `1e0ea236…`.
