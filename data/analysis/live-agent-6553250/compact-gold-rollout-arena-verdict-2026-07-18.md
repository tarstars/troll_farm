# CompactGold rollout controlled arena verdict — 2026-07-18

## Outcome

**REJECT the rollout candidate and retain the slim promoted resident.**  The fresh same-source
capacity control converged to 24.1.  The candidate reached 120 listed games at 21.7, a -2.4
rating delta against that control and -3.4 below the frozen 25.1 promotion bar.  All 123 games
available at the closing audit were valid and contained no timeout/runtime signal.  The exact
resident source was restored as submission `41009991`; the arena changed from candidate agent
`6559513` to resident agent `6559583` at 10:40:33 MSK.

This is a deployment rejection under an unpaired live-rating protocol.  Replay forensics make
single-continuation overconfidence the leading mechanism diagnosis, but do not turn the rating
test into a paired causal estimate.

## Frozen artifacts and gate

| Role | Source | Bytes | SHA-256 |
|---|---|---:|---|
| Resident/control | `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | 62,725 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| Candidate | `candidate-agent6553250-compact-gold-rollout30.min.rs` | 90,643 | `f5df1f760791a21ad0193469c132fea02ebaa2856b33f62213765205b3b59370` |

The protocol was frozen before the first write in
`compact-gold-rollout-arena-protocol-2026-07-18.md`.  It required a healthy same-code control,
at least 120 games, and two mature control reads at least five minutes apart within 0.5.  With
the measured control at 24.1, the candidate promotion bar was 25.1 and the rejection boundary
was below 23.6.  A candidate below that boundary after the minimum sample was restored
immediately; a second mature candidate read was not required for a clear rejection.

## Capacity control

- Pre-reset resident: agent `6557204`, rank 23/104 Legend at 24.4.
- Same-source submission: `41009795` at 09:31:01 MSK; agent `6559490`.
- No compile, runtime, timeout, or game-arrival problem appeared.

| Read | Listed games | Score |
|---|---:|---:|
| +5 min | 26 | 19.6 |
| +10 min | 45 | 21.3 |
| +20 min | 85 | 21.2 |
| +25 min | 100 | 22.5 |
| +31 min | 120 | 23.4 |
| 10:03:06 MSK | 125 | 23.6 |
| 10:08:10 MSK | 142 | 24.1 |

The two closing reads were 5:04 apart and differed by exactly 0.5.  The final score was only
0.3 below the pre-reset 24.4, so the capacity gate passed.  Around +20 minutes its recent 30
games were 20 wins with average scores 199--187 and +12 average margin.

## Candidate trial

- Candidate submission: `41009911` at 10:08:31 MSK; agent `6559513`.
- The new agent landed at 10:09:45 with the expected cold-start score of 17.8.

| Approximate age | Listed games | Score | Same-code control near that age |
|---|---:|---:|---:|
| +5 min | 30 | 20.7 | 19.6 |
| +10 min | 47 | 23.1 | 21.3 |
| +15 min | 62 | 22.4 | 20.3 |
| +20 min | 82 | 21.6 | 21.2 |
| +25 min | 103 | 21.3 | 22.5 at 100 games |
| +29 min | 120 | 21.7 | 23.4 at 120 games |

The attractive early curve did not persist.  At the formal 120-game read the candidate was
2.4 points below the mature 24.1 control and 1.9 below the rejection boundary.  The closing
validity audit then fetched 123/123 results with zero errors; every candidate agent record had
`valid=true`, and no timeout, time-limit, exceeded, or invalid marker appeared in its agent,
tooltip, or metadata fields.  An earlier recent-30 window was 12 wins with -24 average margin;
the closing recent 30 was 13 wins.  Runtime safety passed, but arena value failed.

## Restoration

Before restoration, the resident file was rechecked at 62,725 bytes and SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.  Submission
`41009991` succeeded, and the authoritative arena read changed to new agent `6559583` at
10:40:33 MSK.  `cgauto/api_submit.py` was not edited by this protocol and still points
to the slim resident.  At the post-restoration check the new resident had already accumulated
66 games; its latest 30 were 21 wins with +54 average margin.  Its rating was still in ordinary
cold-start reconvergence and is not used as a new comparison bracket.

## Activation-aware replay forensics

The battle endpoint discards the old submission list after a replacement lands, but two
disjoint recent-30 snapshots had been captured before restoration.  Their 60 explicit game IDs
were frozen in `compact-gold-rollout-arena-known-games-2026-07-18.json`.  This is 60/123 games,
not a complete or random arena sample.

`cgauto/arena_rollout_forensics.py` reconstructs the exact candidate-relative turn-one input
from each official replay and compiles a probe whose only change is a selector marker on stderr.
Its stdout matched the arena's recorded first command in **60/60** games.

| Reconstructed branch | Games | Wins | Mean arena margin | Median margin |
|---|---:|---:|---:|---:|
| Exact resident fallback | 57 | 25 | +2.0 | -10 |
| Max-bank harvest-0 option | 3 | 0 | -23.7 | -26 |

The option activations were:

| Game | Opponent | First-turn option train | Arena margin |
|---:|---|---|---:|
| `896220422` | FreZzz | `2/1/0/2` | -26 |
| `896220808` | daaskare | `2/2/0/1` | -18 |
| `896220941` | a76a44 | `1/1/0/1` | -27 |

All three selected maps lost, but selection is map-dependent: this observational split cannot
tell us what the resident would have scored against the same adaptive opponent on the same map.
It is mechanism-localizing evidence, not a paired treatment effect.

## Continuation-model audit

The exact Rust rollout harness evaluated control and option on all 60 reconstructed initial
states against GoldElite, SchedBot, MyBot, and SilverBoss, both orientations.  A separate
CompactGold pass matched GoldElite terminal margins and deltas in **120/120** seat cells.  The
recorded `CompactGold delta > 30` rule reconstructed the same three arena activations exactly.

| Game | Gold/Compact delta | Sched delta | MyBot delta | Silver delta | Worst |
|---:|---:|---:|---:|---:|---:|
| `896220422` | +197 | +7 | -13 | +1 | -13 |
| `896220808` | +38 | -28 | -9 | -29 | -29 |
| `896220941` | +176 | -40 | -68 | -33 | -68 |

Every selected map had at least one negative continuation.  Two of three were positive under
Gold alone and negative under all three alternatives.  The largest Gold predictions (+197 and
+176) were not the safest decisions, so merely increasing the `>30` threshold is not a sound
repair.  A unanimous-positive continuation veto would have selected none of these three maps.

## Conclusions at several abstraction levels

1. **Platform/runtime:** healthy.  Same-code capacity converged, games arrived continuously,
   all candidate games were valid, and no deadline path was observed.
2. **Deployment:** rejected.  The candidate failed the frozen live comparison by a large margin,
   and the resident was restored exactly.
3. **Controller:** the terminal engine and long horizon are not enough when selection conditions
   on a single deterministic opponent response.  The missing quantity is opponent uncertainty.
4. **Option:** an immediate max-bank harvest-0 worker is not field-robust merely because one
   continuation predicts a large terminal advantage.
5. **Statistics:** sparse local gains and a positive simulator holdout did not guarantee rating
   transfer.  Future gates must report activation-conditioned robustness and preserve an
   abstaining resident option.

## Next move

Close this exact candidate, exact option, and single-CompactGold selector.  Do not retune its
threshold on these consumed arena games, and do not submit an ensemble wrapper immediately.
The next research iteration is an **offline robust first-move option search**:

1. enumerate a small, coherent library of complete first-train policies plus exact resident;
2. score every option under multiple deliberately different opponent continuations;
3. select by a predeclared lower-confidence/minimax-regret rule with exact-resident abstention,
   not by the largest single-model terminal margin;
4. reject the iteration if robust selection is inert or if value depends on one continuation;
5. freeze options and selector before opening a new untouched map block;
6. consider distillation or a compact live architecture only after that prospective block
   shows nonzero robust value and bounded downside.

The 60 arena maps are diagnosis data only.  They may test reconstruction and expose model
disagreement, but they must not become the acceptance holdout for the next selector.

## Reproducible evidence

- `compact-gold-rollout-arena-protocol-2026-07-18.md`
- `compact-gold-rollout-arena-known-games-2026-07-18.json`
- `compact-gold-rollout-arena-forensics-known60-2026-07-18.json`
- `compact-gold-rollout-arena-model-audit-known60-2026-07-18.json`
- `compact-gold-rollout-arena-known60.maps`
- `compact-gold-rollout-arena-known60-model-rollouts.tsv`
- `compact-gold-rollout-arena-known60-compact-rollouts.tsv`
- `phase3-phase5-rollout-study-2026-07-17.md`
- `cgauto/arena_rollout_forensics.py`
- `cgauto/arena_rollout_model_audit.py`
