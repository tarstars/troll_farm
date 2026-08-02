# Owner-directed top-score opponent-crop deployment — 2026-08-02

Phase: **complete; submission accepted once; adverse clean first health**

## Selection

The canonical registry's unfiltered `best --min-finished 100 --evidence mature --scope all`
query ranks `opponent-crop-b100-e6-slim` first by mature source median: 24.89/160 at historical
rank 17/107. Exact selected source:

`cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`, 64,522 bytes,
SHA-256 `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`.

The mandatory preflight flags `REJECTED_SOURCE`, `SINGLE_MATURE_RUN`, and `CROSS_ERA`.
Historically the candidate scored only about +0.12 over its matched control and its frozen
protocol rejected it. These warnings were surfaced before mutation. The owner nevertheless
directed submission of the best scored bot, making this an explicit owner-directed override,
not a qualified scientific promotion.

## Baseline and mutation

Immediately before replacement, authenticated reads showed far-denial agent `6589510` at
19.37, rank 73/130, with 160/160 listed battles finished and zero pending. Candidate size/hash
and sacred resident SHA `fff6669b…` were exact; `local_codex_1` was the sole controller.

The remotely published start record is `2ff6866`. `cgauto/api_submit.py` made one accepted
`TestSession/submit` call. The sanitized terminal result is HTTP 200, submission `41079653`,
`SUBMIT-OK`. No retry occurred. The new agent is `6589709`.

## Immediate identity and first health

The first battle-list read has ten rows. All ten carry exact agent `6589709` and submission
`41079653`; all are pending. There are no unexpected rows. The old leaderboard row remains
visible until games complete.

The immutable checkpoint observed at 2026-08-02T07:47:43Z then captured 22 exact matching
rows: 21 finished and parsed plus one pending. Agent `6589709` is 13.58 at rank 123/130;
the filtered leaderboard is 13.01 at rank 126. The game record is 11W/10L, mean margin
+29.667, one catastrophic loss (4.8%), negative-margin mass 559, no unexpected rows or
fetch failures, clean identity, and zero validity/runtime signals. Evidence:
`owner-top-score-opponent-crop-initial-checkpoint-20260802T074741Z.json`, SHA-256
`d3e7eb491aa82d988bbfccfd4aaea2660c7a6f071a8021ea67af40146ea9fc05`.

This is an adverse immature first health. It does not validate the historical 24.89 score
in the current 130-agent era and does not reverse the frozen protocol's rejection. The
owner-directed submission request is complete; subsequent monitoring is read-only and no
second Arena cycle is in flight.

No session handle, cookie, credential, or secret response content is stored in this report.

## Mature follow-up

The later wide-corpus catch-up recovered the active submission's complete 160-game window.
The repository-standard checkpoint observed at 2026-08-02T09:40:12Z confirms exact
agent/submission identity, 160/160 finished and parsed, zero pending/unexpected/fetch/runtime
faults, score 23.12 at rank 32/130, 101W/2T/57L, mean margin +23.44375, ten catastrophic
losses (6.25%), and negative-margin mass 3,318. Evidence:
`owner-top-score-opponent-crop-mature-checkpoint-20260802T094000Z.json`, SHA-256
`f6367e7feb6b1a6ce219eaedb08d575e3d1ab9ce0ec6eab2be7671ac38f13831`.

This current-era repeat is 1.77 below the historical 24.89 run. Their cross-era median is
24.005, now below the preseed source's four-run median 24.19. The live result is materially
better than the displaced far-denial row (19.37), but it still does not overturn the
candidate's frozen matched-control rejection or meet the 24.70/25.40 project checkpoints.
