# T-G1 — review of Track T's final field comparison — **ACCEPT WITH EDIT**

- Task `20260826-track-t-top10-field-comparison`, board row T-1. One review round (the card's whole
  review budget). Reviewed: codex_1 `20260826T151538Z`, artifacts at `agent/codex_1`
  `ce6b58bbf9227cc88b985fcf6e6e8372ecd29501`.
- Verdict: **ACCEPT WITH EDIT.** The measurement is sound and the headline conclusion holds. Three
  edits, none of which changes a number or the banana-farm decision. No defect that blocks.

## What I checked, and how

I could not re-derive the tables from the corpus: `data/processed/turns.jsonl.gz` is not on this
machine (it was produced on the host and copied to codex_1's VM; it is gitignored). So this is not
an independent re-measurement and I do not claim it is one. What I did instead:

1. **Recomputed every cell of every table in the report from the report's own pinned JSON**
   (`codex_1/top10/per-turn-field-comparison-2026-08-26.json` at `ce6b58bb`), for all the named
   bots. **Every cell reproduces**, including the bucket totals, the provenance rows, the
   plant→chop latencies, the last-30 verb counts, the idle percentages and the contention proxy.
   No transcription error anywhere in the report.
2. **Checked the corpus identifiers against T-2's manifest** (`data/processed/turns.manifest.json`,
   which I do have): 13,313,072 turn records, 0 parse failures, 12 seat-turns without stdout,
   sha256 `1e0ea236…` — all three of the report's claims match the manifest exactly.
3. **Checked the score arithmetic behind the ranked tricks**: the "+11 to +82 points/game" band is
   exactly Stounate +11.3, yaichi +65.0, goq +60.2, skotz +82.3 against our 187.4. Correct, and
   correctly labelled as association and not cause.
4. **Checked the two tables that come from different corpora against each other** — which is where
   the first edit comes from.

## Edit 1 — §1 and §3 print the same column header for two different measurements

§1's `banana plants/game` is **successful plants** from `games.jsonl` (the first table says so:
"Plant counts are successful plants per game"). §3's `total` column is **issued PLANT commands**
from `turns.jsonl.gz`. The final report puts them three sections apart with nothing saying they are
different measurements, and for our own row they disagree: **5.95 in §1, 5.98 in §3**. A reader who
notices will think one of them is wrong.

They are both right, and the comparison is worth keeping rather than hiding: for all four heavy
planters the two numbers are **identical to two decimals** (yaichi 29.03, Stounate 27.26,
skotz 36.20, goq 27.57), i.e. essentially every banana PLANT they issue succeeds, while ours shows
a small gap. That is a free cross-validation of the whole provenance method — the issued-command
corpus and the outcome corpus agree — and it is currently invisible. **Edit: label §1's column
"successful plants/game (`games.jsonl`)" and §3's "issued PLANT commands/game (`turns.jsonl.gz`)",
and say in one line that they agree to 2 dp for the four heavy planters.**

## Edit 2 — the JSON's `corpus.rows` is not the corpus's row count

`per-turn-field-comparison-2026-08-26.json` carries `"corpus": {"path": …, "sha256": "1e0ea236…",
"rows": 4476062}`. Sitting beside the path and the hash of the full corpus, that reads as "this
corpus has 4.48 M rows", which contradicts both the manifest and the report's own prose
("13,313,072-row turn corpus"). It is in fact the **sum of the 26 measured agents' seat-turns** — I
checked: summing `seat_turns` over all 26 rows gives exactly 4,476,062. So the analysis covers
**33.6 %** of the corpus, which is the correct and expected coverage, since only 26 identities are
measured. **Edit: rename the key to `seat_turn_rows_measured` (or add `corpus_rows: 13313072`
beside it).** Nothing about the numbers changes; a future reader pinning that file should not be
able to mistake it for a truncated read.

## Edit 3 — §5's own table contains a finding §5's prose does not read

The last-30-turns table omits the `PICK` and `MINE` columns, and `PICK` is a column where we differ
(ours 3.16/game; yaichi 0.00, skotz 0.00, goq 0.99, Stounate 3.43). More important, the table
prints and then walks past the largest gap in it: **`MOVE`, ours 7.96 per game against 32.18–38.19
for all four leaders** — a four-fold difference, in the same endgame window where our `CHOP` (23.97)
is the highest of any bot in the table. §5 concludes "ours does not lack terminal planting or
banking commands", which is true, but the striking cell is that in the last 30 turns our trolls
barely move while everyone else's are still travelling. That is either a real endgame parking
behaviour — directly relevant to the parked-troll line — or an artifact of how our bot emits
`WAIT` versus `MOVE`, and either answer is worth one sentence. **Edit: restore the two columns and
say which of the two the `MOVE` gap is, or mark it explicitly as unexplained.**

## What I am not asking for

- No re-run. The tables are correct as computed and the corpus is hash-pinned.
- No change to the banana-farm decision. "A persistent banana-to-wood lifecycle, not an isolated
  farm graft" is supported by the three independent columns the report gives it (early planting,
  own-coordinate harvest, plant→chop latency), and the honest boundary — issued commands, not
  referee acceptance — is stated in the right places, including in the definitions block of the
  JSON itself.
- No challenge to the suppression finding. Ours issues **8.73** chops per game at opponent-planted
  coordinates against 0.53–2.46 for the leaders; "they suppress more" is refuted by their own data,
  and the report says so plainly rather than softening it.

## One thing the report does that I want on the record as right

It labels `no_work_verb_turn_pct` and the same-target MOVE count as **proxies**, names them as not
the P3/P4 goal-based detectors, and then declines to draw an idle conclusion from them (35.3 % vs
our 35.5 % — no differentiator). Given how much of this programme's history is inert checks read as
results, an author who measures something, sees no signal, and says "no signal" is the behaviour to
keep.
