# S3 putibuzu-shaped rollout-plus-beam scope audit — 2026-07-31

## Verdict

**`DISTINCT_MULTI_GATED`.**

The public architecture is not a duplicate of any one closed project family. Its
combination is materially distinct: about 30 joint task/local-action candidates, one
lightweight greedy continuation for both sides, values averaged at depths
3/5/7/9/12, a three-ply `5→3→all` beam on large maps, and explicit-opponent maximin
on small maps.

That novelty does not authorize an implementation. Two blockers are direct:

1. the postmortem does not define the weights, tie rules, candidate construction,
   beam semantics, map cutoff, opponent breadth, or chance handling needed to reproduce
   the intervention;
2. this project's continuation/opponent models do not support a prospective value claim.
   The live single-continuation rollout scored 21.7 versus its 24.1 control, and the
   eight-model repair produced no robust opening selection.

Runtime is a third, provisional blocker. Exact-resident search misses the 50 ms contract
at much smaller breadth, while an older lightweight GoldElite subset did fit. This does
not prove that a clean-room lightweight S3-shaped policy is impossible; it proves that
the current exact-resident substrate is not its implementation path.

## What the public source actually specifies

Putibuzu's 2026-05-25
[CodinGame post](https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/5)
describes:

- roughly 30 joint combinations from each troll's top-three tree targets plus local
  actions;
- a greedy priority policy for generation and both-side rollout, with a different
  training order for the opponent;
- averaging values observed after 3, 5, 7, 9, and 12 turns;
- a large-map three-ply beam summarized as `5→3→all`;
- small-map explicit opponent candidates and maximin selection;
- a composite score using score differential, carried-resource distance, tree
  ownership/proximity, and future production.

The post is unusually informative architectural prose, but it is not source code.
In particular, it does not say whether the five depth values reuse one trajectory, what
`5→3→all` prunes at each ply, or how evaluator components are weighted. Rank #2 shows
that the complete contest bot was strong; it does not isolate the search's causal value
or its latency.

## Closure matrix

| Family | Root/action scope | Search/value | Measured result | Relation to S3 |
|---|---|---|---|---|
| Phases 3–8 opening rollout | Turn one; resident plus 28 first-worker alternatives | Terminal rollout; one model, then eight-model robust rules | local +2.717; live 21.7 vs 24.1; robust selectors inert | rollout overlap only; no repeated joint beam |
| GoldElite residual | Warm; one unit's MOVE target only | 4-turn screen, top four at 16 turns, two continuations | +15.906; p95 28.53 ms, max 49.67 | closest lightweight staged-pruning subset; not resident-backed |
| Phase 11 | Shared turn-three root; two complete macros | terminal and 240-turn liquid value; compatible-model minimax | +26.081 terminal; p95 279.460 ms; proxy precision 88.33% | strict action-count subset, much longer horizon |
| Phase 16 | Warm resident roots; ≤14 joint commands, one MOVE changed | 4/top-four/16, two ambiguity models | broad +1.200 at p95 130.047 ms; bank +0.508 at p95 92.852 ms | closest exact-resident strict subset |
| D36 | Resident two-worker roots; joint work bundles, repeated ≤4 boundaries | offline terminal resident upper bound | +10.633 margin vs +25 | semantic sequence overlap; no online primitive beam |
| D84 | Threat roots; control plus ≤3 semantic responses | 1/2/4/8/16/32 decisions; liquid value | best +3.160 vs +5.620; ideal p95 64.840 ms at 32 | narrow multi-horizon subset; not a direct h12 timing bound |
| S1 | Endgame; exact simultaneous MOVE outcomes | exact branch count, no selector | median 600/max 6,400 one-ply outcomes | establishes that ~30-candidate pruning is approximate |

The complete machine-readable matrix is
`s3-putibuzu-rollout-beam-scope-audit-result-2026-07-31.json`.

## Why it is distinct

Every ingredient has an ancestor here, but no experiment combines all of these:

- broad joint choices that can alter local direct actions;
- repeated search rather than one opening or one residual target;
- five-depth value aggregation;
- three-ply beam sequencing;
- map-conditioned switch to explicit-opponent maximin;
- a dedicated lightweight policy owning candidate generation and continuation.

Phase 16 is the nearest structural comparison, but it deliberately freezes every direct
action and changes at most one MOVE target. D36 permits joint semantic work, but uses an
offline terminal oracle at completion boundaries. Phase 11 changes a whole macro but
chooses between only two alternatives. Calling S3 a duplicate would therefore erase the
dimensions that define it.

## Why it is not ready

### Specification

There is no single reproducible S3 candidate yet. Choosing weights, deduplication,
tie-breaking, beam meaning, opponent breadth, or a map threshold would be research
design. Such a candidate can be legitimate, but it must be called **clean-room
S3-shaped**, not a reproduction or a controlled test of putibuzu.

### Opponent and value model

The public bot rolls both sides with its own greedy model and changes the opponent
training order. We do not possess either exact policy. More importantly, this project
already observed the failure mode:

- the single-CompactGold terminal selector passed locally, then all three diagnosed
  live activations lost;
- its rating settled at 21.7 versus 24.1 for exact control;
- the 29-option/eight-continuation repair found no robust selection;
- seven local models never reproduced the field's immediate training, BossReal matched
  0/22 such commands, and the best full-opening agreement was 8/60.

Small-map maximin is a meaningful difference, not a cure by assertion: the public post
does not freeze its opponent-candidate grammar or demonstrate that our field is inside it.

### Runtime

The evidence cuts both ways and must stay qualified:

- a lightweight GoldElite residual with four-turn screening and top-four sixteen-turn
  continuation achieved p95 28.53 ms and max 49.67 ms;
- moving the same idea onto the exact resident cost p95 130.047 ms broadly and
  92.852 ms even bank-only;
- D84's optimistic, already-rooted, actual-opponent, ideal-parallel lower bound reached
  p95 64.840 ms at the first useful 32-decision horizon.

Therefore the raw engine is not the sole blocker, but exact resident continuation is.
A new lightweight greedy policy could change the timing class—and simultaneously becomes
a new full policy/value model whose fidelity and transfer are unproved.

## Disposition

Keep S3 open only as a peer-review-gated successor decision, **S3a: search-kernel
specification and latency preflight**. It is not authorized by this audit.

Before S3a, resolve N4 Phase A and choose one ownership fork explicitly:

1. use exact resident candidate pairs, making S3a a sequence/beam layer that must be
   separated from N4; or
2. define a clean-room broad greedy candidate/continuation policy, acknowledging that
   this is a new controller rather than resident lookahead or a putibuzu reproduction.

If authorized, S3a should first freeze every omitted semantic, then use only consumed
states for deterministic legality and warm-latency measurement. It should clear timing
before any value panel, new map block, candidate, packaging, or Arena action.

No source, analyzer, test, game, map, panel, candidate, submission, or Arena state was
created or changed by S3.
