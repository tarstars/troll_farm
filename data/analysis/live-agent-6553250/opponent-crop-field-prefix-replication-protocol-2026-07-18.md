# Opponent-crop candidate — Phase 20 independent prefix replication protocol, 2026-07-18

## Why a new block

Phase 19 passed every activation/provenance check but failed its unrelated full-game replay
reproduction threshold (43/80 versus 60). The platform source is byte-identical to the resident.
Only the first candidate divergence on an exactly reproduced resident prefix is causal selection
evidence; later official states remain the resident trajectory. Phase 19 stays failed.

Test the corrected estimand only on official games not used by the field census or Phase 19. The
read-only battle listing contains 82 older completed games from the same resident agent `6559583`
and submission `41009991`, immediately following the frozen recent-80 window. Freeze them before
fetching any result: the first 40 in listing order are discovery and the remaining 42 are unchanged
replication. Store their exact IDs in a hashable manifest.

The result-blind manifest is now frozen at
`opponent-crop-field-prefix-manifest-2026-07-18.json`, SHA-256
`6c00ae08a7bdd1ef627698b3b51a2b05b9de86f861bd1c0e361bc12a65158109`. Discovery's ordered ID
list hashes to `d974efcd7474...`; replication's hashes to `ba59a22e7e91...`. No game result from
either block was fetched before these hashes and gates were written.

## Fixed method

Reuse the exact resident, 64,522-byte candidate, decoder, stdout-neutral crop probe, and
first-divergence attribution from Phase 19. For each game, count activation only when:

- resident actions equal recorded actions on every turn through and including the turn immediately
  before candidate divergence;
- the diagnostic candidate is stdout-identical to the production candidate;
- at least one selected candidate target at the first divergence is an active, referee-attributed
  opponent crop with current ETA at most six;
- resident reproduction remains exact for at least ten further official turns, or through game end
  when fewer than ten turns remain.

Full-stream resident reproduction and historical outcome cohorts are descriptive only. No value,
threshold, source, or treatment may change between the two blocks.

## Frozen gates

Discovery (40 games) passes only with all fetches/decodes clean, at least 24 admissible stable-prefix
activations, at least eight distinct activated opponents, 100% first-divergence crop/ETA explanation,
and no production stderr. If it passes, replication (42 games) requires the same checks with at
least 25 activations and eight opponents.

Both blocks must pass before drafting any controlled-transfer protocol. Even a double pass does
not authorize a game, submission, holdout inspection, or `cgauto/api_submit.py` change.

## Execution result

Both predeclared blocks pass without a fetch, decode, attribution, or stderr failure:

| Block | Games | Stable-prefix activations | Rate | Distinct opponents | Full-stream exact (descriptive) | Gate |
|---|---:|---:|---:|---:|---:|---|
| Discovery | 40 | 32 | 80.00% | 19 | 20 | pass |
| Unchanged replication | 42 | 29 | 69.05% | 16 | 24 | pass |
| Combined | 82 | 61 | 74.39% | 33 | 44 | pass |

All 61 stable first divergences select an active attributed opponent crop within ETA six. Median
first divergence is turn 45 (range 4--224). Five of six catastrophic losses activate, versus
38/52 wins and 18/24 ordinary losses. The treatment is therefore broad rather than a classifier
for catastrophic games; the replicated local outcome gates, not activation selectivity, justify
its value.

Combining the original recent-80 audit and this independent 82-game block gives 125/162 official
games with a valid first activation across 56 distinct opponents. The Phase-19 full-stream gate
remains failed; Phase 20 validates the corrected causal prefix independently and does not rewrite
that result.

Machine-readable results:
`opponent-crop-field-prefix-discovery-2026-07-18.json` and
`opponent-crop-field-prefix-replication-2026-07-18.json` in this directory.

## Verdict

Phase 20 passes discovery and unchanged replication. The exact local candidate has now cleared
generated-map outcome replication, standalone parity/size/latency gates, and independent official-
state mechanism replication. A small capacity-controlled arena protocol may be drafted. Execution
still requires separate authorization because it resets the active resident and changes external
arena state.
