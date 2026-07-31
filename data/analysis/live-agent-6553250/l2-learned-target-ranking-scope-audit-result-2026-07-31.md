# L2 learned target-ranking scope audit

Date: 2026-07-31
Verdict: **`N4_DEPENDENCY_GATED`**

## Decision

L2 does not currently name a third executable learned ranking experiment. The exact live
resident has one ordinary, material multi-worker ranking surface: exhaustive selection of
the compatible two-worker candidate pair with maximum summed immediate score. That is
precisely the peer-owned N4 Phase-A surface. Learning only an exact-score tie or reranking
unequal-score pairs both require N4's still-pending coverage, reconstruction, boundary,
and latency census; terminal-value labels additionally require a separately authorized
Phase B.

Every other plausible interpretation is inactive, transient opening/primitive policy,
a fixed invariant rewrite rather than a scheduler, or part of a closed tie/ranker family.
Do not create L2a, export candidates, label pairs, fit a scorer, edit source, or open a
panel before N4 is accepted.

## Exact live selection graph

The executable constructs `SecureOrchardBot::new()` at
`rust/src/bin/yamo_orchard_live.rs:6008-6019`. Its constructor wraps
`YamoBot::tuned_carry_regeneration_transit_idle_harvest()` at lines 3823-3832.
`task_market`, `banana_factory`, opponent-crop scoring, and `ScarceIntent` accretions are
not enabled by that chain and are excluded.

1. `YamoBot::commands` generates hand-written candidates with primitive commands,
   immediate scores, and semantic targets (lines 1535-1590).
2. With one unit, `select` takes the maximum candidate score (1362-1368).
3. With exactly two, it enumerates every target/stock-compatible pair, sums the two
   immediate scores, and retains the first strict maximum (1369-1388).
4. The greedy branch at 1390-1412 requires more than two units. It is unreachable because
   the exact resident's `can_train` hard-caps the roster at two.
5. The selected commands then pass through collision priority and a nearest-detour
   comparator (1425-1528).
6. The outer wrapper chooses one orchard mother by enemy distance then cell order
   (4173-4198), may replace the starter's action with a fixed orchard action, protects the
   mother, and reruns collision resolution (4482-4548, 5209-5428).

Thus "target ranking" must say whether it changes candidate generation, the one-unit
opening choice, the compatible pair, a path tie, or an outer orchard invariant. Those
objects have different authority and labels; they cannot share one learned experiment.

## Overlap and dependency matrix

| L2 reading | Label or teacher | Exact dependency/closure | Disposition |
|---|---|---|---|
| Exact-score tie in the two-worker pair loop | No value label; first enumeration only imitates the resident | N4 Phase A must first measure exact tie/boundary coverage | **N4 dependency** |
| Rerank unequal-score compatible pairs | Terminal counterfactual pair value | N4 Phase A, then a separately authorized Phase B | **N4 dependency** |
| Single-worker opening target ranker | Resident imitation is observable; terminal prefix value is not yet open | E1 is narrowed to an N4-prefix oracle; D18/L1 cover primitive learning boundaries | **dependency / overlap** |
| Collision priority or detour tie | Causal D171/D176 panels | D176 reached 2.88% long-run incidence and zero de novo oscillation, but only +0.045 margin, CI [−0.024,+0.114] | **closed** |
| Orchard mother tie | Exact E4 causal tied-map panel | Reversal loses −8.55 conditional and −0.0855 census-weighted margin | **closed** |
| Alternate home-door/path tie | E2 immediate/joint route audit; only future-conditioned residual | 4,855/4,855 immediate checks and 64/64 joint assignments are optimal; remaining ceiling is 0.335 turn/side-game | **closed micro-family / no label** |
| Broad primitive/concrete-target score replacement | Imitation or offline counterfactual terminal labels | D18, D41a, D79-D84, D97-D158, D172; L1 and L3 are separately scoped | **duplicate or scope expansion** |
| Greedy ranking for three or more workers | None in live resident | unreachable under the hard two-worker cap | **inactive** |

The negative priors matter. D18 passed 0/40 primitive-residual recipes. D41a's learned
scorer plateaued at 84.386-84.960% while an exact tuple decoder reproduced all
85,047/85,047 held decisions. D79's 32 random concrete-job scorers all became global
controllers; D80-D84 narrowed to a useful semantic action set but could not qualify a
snapshot selector or live rollout. D172 supplied dense, exact, zero-noise option labels
and still admitted 0/4 fitted selectors. These results do not prove that N4's exact
pair residual is valueless; they prohibit relabeling a broad scorer as a narrow tie-break.

## N4 gate

N4 Phase A is owned by `chatgpt_1` and freezes the exact 2,048-game A2-0b matrix. It must
export the live pair, every compatible alternative, score gaps, boundary semantics,
reconstruction status, and latency, without an oracle or ranker. At peer head `99cf140`
the full census remains blocked because the test anchor counts all three probe accesses
rather than the single publication. An L2 implementation now would race the active write
owner and prejudge whether the surface is frequent, distinct, or reconstructable.

## Disposition

Mark L2 **dependency-gated on N4**. After accepted N4 Phase A:

- close L2 with N4 if the surface is sparse, non-distinct, non-exact, or too slow;
- if Phase A clears, make an explicit Phase-B value decision under N4; and
- only if a separately accepted Phase B demonstrates material terminal value may a new
  L2 residual-ranker protocol be written.

No source, instrumentation, candidate export, model, fit, game, map, candidate,
submission, or Arena action was created.
