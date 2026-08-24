# Anti-benching causal split: option-only replant design

- Task: `20260824-anti-benching-causal-split-design`
- Scope: read-only source and evidence analysis
- Conclusion: **`ISOLATABLE`**
- Prior result retained: **`RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`**

## Decision

The replant `PICK` option can be specified independently of the failed candidate's two additional
mechanisms: persistent commitment and duplicated bank candidates. The reason is structural, not
experimental:

- `main_candidates` forms the replant candidates before its lossy idle fallback;
- `remember_selected_regeneration` creates persistent memory only after joint selection;
- `commands` routes remembered units on later turns; and
- `MoisanBot::select` receives candidate vectors but neither creates nor reads the commitment map.

An option-only design can therefore construct the exact parent candidate vector first, append only
the specifically discarded replant candidates, pass the vectors through the unchanged selector,
and exclude a selected added candidate from the later memory insertion. Delta-B disappears because
the design never returns the failed candidate's whole accumulated `out` vector.

This is an **isolatable design**, not a useful cure yet. No existing artifact shows that the
isolated option restores durable progress, improves score, or remains safe on a closed-loop panel.

## Evidence pins and vocabulary

- **[ROUTE]** `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:`
  `claude_1/picker2/phase3-generator-route-2026-08-20.md`.
- **[DESIGN-R2]** the same commit,
  `claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`.
- **[BASE]** `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:`
  `claude_1/picker2/candidate-door1-p1p2.rs`.
- **[R2-SOURCE]** the same commit,
  `claude_1/picker3/candidate-door1-p3b.rs`.
- **[PANEL]** the same commit, `claude_1/pipeline/fuzz_panel.py`.
- **[BUILD-REVIEW]** `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:`
  `codex_1/reviews/pair-selector-phase3b-build-review-2026-08-23.md`.
- **[REACH-REVIEW]** the same commit,
  `codex_1/reviews/pair-selector-phase3b-reach-review-2026-08-23.md`.
- **[G-D]** the same commit,
  `codex_1/picker3/results/gd-door1-panel-2026-08-23.md` and
  `codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json`.
- **[UNIFIED]** `agent/local_codex_1@16b6e4ada72ab1381833162ed98e97ba930cd9b4:`
  `local_codex_1/reviews/pair-selector-gd-ge-unified-review-2026-08-23.md`.
- **[REREVIEW]** `agent/chatgpt_1@a3d2b02a605800d147cc78b9995a7a3525b9e315:`
  `chatgpt_1/reviews/anti-benching-result-strategy-rereview-2026-08-23.md`.

Here **Delta-A** means only the replant `PICK` candidates formed by the exact safe-regeneration
block and discarded by the parent idle fallback. **Delta-B** means the duplicated bank candidates
created when r2 returns the whole prior `out` vector and then appends bank candidates again.

All pins resolve from their named canonical branches. The sacred resident remained SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` during this review.

## Causal ledger

| mechanism | observed | deduced | hypothesized | missing evidence |
|---|---|---|---|---|
| Delta-A: preserved replant option | [ROUTE] measured two score-7500/7499 `PICK`s discarded on 101 consecutive OSC-013 turns. [BUILD-REVIEW] reproduced 201 formed and 143 selected ticks over 19/34 Door-1 fixture games. [REACH-REVIEW] reproduced 339 restored-and-selected ticks in 34 episodes over 14/49 parity-verified real games. | The option has non-zero natural formation and can survive joint selection. R2's five turn-100 P3 divergences prove it changes commands on the locked panel. | An isolated option may create useful banking or employment at acceptable cost. | The progress gate was unrun; 111/160 real games refused closed; durable progress, full-corpus reach, score, and causal value are unknown. |
| Persistent regeneration commitment | [BASE] and [R2-SOURCE], `remember_selected_regeneration`, insert every selected `PICK` when `persistent_regeneration` is true; `commands` routes remembered units to `endgame_candidates`; `reconcile_regeneration_commitments` later clears them. The tuned constructor enables persistent regeneration. | Every newly selected Delta-A command in r2 can create cross-turn memory; the small fallback diff therefore has a larger behavioral surface. This path is separate from candidate formation and selection, so it can be excluded for Delta-A while leaving parent-existing commitments unchanged. | Persistent commitment caused most post-turn-100 regressions. | No controlled no-commitment arm or per-game commitment timeline exists. [REREVIEW] correctly leaves this attribution unproved. |
| Delta-B: duplicate bank candidates | [DESIGN-R2] derives duplicated, element-identical bank candidates for carried, shack-adjacent fallback states. [BUILD-REVIEW] reports zero natural Delta-B states in the fixture library and therefore `UNMEASURED`. | Delta-B is mutually exclusive with Delta-A within one unit state (`carried>0` versus `carried==0`), but trajectory changes after Delta-A could reach it later. Returning the parent fallback plus Delta-A only removes Delta-B structurally. | Exact duplicates are selector-inert, or alternatively affect tie/order behavior in some reached state. | No natural-state census or same-state selection fork exists for the 240-game run. R2 cannot exclude Delta-B as a contributor. |
| Joint pair selection | [BASE], `MoisanBot::select`, applies target compatibility, same-stock sufficiency, self-blocking, score, and fewer-WAIT tie-breaking across both units. [BUILD-REVIEW] and [REACH-REVIEW] show Delta-A is sometimes selected. | Adding an option can change either unit's chosen command without changing selector code; partner feasibility is part of the causal chain. | Some added options are useful only with particular partner commands; others displace a better pair. | No per-changed-game candidate vectors, pair scores, rejected alternatives, or same-state parent/option selection table was published. |
| P3: orchard inertness | [PANEL], `eval_p3`, requires whole command-stream equality on orchard-eligible initial layouts. [G-D] records five direct first divergences at turn 100; [UNIFIED] reproduces the five-game count. | One divergence blocks r2 under the frozen gate. An option-only design must form no Delta-A candidates on an orchard-eligible map, rather than trying to excuse their selection. | Excluding orchard-eligible layouts may preserve enough non-orchard reach to justify a later test. | Reach after the orchard exclusion is unmeasured. The exclusion's runtime mirror has not been implemented or parity-tested. |
| P4: long-stall classification | [PANEL], `work_remaining`, `live_horizon`, and `eval_p4`, scan backward from the final terminal suffix and trim stall windows to `horizon-1`. [G-D] records 73 new labels. In `m035` seat 0 the candidate-only P4 window is turns 33–99 while commands first diverge at turn 100. | The 73 count is valid under the frozen gate, but it is not a causal inventory of 73 stalls during the named windows. At least `m035` is classified through later trajectory information. | A subset of the 73 cases may still be genuine post-divergence liveness damage. | Per-game first-divergence, commitment, Delta-B, pair-selection, progress, and window timelines are missing. A separate semantic decision is needed for reactivation policies. |

Two older constraints reinforce the separation. `docs/CONSTRAINTS.md` records fresh-harvest
regeneration commitment at −51.161 active margin with zero own-crop harvests, while sticky banking
is only an incident correction, not a broad value claim. Neither result directly prices this
bank-inventory option; both forbid assuming that persistent routing is valuable merely because the
first action is locally coherent.

## Option-only design contract

This is the exact contract for a possible future implementation. It is not code authorization.

### 1. Baseline and scope flag

The parent is exact [BASE]. On the first view of a game, compute and freeze a boolean matching
[PANEL] `orchard_eligible_view` exactly: at least two walkable own doors; at least one live initial
natural plant; every such plant reachable from the own doors; median home-door distance at least
8; and a free water-adjacent own door whose enemy-door distance is at least 11. Call it
`orchard_eligible_initial`. This flag may only suppress Delta-A; it may not affect any parent path.

Introduce a dedicated `delta_a_option_only` design flag. Do not use persistent commitment as the
meaning of this flag. The parent feature flags and all parent behavior remain unchanged.

### 2. Exact same-state preconditions

Delta-A may be formed for a unit only when all of these hold in the same decision state:

1. `commands` takes the same ordinary `main_candidates` routing branch as [BASE]—not early,
   endgame, or committed-regeneration routing;
2. `delta_a_option_only` is true and `orchard_eligible_initial` is false;
3. `idle_regeneration` is true and `yamo_chop_candidates(...)` is empty;
4. `carried == 0` and `unit.free_capacity() > 0`;
5. `view.turn >= 100`, `view.plants.len() <= 2`, and at least two own units exist;
6. the unit is adjacent to the own shack and no plant occupies its cell; and
7. `inventory_fruits(view)` is non-empty.

For each fruit in the unchanged `inventory_fruits` order, form the existing candidate identity:
`PICK <unit> <kind>`, score `7500.0 - priority`, target `Cell(unit.cell)`. Remove any candidate that
is already element-identical in the parent vector; a duplicate is not Delta-A.

### 3. The only allowed candidate-list difference

Let `B[u]` be the exact ordered candidate vector produced by [BASE] for unit `u` on the recorded
same-state input. Let `D[u]` be the ordered Delta-A vector above.

```text
if the exact preconditions hold:  C[u] = B[u] followed by D[u]
otherwise:                         C[u] = B[u]
```

The full-vector contract is:

- every element and the order of `B[u]` remain byte/bit exact in `C[u]`;
- the ordered multiset addition is exactly `D[u]` and nothing else;
- no element is removed, rescored, retargeted, reordered, or duplicated;
- no bank candidate is added by the option path; and
- all sibling-unit vectors remain exact `B` unless that sibling independently meets the same
  Delta-A preconditions.

This deliberately does **not** return r2's accumulated `out`. It starts from the parent's returned
fallback and appends only Delta-A, so Delta-B is absent by construction.

### 4. Selector and one-turn provenance

`MoisanBot::select`, `compatible`, `stock_compatible`, `self_blocked`, wait counting, move-conflict
resolution, scores, inventory input, unit ordering, and sibling vectors remain source-identical to
[BASE]. The option may change the result only because `D[u]` is present.

Keep an ephemeral, current-turn set of `(unit id, complete Candidate identity)` for `D`. It is
diagnostic provenance and an exclusion input after selection; it must not enter selector scoring,
compatibility, ordering, or tie-breaking and must be cleared before the next turn.

### 5. Explicit absence of Delta-A commitment

If the selected candidate belongs to `D`, `remember_selected_regeneration` must not create, renew,
or change a `regeneration_commitments` entry for that selection. Existing entries and selected
`PICK`s that were already present in `B` retain exact parent handling. No new field may remember a
Delta-A target, fruit, phase, or owner across turns.

Thus later behavior may differ because the referee resolved the selected `PICK` and the world now
contains different cargo; it may not differ because the candidate added a hidden commitment.

### 6. Orchard-inert scope

When `orchard_eligible_initial` is true, `D[u]` is empty for every unit and turn. The complete
candidate vectors, selected commands, and command stream must remain byte-identical to [BASE]. Any
orchard-eligible divergence is a design failure, not a named cost.

## Direct P3 failures and the P4 interpretation warning

These are observations from [G-D], not predictions for the option-only design.

| game | first divergence | r2 command | exact-base command | frozen result |
|---|---:|---|---|---|
| `m035` seat 0 | 100 | `WAIT;PICK 2 BANANA` | `WAIT;WAIT` | P3 and P4 |
| `m065` seat 0 | 100 | `PICK 0 BANANA;PICK 2 PLUM` | `WAIT;WAIT` | P3 and P4 |
| `m074` seat 0 | 100 | `PICK 0 BANANA;WAIT` | `WAIT;WAIT` | P3 |
| `m104` seat 0 | 100 | `WAIT;PICK 2 APPLE` | `WAIT;WAIT` | P3 |
| `m114` seat 0 | 100 | `PICK 0 BANANA;PICK 2 PLUM` | `WAIT;WAIT` | P3 and P4 |

The smallest P4 counterexample is `m035` seat 0. Its candidate-only stall window is turns 33–99,
`live_end=99`, `terminal_from=106`; the exact streams are identical through turn 99 and first
diverge at turn 100. A deterministic referee cannot attribute the world or no-progress behavior in
33–99 to a command that did not yet differ. The label is still valid under [PANEL]'s frozen
trajectory-level definition: the later reactivation moves the start of the final terminal suffix.
It must not be narrated as a candidate-caused stall within 33–99.

## Future measurement matrix — all rows unexecuted

| status | open claim | smallest future measurement | control arm | population | required output | earliest falsifier |
|---|---|---|---|---|---|---|
| **UNEXECUTED** | The source implements only the contracted list delta. | Same-state generator fork plus source-diff allowlist. Compare ordered full Candidate identities and all scalar inputs. | Exact [BASE]. | Every naturally reached ordinary-main state from both arms, including post-effect states. | Per-state `B`, `D`, `C`; exact cross-sum assertions; source hashes. | Any delta outside `D`, any parent reordering/removal, any duplicate, or any changed sibling vector without its own eligible Delta-A. |
| **UNEXECUTED** | Delta-A creates no persistent commitment. | Before/after snapshot of every persistent field around selection and the next turn; poison control that deliberately remembers `D`. | Exact [BASE] plus a deliberately committing poison arm. | Every state where `D` is selected, plus matched baseline `PICK` selections. | Selected provenance and field-level memory diff. | A selected `D` creates/renews any persistent entry, or a baseline `PICK` loses parent behavior. |
| **UNEXECUTED** | The unchanged joint selector sometimes selects Delta-A legally. | Replay `MoisanBot::select` on recorded same-state vectors `B` and `C`, then unchanged move-conflict resolution. | `B` on the identical state. | All naturally reached states with non-empty `D`; no synthetic states for reach claims. | Candidate vectors, scores, compatibility decisions, selected pair, and resolved commands. | `D` is never selected; selector source/hash changes; or a chosen pair violates target/stock/self-blocking checks. |
| **UNEXECUTED** | Orchard-inert scope is exact. | Initial-map predicate parity plus full command-stream comparison. | Exact [BASE]. | Every orchard-eligible locked-panel game and predicate boundary fixtures. | Predicate agreement and byte-identical complete streams. | One predicate disagreement or one command byte differs on an orchard-eligible game. |
| **UNEXECUTED** | The isolated option restores real progress. | The existing two-clause progress grade, adapted only to consume the new provenance, after the structural checks above pass. | Exact [BASE]. | Matched benched-and-work-available population; baskets only as exhibits. | Healed-minus-new unit-turns and episodes, with actual banking or employment, every changed game named. | No positive population improvement; a selected `D` merely silences a detector; or any required fixture lacks progress. |
| **UNEXECUTED** | Option-only closed-loop costs are acceptable. | Full locked named-cost panel only after useful progress is demonstrated. | Exact [BASE], rerun or provenance-equivalent under a newly frozen protocol. | All 240 locked games at the protocol horizon. | Full per-game changes, P3/P4/horizon, blocking, execution and identity checks. | Any P3 divergence, new P4/horizon event under the frozen semantics, worse blocking total, or unnamed changed game. |
| **UNEXECUTED** | Which P4 labels are temporal reclassification versus post-divergence harm? | Separate read-only tool: join first command divergence, progress windows, `work_remaining`, `live_horizon`, and post-divergence events per game. | Exact base and the already stopped r2 packet; no new bot arm. | The 73 existing new-P4 rows, starting with `m035`, `m065`, and `m114`. | Partition into pre-divergence-only, crossing, and post-divergence windows; no cure verdict. | The tool cannot reproduce the frozen labels exactly, or reports a pre-divergence interval as command-caused. |
| **UNEXECUTED** | Local progress translates to score. | Only after qualification, a separately authorized paired score design with arm order balanced. | Qualified option-only candidate versus exact champion/base named by the future protocol. | Future frozen local/Arena population. | Paired score and named costs with identity checks. | Candidate is not locally qualified, protocol lacks authorization, or identities/order are ambiguous. |

## Stage order and stop conditions

1. **Static design review first.** Review this contract and the exact future source diff. Stop if
   the source cannot make `C = B + D` or exclude `D` from commitment without changing the selector.
2. **Same-state structural gates second.** Prove the candidate-list delta, no-commitment rule,
   selector identity, and orchard predicate. Stop on the first violation; do not run a panel to
   average it away.
3. **Selection and progress third.** Measure natural same-state selection, then actual banking or
   employment. If the isolated option has no useful progress, retire the replant cure family and
   redirect to explicit capability-aware work/resource ownership.
4. **Bounded transaction only after option value.** If useful progress exists but completion needs
   memory, design a new bounded transaction with explicit success, timeout, cancellation, and
   ownership. Do not restore the generic commitment implicitly.
5. **Named-cost panel and score last.** Each needs a new frozen protocol and its recorded authority.

P4 semantics are a separate evidence-tool charter. It may clarify future causal language and gate
design, but it cannot waive r2's five P3 failures, rewrite the 35-to-115 result, or retroactively
qualify the stopped candidate.

## Final limits

Conclusion: **`ISOLATABLE`**. The option can be separated structurally because formation,
selection, and persistent memory occupy distinct functions, and Delta-B can be avoided by adding
only the explicit Delta-A vector to the exact parent fallback.

The scientific verdict remains **`RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`**. R2 remains rejected.
Progress, full-corpus value, score, qualification, and Arena readiness remain unmeasured. No source,
panel, detector, grader, protocol, simulation, replay corpus, TestSession, submission, or Arena
state was changed or run for this memo.
