# D89a opponent-score leak — repairability analysis

Author: `claude_1`. Date: 2026-08-07. Type: **ANALYSIS ONLY** (owner-directed scoping).
Question: *is D89a's opponent-score leak repairable without destroying its production gain?*

**VERDICT: `NOT_REPAIRABLE`** — for the *exact* leak against the *exact* `<= +1` gate, by any
mechanism the corpus contains or that this analysis can construct. Two sub-branches are
`UNRESOLVED` and are named precisely in §8; neither is a route to a candidate on any near horizon.

---

## 0. Boundary compliance and status

Owner boundary: analysis only. This document is the **only** file this task created or changed.

| forbidden action | performed? |
|---|---|
| implementation / candidate / builder / detector / gate edit | NO |
| host run, `cargo` build, panel execution, TestSession | NO |
| value protocol, submission, Arena action, resident replacement | NO |
| CI change anywhere | NO |
| modification of any existing repo file | NO — one new file only |

Everything below is `git show` + `sha256sum` + arithmetic in `python3` over already-committed
bytes. No simulator was run. The working tree is otherwise untouched
(`git status --porcelain` clean apart from this file).

## 0.1 Conflict-of-interest declaration (owner-required)

`claude_1` owns **Route A** (the `banana-restoration-r2` wrapper line). A `NOT_REPAIRABLE`
verdict on D89a **protects claude_1's own line** by removing its only live competitor for the
programme's banana effort. That is a direct interest in the conclusion I have reached, and it is
the failure mode this document must be read against.

Mitigations actually applied, and where the evidence cuts against Route A:

1. §3.4 constructs an **oracle** (perfect-hindsight) repair and reports that it **succeeds** —
   a 70/256 subset of D89a's own panel passes every failed gate simultaneously
   (opponent `+0.829`, margin `+129.957`, worst `-58`, p10 `-20`, all 8 families, both seats,
   15/16 maps). I could have omitted this. It is the single strongest argument *for*
   repairability and it is stated in full.
2. §3.4 also refutes, from the same data, the corpus's own stated reason for closing the
   selector branch. `CONSTRAINTS.md:103-104` says factory selectors "fail map transfer
   (selection on 5/16 maps)". The oracle-optimal core is spread over **15/16 maps**, with a
   16-map-cluster 95% CI of **[+14.248, +56.822]** — lower bound positive. D91's map-cluster
   failure was a property of *its predicate grammar*, not an intrinsic property of the target.
   That materially weakens the corpus's closure argument and I say so.
3. §4.9 surfaces and quantifies the **one counterexample in the entire repository** to my central
   exchange-rate argument — the `b100_e6` denial rule, which removes `5.342` opponent points for
   `0.481` of ours (ratio `0.090`, sub-unity, and it passed a frozen discovery block *and* an
   unchanged replication). That is the single fact most capable of overturning my verdict. I
   found it, state it first, and then explain in measured terms why it does not rescue D89a.
4. §6 concludes on the numbers that **Route A is in a worse position than D89a on four of five
   cost dimensions**, that Route A has produced zero valid candidates in ~5 days and six gate
   rounds, that its own feasibility scoping rates its critical prerequisite
   `UNRESOLVED, leaning INFEASIBLE`, and that **its remaining path is strictly longer than
   D89a's**. §6.4 states the wind-down case against my own line explicitly.
5. Conversely, §6.2b records the one fact that cuts *for* my line and *against* D89a — the D89a
   architecture has actually been Arena-tested and placed at **rank 127/131** — and labels it as
   such rather than leading with it.
6. The verdict is `NOT_REPAIRABLE` **for the leak**, and §6/§9 make clear this does **not**
   imply Route A should proceed. My honest recommendation (§9) is that *neither* line is the
   next move, which is not the answer that favours me either.

`chatgpt_1` reviews this from the opposite interest; its whole-programme disposition called this
lineage "fully superseded" (§5.3 quotes it and records that the coordinator overturned it).

---

## 1. Provenance — inputs and SHA-256

All D89a artifacts are on `origin/main`, `origin/agent/local_codex_1`, `origin/agent/chatgpt_1`
and every agent branch; the five `d89a-*` files and the analyzer are byte-identical across them
(verified below). The earlier claim that this lineage exists "only on `origin/agent/local_codex_1`"
was **false** and was corrected by the coordinator; this document uses `origin/main` as the
canonical source.

Fetch (run once):

```bash
cd /home/tarstars/prj/troll_farm-claude_1
git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*'
```

Hash reproduction:

```bash
for f in d89a-banana-seed-factory-result-2026-07-21.md \
         d89a-banana-seed-factory-blueprint-2026-07-21.md \
         d89a-banana-seed-factory-protocol-2026-07-21.md \
         d89a-banana-seed-factory-freeze-2026-07-21.json \
         d89a-banana-seed-factory-discovery-result-2026-07-21.json; do
  printf '%-62s %s\n' "$f" \
    "$(git show origin/main:data/analysis/live-agent-6553250/$f | sha256sum | cut -d' ' -f1)"
done
git show origin/main:cgauto/analyze_d89a_banana_seed_factory.py | sha256sum
```

| input | ref | SHA-256 |
|---|---|---|
| `d89a-…-result-2026-07-21.md` | `origin/main` | `1762ccb16e89bf1a118088759bdfb7c3672ee6b252872eb8a5f4a8e7bc8d8b52` |
| `d89a-…-blueprint-2026-07-21.md` | `origin/main` | `c3956d3bf33e51fb6a8a9b398a69bcdeea74b66c952eff1ced5144e200fbab04` |
| `d89a-…-protocol-2026-07-21.md` | `origin/main` | `65bb19bf438848c6f10cfb974a5687f4277eb4527fc63e8b0ef813714486af06` |
| `d89a-…-freeze-2026-07-21.json` | `origin/main` | `c8ecfb77538844c40c4f73282af4f46401f67d396dc9fecc22f2d90b011ddde1` |
| `d89a-…-discovery-result-2026-07-21.json` | `origin/main` | `d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a` |
| `cgauto/analyze_d89a_banana_seed_factory.py` | `origin/main` | `6a4bb8971310d74777ef1491a73f95e40d72e89bd0355eddac6983ca1c6c75c8` |
| `d90-lineage-and-attack-diagnosis-2026-07-21.md` | `origin/agent/chatgpt_1` | `4cec5874f8da5347ac478ac9a42ad6dcc9616f4b08286b46c6107b7e1fd8cfcc` |
| `d91-factory-activation-selector-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `c52b94c9025f9adcf424e4b38c1dc404ff89ef8281fb064d93acd85e9605750d` |
| `d91c-factory-activation-selector-protocol-2026-07-21.md` | `origin/agent/chatgpt_1` | `36ee7cd9b15306cb80f5451236e6c95fbc979aae732814cab3fe037ac6019449` |
| `d92-factory-dual-value-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `0e5084a05e65002b95d469d0e6e2da1c82d43549d0a7d9051646bf2eb6812f6c` |
| `d93a-…-stock-flow-audit-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `b0a6c0c3351bd7502a0eaa879b84be60eb8993eb491d7dae632456606e83f2d8` |
| `d94a-…-materialization-audit-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `9f418e0d872f1e875a2f6c3c9cf0b307a254b524e6fd8a5feaecaea4be94fdb6` |
| `d94b-c-…-worker-three-bridge-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `d30237a63c454157c43f4b52ee9be8bd2637bcd0575b6263d44c01c384dd57f9` |
| `d103a-…-opponent-growth-phase-decomposition-result-2026-07-22.md` | `origin/agent/chatgpt_1` | `ac78d0a92cf0407ee9889c5c7d2c4a1316d51b35cc6ee77783e68fa4264570ab` |
| `d175a-bounded-early-planting-result-2026-07-29.md` | `origin/agent/chatgpt_1` | `a7ee751f4d9cc62ac962216c0835b2046b2968cef20d7349a6da0e998efd6dd6` |
| `docs/CONSTRAINTS.md` | `origin/agent/chatgpt_1` | `81e578e18443af619260f8f0f21490761207f24c63f8d6cf8fb30f2f4e0b986b` |
| `docs/BACKLOG.md` | `origin/agent/chatgpt_1` | `14b2475be7e294b715b453798d6ea92da3483585690a805823bd310e463fa49e` |
| `rust/src/game/engine.rs` | `origin/agent/chatgpt_1` | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |
| `opponent-crop-suppression-2026-07-18.md` | `origin/agent/chatgpt_1` | `4c8bc864ef6cb4994f30cad17f25ce497ebfd4694b26bed972ab7192d0cd3a27` |
| `banana-ring-b100-smoke-20260802T-r5.json` | `origin/main` | `3b8e596d837b1fd1549975ea84a13d8f8e36964d3365610e3ed0d955e7e35818` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | worktree @ `390158a4` | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `docs/HARDENING-PLAN-CONSOLIDATED-2026-08-07.md` | `origin/main` | `6dfa6e42dcaace878b6bd798f734d039827454531b041ba985efd0ba1cd5085f` |

The freeze manifest's recorded `analyzer` hash
(`d89a-…-freeze-2026-07-21.json`, key `hashes.analyzer`) is
`6a4bb8971310d74777ef1491a73f95e40d72e89bd0355eddac6983ca1c6c75c8` — **equal** to the analyzer
byte hash above. The `blueprint` and `protocol` hashes in the same manifest likewise match. The
result document's own claimed analyzed-result hash
(`d89a-…-result-2026-07-21.md` line 13) is `d2bab93a…7741a` — **equal** to the discovery JSON's
byte hash. `[MEASURED]` The artifact set is internally hash-consistent and unaltered since freeze.

**Scoring rule** `[MEASURED]` — `rust/src/game/engine.rs:15` and `:191-195`:

```rust
pub const WOOD_POINTS: i32 = 4;
/// Recompute scores from inventories: sum of fruits (0..4) + WOOD_POINTS * wood.
game.scores[p] = inv[0] + inv[1] + inv[2] + inv[3] + WOOD_POINTS * inv[WOOD];
```

`score = PLUM + LEMON + APPLE + BANANA + 4 x WOOD`. One wood = 4 points, one fruit = 1 point.
Independently corroborated at `cgauto/suppression_efficiency_diagnostic.py:144`
(`WOOD_POINTS = 4  # score.rs: score = sum(fruit) + 4*wood; matches sim/engine.py`).

Labelling convention used throughout: `[MEASURED]` = recomputed by me from committed bytes, or
quoted verbatim from a committed measurement with its hash; `[INFERRED]` = my reasoning over
measurements; `[ASSUMED]` = a modelling assumption I could not test.

---

## 2. Question 1 — re-derivation of the `+82.863` decomposition

### 2.1 What I re-derived successfully `[MEASURED]`

Everything that lives in the committed discovery JSON. Reproduction (`compute.py`, embedded in
Appendix A):

```bash
git show origin/main:data/analysis/live-agent-6553250/\
d89a-banana-seed-factory-discovery-result-2026-07-21.json > /tmp/d89a.json
sha256sum /tmp/d89a.json   # d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a
python3 compute.py         # Appendix A
```

| quantity | doc value | my recomputation from the 256 committed pairs |
|---|---:|---:|
| mean margin delta | `+79.441` | `+79.441406` |
| mean own-score delta | `+162.305` | `+162.304688` |
| **mean opponent-score delta** | `+82.863` | **`+82.863281`** |
| mean terminal-wood delta | `+40.590` | `+40.589844` |
| mean successful-plants delta | `+35.688` | `+35.687500` |
| mean own-crop harvested-fruit delta | `+36.176` | `+36.175781` |
| resident mean opponent score | — | `155.9648` |
| candidate mean opponent score | — | `238.8281` |
| total opponent-score mass added over 256 tasks | — | **`21,213` points** |
| leak ratio (opponent gain / own gain) | — | **`0.510542`** |

All headline figures reproduce exactly. The four failed gates reproduce from
`value_gates` in the same JSON: `worst_family_at_least_minus_5: false`,
`active_p10_at_least_minus_20: false`, `active_worst_at_least_minus_60: false`,
`active_opponent_score_delta_at_most_1: false`.

Per-opponent-family structure, recomputed `[MEASURED]` (n = 32 each; all 256 tasks are active):

| family | Δmargin | Δown | Δopponent | leak ratio | worst | p10 |
|---|---:|---:|---:|---:|---:|---:|
| compact_gold | `+60.719` | `+170.219` | `+109.500` | 0.643 | `-114` | `-76` |
| **gold_adaptive** | **`-6.938`** | `+201.844` | **`+208.781`** | **1.034** | **`-235`** | `-151` |
| gold_elite | `+60.719` | `+170.219` | `+109.500` | 0.643 | `-114` | `-76` |
| mybot | `+55.000` | `+84.562` | `+29.562` | 0.350 | `-103` | `-30` |
| printer_bot | `+152.812` | `+203.094` | `+50.281` | 0.248 | `-50` | `+8` |
| sched_bot | `+83.250` | `+108.438` | `+25.188` | 0.232 | `-112` | `-43` |
| script_boss | `+104.125` | `+173.531` | `+69.406` | 0.400 | `-99` | `-76` |
| silver_boss | `+125.844` | `+186.531` | `+60.688` | 0.325 | `-30` | `+6` |

The leak is **not uniform**: it ranges 0.232 (sched_bot) to 1.034 (gold_adaptive). Against
`gold_adaptive` the opponent gains *more* than we do. `gold_elite` and `compact_gold` are
byte-identical twins on this panel (identical figures in every column) — noted so the "three Gold
families are worst" observation is understood as **two** independent behaviours, not three.

### 2.2 What I could **not** re-derive — `UNRESOLVED`

**The theft-vs-opponent-own split (`+12.453` / `+76.508`) is NOT re-derivable from any committed
artifact.** `[MEASURED — absence verified]`

The analyzer (`analyze_d89a_banana_seed_factory.py`) reads a TSV panel and emits only aggregated
own-side quantities. Its `pair_rows()` (lines 79-194) writes exactly these per-pair fields:
`resident/candidate/delta` x `{score, opponent_score, margin, wood, owned_chop_wood, workers,
plants, own_crop_harvest, action_hash, state_hash}`. `own_crop_harvest` is
`sum(row["own_fruit_from_ours_{kind}"])` (line 68-69) and `owned_chop_wood` is
`sum(row["own_from_{natural,ours,opponent,unknown}"])` (line 72-76). **No opponent-side
provenance quantity is carried into the JSON at all.**

The columns that would be needed exist in the harness row schema —
`cgauto/ownership_aware_complete_economy.py:35-38` declares
`opponent_from_{natural,ours,opponent,unknown}` (opponent's chop wood by tree origin), and
`opponent_fruit_from_{natural,ours,opponent}_{species}` columns are referenced in the harness
test fixtures (`tests/test_species_separated_renewable_supply.py:87,89`;
`tests/test_reproductive_seed_source_decomposition.py:37`). But the D89a panel TSVs themselves
are not committed anywhere:

```bash
for b in $(git branch -r | grep -v HEAD | sed 's/^ *//'); do
  git ls-tree -r --name-only $b 2>/dev/null | grep -iE '\.tsv$'; done | sort -u
# 56 distinct TSV paths across all branches; NONE is a d89a-* panel.
```

The result document itself names no TSV artifact (unlike D92, D93a, D94b, D103a, which all list
their `.tsv` filenames and hashes). `[INFERRED]` The D89a panel rows were consumed in-session and
never committed.

**Verdict on sub-question 1: `UNRESOLVED` for the split itself.** Exactly what is missing:
a D89a panel TSV over seeds `9,914,032..9,914,047` x 2 seats x 8 opponents x
`{resident, banana_seed_factory}` (512 rows) carrying the columns
`opponent_from_{natural,ours,opponent,unknown}` and
`opponent_fruit_from_{natural,ours,opponent}_{plum,lemon,apple,banana}`. Nothing less will settle
it; a rerun would produce it, but a rerun is a host action and is outside this task's boundary.

### 2.3 What I *can* verify about the split — three independent consistency checks

`[MEASURED]` The reported figures are means over 256 tasks, so exact values must be integer
multiples of 1/256. All eight quoted figures snap cleanly:

| reported | exact `k/256` | float |
|---|---|---:|
| theft `+12.453` | `3188/256` | `12.4531250` |
| opponent-created `+76.508` | `19586/256` | `76.5078125` |
| its wood component `+16.461` | `4214/256` | `16.4609375` |
| its fruit component `+10.680` | `2734/256` | `10.6796875` |
| total `+82.863` | `21213/256` | `82.8632812` |
| our gain from owned crops `+316.254` | `80961/256` | `316.2539062` |
| our loss, natural+opponent sources `+117.508` | `30082/256` | `117.5078125` |
| mean own-score delta `+162.305` | `41550/256` | `162.3046875` |

**Check 1 — the score identity.** Under `score = fruit + 4 x wood`:
`4 x 16.4609375 + 10.6796875 = 76.5234375` against a reported `76.5078125`. Residual `0.015625`
= exactly `4/256`, i.e. one wood-point of accumulated rounding across the panel, 0.02% of the
term. `[INFERRED]` The parenthetical "(`+16.461` wood and `+10.680` fruit)" is a
**units** breakdown (wood units, fruit units) whose score-equivalent is the `+76.508` figure, and
the identity holds to within one part in 4,900. This confirms the *form* of the decomposition,
not its magnitude.

**Check 2 — the additive closure.** `12.453125 + 76.5078125 = 88.9609375`, against the
independently recomputed total `+82.8632812`. Residual **`-6.0976563`** (= `-1561/256`).
`[INFERRED]` This is a coherent third term: the opponent's take from **natural and
unknown-origin** sources *fell* by ~6.10 score-equivalent. The decomposition is therefore
arithmetically closed and not double-counted. A decomposition that did not close would have been
a red flag; this one does.

**Check 3 — the own side does *not* close, and this is a real discrepancy.** `[MEASURED]`
The document's own-side sentence gives `+316.254` from owned crops and `-117.508` from natural +
opponent-created sources; `316.254 - 117.508 = 198.746`, against the recomputed mean own-score
delta `+162.305`. Residual **`+36.441`**. `[INFERRED]` This is most likely a fourth own-side
channel (unknown-origin and/or bank/board fruit not attributed to any crop lineage) that the
sentence omits, and `+36.441` is suspiciously close to the measured mean own-crop harvested-fruit
delta `+36.176` — but I cannot close it without the rows, and I decline to assert it.
**Flag this as an unverified figure in the result document.**

**Net position on Question 1.** The `+82.863` total is `[MEASURED]` and reproduces exactly. The
`+12.453` / `+76.508` split is `[UNRESOLVED]` — internally consistent, dimensionally correct
under the engine's scoring rule, and additively closed to a plausible third term, but **not
independently re-derivable**. The document's own-side companion figures do **not** close, by
`+36.441`. Everything downstream in this analysis that depends on the split is labelled
accordingly.

---

## 3. Question 2 — the causal mechanism

Four candidate mechanisms were named in the brief. I test each against the committed data.

### 3.1 "We occupy fewer contested cells / release map control" — **FALSIFIED as stated**

`[MEASURED]` Mean `delta.owned_chop_wood` = **`+40.648`**. We chop **more** wood, not less:
only **24/256** tasks show any decrease; median `+41`, max `+94`. At the single worst cell
(map 9,914,047 / seat 0 / gold_adaptive) our chopped wood rises `54 -> 96` (`+42`) while the
opponent's score rises `83 -> 481` (`+398`).

The *volume* hypothesis is dead. We do not withdraw from the board.

### 3.2 "We stop denying/chopping *their* crops because our workers farm" — **the surviving mechanism, MEASURED in direction, INFERRED in magnitude**

`[MEASURED]` Total chop volume rises (+40.648) while the result document reports that our
acquisition **from natural and opponent-created sources falls by `117.508` score-equivalent**
(`d89a-…-result-2026-07-21.md:59`, hash `1762ccb1…`). Those two facts are only jointly consistent
if the chop *target mix* is redirected: we chop **our own banana descendants** instead of natural
trees and the opponent's crops.

`[INFERRED]` `117.508` score-equivalent, if predominantly wood at 4 pts/unit, is ~29.4 units of
felling pressure withdrawn from natural + rival stock. The rival crops we would otherwise have
felled survive to be reaped or chopped by their owner — which is exactly the `+76.508`
opponent-created term. Implied conversion ≈ 2.6 opponent points per unit of withdrawn denial
pressure. This is the mechanism: **redirected, not reduced, chop pressure**.

Supporting `[MEASURED]` but weak signals from the 256 pairs (Pearson r, `compute2.py`):

| predictor of `delta.opponent_score` | r |
|---|---:|
| `harvest_successes` (factory intensity) | `+0.311` |
| `renewable_plant_successes` | `+0.310` |
| `delta.own_crop_harvest` | `+0.294` |
| `delta.score` (our production) | `+0.263` |
| `delta.plants` | `+0.252` |
| **`trained_role_rewrites`** (forced extra chopping) | **`-0.238`** |
| `delta.owned_chop_wood` | `+0.204` |
| `shadow_divergence_turns` | `+0.193` |
| `tracked_live_crops` | `-0.019` |

The strongest single predictor of the opponent's gain is **how hard our factory runs**, and the
only meaningfully negative predictor is `trained_role_rewrites` — the count of turns on which the
blueprint **forced** the trained worker off a resident-chosen PICK/PLANT/HARVEST/MINE onto a
chop/bank candidate. More forced chopping, less opponent gain. `[INFERRED]` Consistent with §3.2;
all r are small (|r| <= 0.31), so this is corroboration, not proof.

### 3.3 "Pure time/attention reallocation" and "the opponent's policy reacts" — **PARTIALLY MEASURED, jointly with §3.2**

`[MEASURED]` The leak ratio is strongly family-structured (0.232 -> 1.034, §2.1) and the two
`gold_adaptive`/`compact_gold`-class behaviours carry it. `[INFERRED]` A leak driven purely by
our own withdrawn denial would be roughly family-invariant; a 4.5x spread across opponents means a
large part of the effect is the **opponent's policy responding to the board we create**. We plant
crops and grow fruit; adaptive opponents route onto that richer board.

`[MEASURED]` The nearest committed phase decomposition of an opponent-score leak in this corpus is
D103a (a *different* intervention, D40, on a different panel; hash `ac78d0a9…`): its `+65.943`
opponent excess splits pre-scale `+9.480` (14.38%), post-scale `+25.715` (39.00%),
terminal-duration tail `+30.748` (46.63%), and its key sentence is
"*The productive loop and opponent opportunity expand together, which is precisely why
independent producer and endgame rules are insufficient.*" `[INFERRED]` The same coupling
almost certainly applies to D89a, but D103a's own crop-flow term (`+3.150` opponent-created crops
per task) is small, unlike D89a's — so **the two leaks are not the same leak** and D103a's phase
split must not be transferred to D89a numerically. I do not transfer it.

**Not testable from committed artifacts:** `terminal_turn` is a TSV column the analyzer reads
(`PAIR_FIELDS`, line 26) but does **not** emit, so I cannot measure whether D89a lengthens games.
`shadow_divergence_turns` (r = `+0.193`) is a weak proxy only.

### 3.4 Mechanism summary

| mechanism | status |
|---|---|
| We reduce total board contact / release map control | **`FALSIFIED`** `[MEASURED]` — chop volume rises `+40.648` |
| We redirect chop pressure from rival/natural stock onto our own crops, so rival crops survive | **PRIMARY** — `[MEASURED]` in direction (volume up + rival-source acquisition down `117.508`), `[INFERRED]` in magnitude (depends on the `UNRESOLVED` §2.2 split) |
| The opponent's policy reacts to the richer board we create | **CONTRIBUTING** — `[INFERRED]` from a 4.5x family spread in the leak ratio; `[MEASURED]` that the spread exists |
| Direct theft of our crops | **MINOR** — `[UNRESOLVED]` magnitude; the reported `+12.453` is 15% of the total and cannot be re-derived |
| Time/attention reallocation away from denial | **CONFOUNDED with §3.2** — cannot be separated without per-turn traces |
| Game-duration extension | **`UNRESOLVED`** — `terminal_turn` not emitted by the analyzer |

**This matters for repair design**: the leak is *not* something we do to the opponent's crops. It
is the **absence** of something we used to do to them, plus their reaction to a board we enriched.
A repair must therefore either restore denial pressure without spending production, or produce
without enriching the shared board — and §4 shows the corpus has already tested both.

---

## 4. Question 3 — candidate repairs

Six repair classes. **Four have already been measured and failed.** The gates each targets, the
production cost, and the mechanism are given per repair. Gate references are to the frozen D89a
protocol (`65bb19bf…`), value gates 4, 5 and 8.

### 4.0 The arithmetic every repair must satisfy

`[MEASURED]` The four failed gates are:

| gate | required | observed |
|---|---|---|
| G4 worst opponent-family mean | `>= -5` | `-6.938` (gold_adaptive) |
| G5a active p10 margin delta | `>= -20` | `-72` |
| G5b active worst margin delta | `>= -60` | `-235` |
| G8 mean opponent-score delta | `<= +1` | `+82.863` |

`[MEASURED]` **G4, G5a and G5b are jointly and easily satisfiable; G8 is not.** Oracle
tail-abstention (drop the k worst-margin tasks, perfect hindsight):

| k dropped | active | p10 | worst | worst family | **mean Δopponent** | mean Δmargin |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 256 | `-72` | `-235` | `-6.938` | **`+82.863`** | `+79.441` |
| 16 | 240 | `-49` | `-94` | `+55.909` | **`+72.154`** | `+93.446` |
| **37** | **219** | `>= -20` | `>= -60` | `>= -5` | **`+65.868`** | `+109.192` |
| 64 | 192 | `+6` | `-15` | `+73.296` | **`+63.333`** | `+128.771` |
| 96 | 160 | `+55` | `+20` | `+121.923` | **`+58.044`** | `+154.262` |

`[MEASURED]` Dropping the 37 worst-margin tasks clears **all three tail/family gates at once**
and leaves 219/256 active — comfortably above the `>= 160` activation floor. It leaves G8 at
`+65.868`, **66x over its ceiling**. Dropping 96 tasks (37.5% of the panel) still leaves
`+58.044`.

**This is the central structural finding.** `[INFERRED]` The tail and the leak are largely
**orthogonal**: the opponent-score leak is present in the tasks we *win*, not concentrated in the
tasks we lose. Any repair aimed at the tail leaves G8 essentially untouched. G8 is the binding
constraint and it must be attacked directly.

`[MEASURED]` What G8 demands, stated as a ratio: with `Δown = +162.305`, `Δopp <= +1` means a leak
ratio `<= 0.00616`. D89a's is `0.5105`. The best ratio anywhere in the lineage is D91's
in-sample selected cohort at `0.337`. **G8 as written is a near-prohibition on production**,
and the lineage knew it: D91c (`36ee7cd9…`, lines 75-80) **replaced** the absolute `+1` ceiling
with a ratio gate (`selected opponent increase <= 40% of selected own increase`), explicitly
noting "*D89 itself fails this ratio (`82.863 / 162.305 = 0.511`)*". `[MEASURED]` So even under
the lineage's own relaxed successor gate, D89a fails — **and it independently fails G4, G5a and
G5b**. Gate relaxation is not an escape hatch.

### 4.1 Repair R1 — rate-limiting the factory (moderate, sustained planting)

**Targets:** G8 (and, indirectly, G5). **Mechanism:** produce less, so the board is enriched less
and less denial pressure is diverted. **Explicitly flagged as UNTESTED** in the corpus:
`CONSTRAINTS.md:265` — "*The middle ground — early, moderate, sustained planting — is untested.*"

`[ASSUMED]` Under proportional scaling (own and opponent gains both scale by a throttle factor
`k`), `compute3.py` gives:

- `k` such that `k x 82.863 <= 1`: **`k <= 0.01207`**, leaving `Δown = +1.959`, `Δmargin = +0.959`.
  Fails value gate 2 (`Δown >= +2`) **and** gate 2 (`Δmargin >= +4`).
- `k` such that `k x 79.441 >= 4`: **`k >= 0.05035`**, giving `Δopp = +4.172`. Fails G8.

**No `k` satisfies both. The feasible intervals are disjoint by a factor of 4.2.** For a rate
limit to work, our own-score return must be at least 4.2x more concave in the production rate
than the opponent's gain — i.e. we must capture `>=5%` of the full production gain while inducing
`<=1.2%` of the leak.

`[MEASURED]` The nearest evidence on the low-rate end of that curve runs the wrong way. D175a
(`a7ee751f…`, 2026-07-29, 4,087 activated tasks) moved median first-plant from turn 199 to 13 —
a small, bounded, early planting increment — and measured **`Δown = -5.41`, `Δopponent = +21.09`**,
overall `-26.44`, map-clustered 95% CI `[-28.96, -23.92]`, catastrophes 229 vs 130, all six value
gates failed, every opponent family negative. Its own words (`:145-147`): "*Own score fell under
the candidate while the opponent's rose — a strictly dominated outcome, worse in kind than the
leak the safety gate was built to bound.*"

`[INFERRED — with a caveat I must state]` D175a is **not** a clean test of a rate-limited D89a.
Its own-crop reap rate was `0.45%` (gate required `>= 5%`); it planted without a working reap
loop, whereas D89a reaps 10,729 times across 252/256 tasks. So D175a measures "plant more, reap
nothing", not "run the factory at 10%". The direction of evidence is strongly unfavourable but it
is **not decisive** for this repair.

**Status: `NOT_REPAIRABLE` under the proportional model `[ASSUMED]`; the required concavity is
`UNRESOLVED` and would need a throttled-D89a arm to settle.** Production cost if the proportional
model holds: everything — the margin gain collapses to `+0.96`.

### 4.2 Repair R2 — keep a denial/interference budget — **MEASURED, FAILED**

**Targets:** G8 directly, G4. **Mechanism:** restore the rival-loop pressure §3.2 says we
withdrew.

`[MEASURED]` This is **exactly** D92 (`0e5084a0…`), which composed the already-frozen ETA-6
dual-value opponent-crop priority onto the running D89 factory in two arms:

| arm | changed | Δmargin vs D89 | 95% CI | impr/tie/regr | p10 | worst |
|---|---:|---:|---|---:|---:|---:|
| broad (starter + trained) | 159/256 | `-6.371` | `[-12.337, -0.405]` | 69/104/83 | `-70` | `-157` |
| trained-only (starter untouched) | 90/256 | `-5.609` | `[-7.350, -3.869]` | 12/183/61 | `-28` | `-64` |

Two decisive facts:

1. `[MEASURED]` **Trained-only denial has essentially zero efficacy.** It produced **898**
   opponent-crop target selections against D89's incidental **166** — 732 extra denial actions —
   and the opponent's score moved by **`+0.188`**, i.e. *upward*. Our own score fell `5.422`.
   The lineage's own conclusion: "*the trained worker reaches many nominal rival crops but is too
   late or too low-leverage to alter the rival's score.*"
2. `[MEASURED]` **Broad denial works but costs more than it denies.** It suppressed `13.883`
   opponent score — including `31.160` score-equivalent of opponent-created production — while
   destroying `20.254` of our own. Exchange rate **1.459 own points lost per 1 opponent point
   removed**. Note the substitution: denying `31.160` of their production only netted `13.883`
   of their score; the opponent substitutes at ~55%.

`[MEASURED]` D92 also made gold_adaptive **worse**: family margin delta vs D89 `-19.281`, and vs
resident the trained-only arm's gold_adaptive family mean is `-26.219` against D89a's `-6.938`.
G4 moves in the wrong direction. Tail: trained-only vs resident is p10 `-76`, worst `-251`, both
worse than D89a's `-72` / `-235`.

`[INFERRED]` Extrapolating the broad arm linearly, removing `81.863` of leak would cost `119.5`
own score, leaving `Δown = +42.8` and `Δmargin = +41.8` — which would still clear the margin
gates. That extrapolation is a **6x extension** of a measured `13.883` effect, and every
measured tail/family indicator moved against it at 1x. I record it because it is the strongest
quantitative case *for* repairability and it should not be suppressed; I do not believe it, for
three reasons: (a) the trained-only arm shows denial efficacy collapsing to zero as denial volume
rises 5.4x; (b) the substitution ratio is ~55%, so the marginal cost rises, not falls;
(c) the tails degrade at 1x.

**Status: `NOT_REPAIRABLE` `[MEASURED]`.** Verdict quoted from D92: "*Reject D92 without
prospective testing. The exact dual-value composition is closed; do not retune its ETA,
multiplier, or target threshold on these maps.*"

#### 4.2.1 R2 was independently retried in August with the *best* denial rule in the corpus — and failed the same way

`[MEASURED]` There is exactly **one** denial controller in this repo that has ever been measured
to remove opponent score more cheaply than it cost us:
`opponent-crop-suppression-2026-07-18.md` (`4c8bc864…`), the flat opponent-crop
priority bonus `b100_e6` (bonus 100, ETA `<= 6`). Combined audit over 960 cells, 752 active:
mean margin `+4.860`, **own score `-0.481`, opponent score `-5.342`**, 7/8 families nonnegative.
Exchange rate **0.090 own points per opponent point removed** — the only sub-unity figure in the
corpus. It passed a frozen discovery block (480 cells: own `+0.744`, opponent `-4.406`) *and* an
unchanged fresh replication (480 cells: own `-1.706`, opponent `-6.277`), and became the live
resident. Its own document: "*It is principally denial: opponent score falls 5.342 while resident
score falls only 0.481.*"

`[MEASURED]` On 2026-08-02 the programme composed **exactly** that rule onto **exactly** the D89a
factory — constructor `banana_seed_factory_opponent_crop_b100_e6()` = `banana_seed_factory()` with
`opponent_crop_bonus = 100`, `opponent_crop_eta_limit = 6`. This is repair R2 with the single
denial policy in the corpus that is known to work. The three-arm paired smoke
(`banana-ring-b100-smoke-20260802T-r5.json`, `3b8e596d…`, 16 games, consumed seeds
1300–1307, both seats, `SMOKE_QUALIFIED`, all behavioural invariants pass) measures it. Paired
deltas recomputed by me from the 16 per-row `score`/`opponent_score` entries (Appendix A.6):

| arm | mean margin | mean own | mean opp | Δmargin | Δown | Δopp | leak ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fallback_b100_e6` (denial only, no factory) | `+24.500` | `185.688` | `161.188` | — | — | — | — |
| `live_unbounded_factory` (= D89a + `b100_e6`) | `+7.438` | `316.562` | `309.125` | **`-17.062`** | `+130.875` | **`+147.938`** | **`1.130`** |
| `bounded_ring` (= ring + `b100_e6`) | `-18.750` | `258.500` | `277.250` | **`-43.250`** | `+72.812` | `+116.062` | **`1.594`** |

**The leak ratio with the best available denial composed in is `1.130` — *worse* than D89a's
`0.511` on its own panel, and the composition is margin-negative (`-17.062`).** `[INFERRED]`
Adding the one denial rule that works does not close the leak; it does not even hold the ratio.

Caveats stated: n = 16 paired games (not 256), consumed seeds, a different resident base from
D89a's panel, and the artifact itself says "*paired smoke, not a fitted estimate*". This is
corroboration of D92, not a replacement for it — but it is **independent** corroboration, on a
different panel, twelve days later, with the strongest denial rule available.

### 4.3 Repair R3 — restrict activation by opponent family or map class — **MEASURED, FAILED (with one caveat that cuts my way)**

**Targets:** G4, G5, G8. **Mechanism:** abstain where the factory is unsafe, keep it where it is
not.

**Family selection is forbidden and would not work anyway.** `[MEASURED]` The frozen protocol
(`65bb19bf…`, line 8-9) forbids any "*map, opponent, score, turn, tree-count, supply, species, or
outcome selector*"; D91c repeats "*opponent names are forbidden*". For completeness I computed the
oracle family exclusion: dropping all 32 `gold_adaptive` tasks gives Δmargin `+91.781`,
Δown `+156.656`, **Δopponent `+64.875`** (G8 still 65x over), worst `-114`, p10 `-53`. It fixes
G4 and nothing else.

**Map-class selection was implemented and rejected.** `[MEASURED]` D91 (`c52b94c9…`) built a
three-predicate conjunction on the pre-treatment worker-two snapshot (live plants `<= 20`, fruit
on live plants `>= 27`, live BANANA plants `>= 6`). Implementation was clean: 256/256 decisions,
zero preactivation mismatch, 50 selected tasks outcome-identical to D89, 206 abstentions
action/state/terminal-identical to resident. On the consumed panel it looked excellent — overall
`+31.012`, selected `+158.780`, selected own/opponent `+239.520 / +80.740`, 47 improve / 3 regress,
p10 `+20`, worst `-25`, every family positive, leak ratio `0.337`. **It was rejected before
prospective execution** because selection concentrated in **5 of 16 maps**, giving a 16-map-cluster
95% CI of **`[-1.738, +63.761]`** — negative lower bound. Reciprocal eight-map fits held positive
mean but broke the tail floor (held-out worst `-96` to `-112` against a `-60` gate).

#### 4.3.1 The oracle bound — and where it cuts against my own verdict

`[MEASURED]` I computed the **best possible** activation restriction, using perfect hindsight
knowledge of every task's outcome — an upper bound no implementable selector can exceed
(`compute3.py`):

- **Maximum subset with mean Δopponent `<= +1`: 70 / 256 (27.3%).**
- That subset (after also excluding margin `< -60`): mean Δopponent **`+0.829`**, mean Δmargin
  **`+129.957`**, mean Δown **`+130.786`**, worst `>= -60`, p10 `>= -20`, **all 8 families, both
  seats**.
- As a whole-panel policy (select 70, abstain 186): overall mean margin **`+35.535`**, and the
  16-map-cluster 95% CI is **`[+14.248, +56.822]`** — **lower bound positive**.
- Map spread: **15/16 maps contribute at least one selected task**; 8/16 contribute `>= 4`.

Three consequences, stated plainly:

1. `[MEASURED]` **A leak-free, tail-safe, high-margin core of D89a exists**, it is not a single
   map cluster, and it would pass every gate D89a failed. Repairability is therefore not
   excluded by the data.
2. `[MEASURED]` **The corpus's stated closure reason is too strong.** `CONSTRAINTS.md:103-104`
   says factory selectors "*fail map transfer (selection on 5/16 maps)*". The *target* spans
   15/16 maps; D91's 5/16 concentration is a property of **its predicate grammar**, not of the
   thing being selected. One grammar, tested once, on 16 maps, is thin evidence for closing a
   branch.
3. `[INFERRED]` But the oracle is not a repair. It selects on **outcomes**, which the protocol
   forbids and which no controller can observe. The only pre-treatment grammar ever tried
   captured 50 tasks in 5 maps. The gap between "a 70-task target exists across 15 maps" and
   "a first-move predicate can find it" is exactly what D91 failed to bridge, and nothing in the
   corpus indicates the target is *learnable* from worker-two-boundary state.

**Status: `UNRESOLVED`, leaning `NOT_REPAIRABLE`.** This is the strongest surviving branch and I
am obliged to say so. See §8 for what would settle it and §5 for what it would cost.

### 4.4 Repair R4 — bound the ring / bound the orchard — **MEASURED, FAILED**

**Targets:** G5 (tail), D-5, owner design intent. **Mechanism:** confine planting to `<= 8`
tent-adjacent cells.

`[MEASURED]` The bound is encoded in `trace_detectors.py:829-888` (`detect_d5`, threshold 0):
every own `PLANT BANANA` must satisfy `cheby(cell, tent) == 1`; concurrent live own bananas
`<= |Ring|`; **cumulative distinct plant cells `<= |Ring|`**, with `|Ring| <= 8`; plus I-5
late-game cutoffs.

`[MEASURED]` D89a violates this massively. Its protocol (`65bb19bf…`, lines 11-14) places crops
by "*minimum farmer distance, minimum home-door distance, maximum opponent-door distance, and
lexicographic cell*" — no tent-adjacency constraint at all — and it records `+35.688` mean extra
successful plants per task (52 plants in the worst cell), with a *cumulative distinct plant-cell*
count far above 8. **D89a as frozen is not ring-bounded and cannot be made so without replacing
its placement rule entirely.**

`[INFERRED]` My prediction before looking for a measurement was that the ring bounds **spatial
extent**, not throughput — `<= 8` distinct cells replanted repeatedly still sustains a high
harvest/replant rate — and that since §3.2 locates the leak in **redirected chop pressure and
board enrichment** rather than in planting geography, a ring bound constrains the wrong variable.
It should reduce the enrichment term (fewer distinct crop sites for an adaptive opponent to route
onto) while doing nothing to restore denial pressure, which is the larger half. §4.4.1 shows this
prediction is confirmed by an actual measurement.

#### 4.4.1 The bounded ring was actually built and measured — and it made things worse

`[MEASURED]` The bound was implemented (`banana_ring_opponent_crop_b100_e6()`;
`chatgpt_1/banana-ring-b100-successor/{protocol,implementation-delta}.md`) with exactly the D-5
geometry: "*The banana farm is the up-to-eight Chebyshev-distance-1 cells around our tent and
nothing else*", diagonal cells as protected mothers, orthogonal cells as consumable wood slots,
`MIN_FARM_CELLS = 4`, `RING_LIQUIDATION_TURNS = 34`. Its behavioural invariants all passed in the
r5 smoke: `plants_outside_ring = 0`, `max_own_banana_chebyshev_from_tent = 1`,
`max_concurrent_own_ring_bananas = 8`, `diagonal_ordinary_chops = 0`, 727 orthogonal chops,
330 post-full-ring BANANA drops, wood deposit `+910`. **The geometry works exactly as designed.**

`[MEASURED]` Its value effect, paired against the unbounded factory arm on the same 16 games
(recomputed by me, Appendix A.6):

> `bounded_ring` − `live_unbounded_factory`: **Δmargin `-26.188`, Δown `-58.062`,
> Δopponent `-31.875`** ⇒ **1.822 own points spent per opponent point removed**.

Bounding the orchard removed **`31.875`** of opponent score at a cost of **`58.062`** of ours, and
moved margin from `+7.438` to `-18.750`. Against the no-factory `b100_e6` fallback the ring still
leaks `+116.062` opponent for `+72.812` own — **ratio `1.594`, three times worse than D89a's
`0.511`**. Catastrophes rose 5 → 6 and negative-margin mass 589 → 690.

`[MEASURED]` Both arms were then Arena-tested. The unbounded factory + `b100_e6` (agent `6590083`,
submission `41081195`): 98 games, 49W/49L, mean margin `+4.643`, **22 catastrophes (22.45%)**,
Arena row **12.99 at rank 127/131** — against a resident holding 21.76 at rank ~45. The bounded
ring (agent `6590136`, submission `41081465`): 4W/6L, mean margin `-110.8`, filtered
**13.46 at rank 126/131**, then terminated `IMPLEMENTATION_INVALID / DISPLACED` on a
live oscillation incident (game `897829265`, worker 2 reversing `(10,4)<->(11,4)` turns 20–29 and
`(8,2)<->(8,3)` turns 269–280, both with empty cargo). The incident document states the ring
result "*must not be resubmitted or used as a banana-value observation*" — so I use the ring's
**smoke** numbers, which are valid, and cite the ring's Arena row only as an execution outcome.

`[INFERRED]` The ring bounds **spatial extent**, not throughput: `<= 8` cells replanted repeatedly
still sustains a high harvest/replant rate. Since §3.2 locates the leak in **redirected chop
pressure and board enrichment**, not in planting geography, the ring constrains the wrong
variable — and the measurement agrees.

`[MEASURED]` chatgpt_1's whole-programme disposition reaches the same design conclusion from the
other direction: "*The bounded ring correction is the durable design seed…* **The unbounded field
is dead.**" That is a statement about **geometry safety**, correct on its own terms, and it should
not be read as a repair for G8.

**Status: `NOT_REPAIRABLE` `[MEASURED]` — built, geometrically correct, and value-negative.**
Genuinely useful for D-5 and as design intent.

### 4.4b Repair R8 — geometry restriction to contested-free zones — **already in D89a, and it leaks anyway**

`[MEASURED]` The frozen D89a protocol *already* ranks planting cells by
"*minimum farmer distance, minimum home-door distance, **maximum opponent-door distance**, and
lexicographic cell*", and the reserve cell by "*water adjacency, home accessibility, **opponent
distance**, and deterministic cell order*". **Planting as far from the opponent as the map allows
is not a proposed repair — it is what D89a already does**, and it produced `+82.863`.

`[INFERRED]` This is a strong independent confirmation of §3.2's mechanism: if the leak were
driven by the opponent physically reaching our crops (direct theft), opponent-distance maximisation
would already have suppressed it. It did not, which is consistent with the reported theft term
being the minority `+12.453` and the majority being the opponent's *own* production. The remaining
degree of freedom — planting only in zones the opponent provably never visits — is not a
controller the corpus contains, and R4's measurement (the tightest possible geometry restriction,
8 cells at the tent) is the natural upper bound on what geometry alone can buy: `1.822` own points
per opponent point.

**Status: `NOT_REPAIRABLE` `[MEASURED]` — already applied at full strength.**

### 4.4c Repair R9 — conversion timing — **`UNRESOLVED`, but bounded by R1**

`[MEASURED]` D89a converts to wood late and completely: terminal bank means are `92.777` WOOD
against `1.375` PLUM / `0.621` LEMON / `5.441` APPLE / **`0` BANANA** / `0.438` IRON (D93a,
`b0a6c0c3…`). Every banana is consumed. The blueprint's rule 6 sends every harvested BANANA
straight to a conversion cell and replants; rule 4 protects exactly one reserve crop.

`[INFERRED]` Converting *earlier* (bank the fruit as 1 point instead of growing it into 4-point
wood) reduces board enrichment — fewer live crops for an adaptive opponent to route onto — but at
a 4:1 score penalty on the converted units. Converting *later* is already what it does. Either
direction reduces `Δown` faster than `Δopp`, which is the R1 arithmetic (§4.1) under a different
parameterisation.

**Status: `UNRESOLVED`, bounded above by R1's disjoint-`k` result `[INFERRED]`.** Would be settled
by the same throttled-arm experiment as U5 (§8).

### 4.5 Repair R5 — late-game-only activation

**Targets:** G8, G5. **Mechanism:** if the leak accrues over the whole game, a short late window
accrues less of it.

`[MEASURED]` Forbidden by the frozen protocol ("no … turn … selector", line 8-9), so this is
strictly a new-protocol option.

`[MEASURED]` D89a's own activation is already late-ish and heterogeneous: `activation_turn` has
r = `+0.018` with `delta.opponent_score` — **no relationship whatsoever**. Later activation on
this panel did not reduce the leak.

`[MEASURED]` The nearest tested analogue is the mirror image: D175a moved planting *earlier* and
the leak got worse (`Δopponent +21.09`). `[MEASURED]` D89a's terminal state is
`92.777` WOOD vs `1.375` PLUM / `0.621` LEMON / `0.438` IRON (D93a, `b0a6c0c3…`), i.e. the factory
converts to wood late; truncating the window truncates the conversion, so this collapses to a
special case of R1 (§4.1) with the same disjoint-`k` arithmetic.

**Status: `NOT_REPAIRABLE` `[INFERRED]`, on `activation_turn` r ≈ 0 plus the R1 arithmetic.**

### 4.6 Repair R6 — the repair the blueprint/result document itself proposes — **MEASURED, FAILED**

`[MEASURED]` The D89a result document's own "Next eligible experiment" (lines 63-70) is the
**source-separated** controller: harvest only bank-seeded reproductive crops, never
harvested-fruit descendants. This was executed as **D90a** (`4cec5874…`):

> "*The source boundary changes only 19/256 tasks… mean margin moves from `+79.441` to `+78.008`,
> own score from `+162.305` to `+160.680`, and opponent score only from `+82.863` to `+82.672`.
> The p10 (`-72`), worst (`-235`), catastrophe count (11), negative-margin mass (3,112), and
> Gold-adaptive mean (`-6.938`) do not improve.*"

Leak removed: `0.191` of `81.863` needed (0.23%), at a cost of `1.625` own score — exchange rate
**8.508 own per opponent point**. Verdict: "*Reject source eligibility as the D89 tail repair.*"

`[MEASURED]` The blueprint's second implied lever — the yaichi `ATTACK` blockade — was closed by
D90b: 343 unit-turns / 94 episodes across 14 of 35 games, every target one orthogonal step from
the opponent shack, median entry turn 174.5, all episode starts with zero carried items. Verdict:
"*`ATTACK` is a resource-exhaustion/bank-blockade fallback after ordinary crop work has
disappeared… Do not graft a shack-door rush onto the live factory as a D89 repair.*"

**Status: `NOT_REPAIRABLE` `[MEASURED]` — both of the document's own proposals were executed and
rejected.**

### 4.7 Repair R7 (out-of-scope but measured, for completeness) — capacity expansion

`[MEASURED]` D93a proved D89a can never fund worker three (0/256 balanced bills, 0 legal turns,
zero tasks ever holding cheap IRON). D94b/c built the existing-stock bridge anyway: it trained
worker three in 147/256 tasks and lost **`-91.633` mean margin** to D89, `[-132.098, -51.168]`,
221/256 regressions, catastrophes 11 -> 35, every family negative. It removed `24.172` of
opponent score at a cost of `115.805` own score — exchange rate **4.791**.

### 4.8 Repair scoreboard

| # | repair | targets | status | leak removed | own-score cost | exchange rate |
|---|---|---|---|---:|---:|---:|
| R1 | rate-limit the factory | G8, G5 | `NOT_REPAIRABLE` `[ASSUMED]` / concavity `UNRESOLVED` | — | total (margin -> `+0.96`) | — |
| R2 | denial/interference budget (D92) | G8, G4 | **`NOT_REPAIRABLE` `[MEASURED]`** | `13.883` broad; `-0.188` trained-only | `20.254` / `5.422` | **1.459** / **INF** |
| R2.1 | D89a composed with `b100_e6`, the one denial rule that works | G8 | **`NOT_REPAIRABLE` `[MEASURED]`** | leak *rises* to `+147.938` | `Δmargin -17.062` | **ratio `1.130`** |
| R3 | activation restriction (D91) | G4, G5, G8 | **`UNRESOLVED`, leaning NOT** | oracle: `81.9` | oracle: `31.5` | oracle: 0.38 (unattainable) |
| R4 | bound the ring / orchard | G5, G8, D-5 | **`NOT_REPAIRABLE` `[MEASURED]`** | `31.875` | `58.062` | **1.822** |
| R5 | late-game-only activation | G8, G5 | `NOT_REPAIRABLE` `[INFERRED]` | `activation_turn` r = `+0.018` | — | — |
| R6 | source separation (D90a) — the doc's own proposal | G5, G8 | **`NOT_REPAIRABLE` `[MEASURED]`** | `0.191` | `1.625` | **8.508** |
| R7 | worker-three capacity (D94) | — | **`NOT_REPAIRABLE` `[MEASURED]`** | `24.172` | `115.805` | **4.791** |
| R8 | geometry: contested-free zones | G8 | **`NOT_REPAIRABLE` `[MEASURED]`** — already applied at full strength in the frozen protocol | — | — | — |
| R9 | conversion timing | G8 | `UNRESOLVED`, bounded above by R1 | — | — | — |

**Nine repair classes considered. Seven closed by measurement or arithmetic; two (`R3`, `R9`)
`UNRESOLVED`, and `R9` reduces to `R1`.**

### 4.9 The exchange rate — stated precisely, including its one counterexample

`[MEASURED]` **On the D89a factory substrate, every leak-reducing lever ever measured costs more
own score than the opponent score it removes**: `1.130` (R2.1 — the leak actually *grows*),
`1.459` (D92 broad), `1.822` (R4 ring), `4.791` (D94 bridge), `8.508` (D90a source separation),
and **infinite** (D92 trained-only — 5.4x the denial volume, opponent score `+0.188`). **Six for
six, no exceptions.**

`[MEASURED]` **There is exactly one counterexample anywhere in the repo, and it is not on this
substrate**: `b100_e6` (§4.2.1) removes `5.342` opponent points for `0.481` of ours — exchange
rate `0.090`, and it passed a frozen discovery block plus an unchanged replication. I state it
because it is the one fact that could support a `REPAIRABLE` verdict and it would be dishonest to
omit it. It does not rescue D89a for two measured reasons:

1. **Magnitude.** `5.342` against a needed `81.863` — **15.3x too small**, and the sweep in the
   same document shows the mechanism does *not* scale: `b250`/`b500`/`b1000` and ETA 10/20 all
   suppress more (up to `-17.031`) but fail their family/tail gates, with own-score cost rising
   from `0.481` to `8.233` — the exchange rate degrades monotonically with dose (0.09 → 0.48).
2. **Composition.** It was *actually composed* with D89a in August and the result is R2.1: the
   leak ratio came out at `1.130`, worse than D89a alone. The counterexample does not survive
   contact with the factory.

`[MEASURED]` The wider denial corpus is uniformly worse: pre-fruit reproductive interruption
(`-36.992` opponent for `-118.683` own), capacity-separated reproductive denial (`-17.658` for
`-100.717`), resident chopper-layer transplant (`-37.650` for `-82.150` — "*production damage is
more than twice the suppression benefit*"), and the N6 denial-weight sweep, where **both**
halving and doubling the resident's denial scalar *raised* opponent score (`+0.787` and `+0.271`).
The largest opponent-score suppression ever achieved by any implemented controller at any cost is
`-37.650`. **D89a's leak is `+82.863` — 2.2x larger than the entire measured reach of denial in
this repository.** That is the single most important number in this document.

`[MEASURED]` It is also the corpus's own standing conclusion, `CONSTRAINTS.md:241-251`:

> ★★★ PRODUCTION IS STRUCTURALLY NEGATIVE FOR THIS ARCHITECTURE — three independent
> confirmations: D89 (full factory, opponent +82.9, of which +76.5 from the opponent's own crops),
> B4.5 (field: higher-planting peers give opponents +20.8, CI [1.8,38.0]), D175a (bounded early
> planting: Δown −5.41, Δopponent +21.09, overall −26.44…). … **do not reopen production without
> first changing harvest capability AND demonstrating denial is preserved.**

Note the reopening condition is a **conjunction**, and D89a satisfies exactly half of it: it
*does* change harvest capability (10,729 harvests, 252/256 sustained). It does **not** preserve
denial — which is precisely §3.2.

---

## 5. Question 4 — would any repair introduce D-1 or D-4 episodes?

Predicates read directly from `claude_1/banana-restoration-r2/trace_detectors.py`
(`59dce10d…`). Threshold for both is **0 episodes across all 240 panel games**
(`:549-551`) — one occurrence anywhere is a FAIL.

**D-1 (`:555-621`)** — an own unit alternating strictly between exactly two cells for
`>= 7` consecutive states (`(t-1) - s >= 6`, line 605, hard-coded), with **zero progress events**
in the window: `carry` unchanged every step, own `inventories[0]` unchanged on any DROP/PICK turn,
and no plant created/removed at the unit's own cell. Standing still breaks it; a 3-cycle never
fires; no time gate, no geometry input.

**D-4 (`:757-826`)** — within a *wood-committed* interval (entered when `carry[WOOD] > 0` **and**
either `free_capacity() == 0`, or a `MOVE <door>`, or a `DROP` on a door), either
(a) any command in `D4_BANNED_VERBS = {HARVEST, CHOP, PLANT, MINE, PICK}` (`:108`) — fires
**immediately, no slack**; or (b) two consecutive transitions with `door_dist(next) >= door_dist(now)`
(`nd_run == 2`, line 821), using a **static, unit-agnostic** BFS from the shack doors. Commitment
ends only on a door DROP, death, or cargo loss.

Assessment per repair. `[INFERRED]` throughout — no trace of any repaired D89a variant exists, so
none of this is measured on a repaired controller.

| repair | D-1 risk | D-4 risk | verdict |
|---|---|---|---|
| **R1 rate-limit** | LOW **if** the throttle is `WAIT`-in-place (breaks the alternation predicate). **HIGH** if implemented as step-away/step-back — a 1-cell hold pattern for `>= 7` turns with unchanged `carry` is *literally* the D-1 predicate. | **HIGH.** A hold of `>= 2` turns on a wood-committed carrier is a guaranteed `no_progress` episode. Route A already hit this and had to special-case it: `gate-results-v6-2026-08-06.md:55-57` — "*the resident holds one turn (**wood-free turns only — a wood-committed WAIT would trip D-4**)*". | **SURVIVES only under a strict rule: throttle only when `carry[WOOD] == 0`, and never by repositioning.** |
| **R2 denial budget** | MODERATE. Budget exhaustion reverting a unit's goal onto a peer-occupied cell is exactly the measured D1-A mechanism (parked peer + memoryless `min_by_key((BFS_dist, Cell))` detour). A spend/refill goal alternation is the D1-B two-cycle, the residual Route A could not localise. | **FATAL.** Denial *is* `CHOP`, and `CHOP` is in `D4_BANNED_VERBS`. A carrier that is full, or that has emitted one `MOVE <door>`, is committed until it DROPs; one denial chop en route fires `non_bank_verb` on the spot with no slack window. Detouring to a denial target instead fires `no_progress` after 2 turns. | **DEAD ON ARRIVAL** unless denial is consultable *only* when `carry[WOOD] == 0` and uncommitted — which is precisely the low-leverage regime D92 measured at zero efficacy. |
| **R3 activation restriction** | Neutral for the wrapper; **cannot help**. The 32 D-1 games / 35 episodes are the *parent's* inherited behaviour, measured with the parent as its own candidate. | Neutral; same. The 6 D-4 games are parent floor. | **SURVIVES** (adds nothing, removes nothing). |
| **R4 bound the ring** | **RAISES** risk — and this is now `[MEASURED]`, not inferred: see §5.1. Corroborating floor statistics: restricted to 2-unit games, D-1 eligibility is `orchard_eligible` 31%, `choke_corridor` 30%, `forest_sparse` 30% vs `open_field` 11%, `water_diagonal` 5% — fewer targets ⇒ more same-tree contention ⇒ more memoryless detours. | Mostly neutral geometrically, but **all 6 floor D-4 episodes are on single-door maps (0/210 on `>= 2`-door maps)**; a ring concentrating traffic through tent-orthogonal cells worsens door serialisation. Round 5's terminal injury was exactly this (protected mother = BFS articulation cell, 225-turn livelock). | **FAILS D-1 in live play (§5.1).** |
| **R5 late-game-only** | Neutral-to-**worse**: D-1 has no time gate, and late maps are the "last remaining tree" regime (20/240 games start with 0 plants, 54 with 1, 48 with 2). | Neutral-to-worse: more accumulated wood in transit late. | **SURVIVES with elevated risk.** |
| **R6 source separation** | Changes harvest *eligibility* only; no motion pattern change. | No commitment-interval change. | **SURVIVES.** |

### 5.1 R4 did not merely risk D-1 — it produced one, in a live Arena game `[MEASURED]`

The bounded ring was submitted (agent `6590136`, submission `41081465`) and terminated
`IMPLEMENTATION_INVALID / DISPLACED` on an oscillation incident. Exact game `897829265`,
worker 2, detector `p[t] == p[t-2] != p[t-1]`:

| turns | positions | carried stock | behaviour |
|---|---|---|---|
| 20–29 | `(10,4) <-> (11,4)` | empty | reversing MOVE every turn |
| 269–280 | `(8,2) <-> (8,3)` | empty | reversing MOVE every turn |

Diagnosis: "*The bot regenerates the trained worker's tree choice every turn, so a state-dependent
target/routing decision reverses with the worker's position.*" Both episodes are ≥ 10 states of
strict two-cell alternation with empty cargo — **squarely inside `detect_d1`'s predicate**
(≥ 7 states, `carry` unchanged, no plant flip at the unit's cell). This is exactly the D1-A
memoryless-goal-regeneration mechanism Route A's floor analysis identifies, reproduced by the
ring geometry in live play.

`[INFERRED]` The ring bound *causes* this class: fewer legal targets ⇒ more same-target
contention ⇒ more per-turn goal regeneration. R4 is therefore not "elevated risk" — it is a
`[MEASURED]` D-1 producer.

**Answer to Question 4:** of the nine repair classes, **R2/R2.1 (denial budget) is dead on arrival
on D-4** in any useful form (denial *is* `CHOP`, and `CHOP` is a banned verb inside a
wood-committed interval, firing with no slack); **R4 is a measured D-1 producer**; **R1
(rate-limit) survives only under a strict `carry[WOOD] == 0` restriction**; R5 survives with
elevated risk on both; R3, R6, R8 and R9 are D-1/D-4-neutral. **So: 6 of 9 survive the D-1/D-4
constraint, but the two that do not are the only classes that attack the leak's primary mechanism
directly** — and both were already independently rejected on value (§4.2, §4.4).

`[MEASURED]` Separately: **D89a as frozen is a massive D-5 violator** (§4.4). D-5 is not
owner-standing, but any D89a revival inside the R2 detector suite would have to be re-geometried
before it could be measured at all.

`[MEASURED]` One cross-cutting warning from Route A's own feasibility work that applies to every
repair here: D-1 is **fragmentation-sensitive**. The best oscillation breaker the project ever
built (D176a) would have taken D-1-eligible runs from `~213 + >=174` to `~825 + >=59` — **more
than doubling the raw episode count** — because the standing rule counts episodes, not turns. Any
repair that converts one long pattern into several short ones makes raw D-1 **worse**.

---

## 6. Question 5 — honest cost comparison against Route A

### 6.1 Route A, as its own documents state it `[MEASURED]`

- **Start** `2026-08-02T17:45:26Z`; latest artifact `2026-08-07`. **~5 days**, 35 commits under
  `claude_1/banana-restoration-r2/`. Route A's own disposition review calls this
  "*the bulk of the week*" and adds "*R2 not knowing D89a existed — possibly the whole week.*"
- **Six gate rounds** (`gate-results-2026-08-04.md`, `v2`..`v6`), plus a seventh design-first
  reset that produced no candidate.
- **Six candidate hashes. Zero valid candidates.** `f29efd0e` (I-9 falsified by its own
  lifecycle trace), `280ed777` (health/chop arithmetic), `2f58edef` (three conflicting conversion
  deadlines), `9f5ef833` (225-turn `(8,4)<->(8,3)` full-cargo oscillation; parent margin `+68`
  becomes `-93`), `47c98f53` (withdrawn pre-host, 141/240 blocking), `eac2eb36`
  (47/240, "*explicitly a stabilization baseline, not a handoff*").
- **No Route A candidate has ever reached host replay, a value protocol, or the Arena.**
- **The gate blocks its own reference: 118/240** (240 = 120 maps x 2 seats; 118 = blocking
  *games*, parent run as its own candidate). Raw, pre-P4-calibration, it was **223/240** — 93%.
- **Perfect raw D-1/D-4 compliance moves the floor 118 -> 106.** Only **12** of 118 games block
  *solely* on D-1/D-4. The dominant residual is **D-9 (74 games, sole blocker in 63)**, which is
  *candidate-invariant* — it fires on exactly 74 games for the floor, for `bbe54a48`, and for the
  tip alike, so it measures nothing about any candidate. Even zeroing D-1, D-4 **and** D-9 leaves
  **42** blocking games. D-2/D-3/D-8 are at zero because they are **unexercised**, contributing a
  false green.
- **Route A's own feasibility verdict on its critical prerequisite:**
  "`UNRESOLVED`, leaning `INFEASIBLE` at acceptable cost" — because D1-B is unlocalised and one
  episode blocks, and the only measured attempts at D1-A's mechanism both failed their frozen
  mechanism gates, "*with the better one increasing the very quantity the rule counts.*"
- **Route A is currently under a stop condition**: "*no further implementation from
  [the FSM design] until the gate can reach ACCEPT.*"

### 6.2 Like-for-like: what each route needs before a candidate could be Arena-tested

| step | Route A (R2 wrapper) | D89a revival |
|---|---|---|
| 1. instrument | **Phase 1: repair the gate.** D-9 calibrate-or-retire (74 games), P4 liveness (29-32 games), fixtures for three unexercised detectors, gate architecture rebuilt against 9 review findings, plus a **new invariant class for the schedule/opponent-production leak that does not yet exist**. Exit = a floor self-test where every blocking class is a genuine defect or explicitly `UNPROVEN`, stable across two machines. | **Already exists and is frozen.** `analyze_d89a_banana_seed_factory.py` (hash-locked in the freeze manifest), 15 integrity gates, 6 activation gates, 15 value gates. Its own reference (the resident arm) is exact by construction — 0 inactive mismatches, byte-identical 1-thread/20-thread repeats. **No calibration debt.** |
| 2. base | **Phase 2: surgery on the parent's inner policy.** D-4 feasible; **D-1 `UNRESOLVED`**. Blast radius, per Route A's own §7.2: invalidates every committed floor number; re-opens all five wrapper insertion anchors and the compactor-idempotence claim; invalidates P3 orchard byte-inertness; **requires fresh Arena qualification of the resident**; consumes a 2,048-task sealed validation budget. Priced as "*comparable to D171a or D176a — each a full experiment cycle, both of which closed.*" | **None needed.** The D89a controller compiles and runs today: `rust/src/bin/yamo_orchard_live.rs` carries **306** `banana_factory` references, disabled-by-default; the paired harness `rust/src/bin/ownership_aware_complete_economy.rs` is present; all 8 opponent strategies are present in `rust/src/strategies/`. |
| 3. mechanism | **Phase 3: re-implement from a 15-gap design** (8 gaps needing refactor), contracts -> executable -> **1,594-config** enumeration -> broad fuzz -> host replay. Cannot start until step 2 lands. | **Already measured**: 256/256 activation, 1,344/1,344 bootstrap, 252/256 sustained, 10,729 harvests, zero shadow mismatch, zero trained forbidden commands. |
| 4. value | **Phase 4**, never reached. | **Already measured and FAILED**: 4 of 15 value gates. This is the entire remaining problem. |
| 5. residual work | Phases 1-4, none priced, the critical one `UNRESOLVED, leaning INFEASIBLE`. | **One thing: an implementable pre-treatment selector that finds the §4.3.1 core** — plus fresh maps (`9,914,064+` were consumed by D91's protocol; a new sealed range is needed), a new frozen protocol, and a D-5 re-geometry if it must live inside the R2 detector suite. |

### 6.2b One asymmetry the brief did not anticipate: the D89a architecture *has* been Arena-tested

`[MEASURED]` Route A has never reached the Arena. The D89a architecture has — twice, on
2026-08-02, by owner override, skipping the planned 2,048-game discovery panel:

| submission | what it was | Arena result |
|---|---|---|
| agent `6590083` / `41081195` | D89a factory + `b100_e6`, unbounded | 98 games, 49W/49L, mean margin `+4.643`, **22 catastrophes (22.45%)**, negative-margin mass 4,851, row **12.99 at rank 127/131** |
| agent `6590136` / `41081465` | bounded ring + `b100_e6` | 4W/0T/6L, mean margin `-110.8`, 5 catastrophes, row **13.46 at rank 126/131**, then `IMPLEMENTATION_INVALID / DISPLACED` (§5.1) |

Against a resident holding **21.76 at rank ~45**. `[INFERRED]` The unbounded run is the more
informative of the two (the ring run is disqualified as an implementation failure, and its own
document says it "*must not be… used as a banana-value observation*"): the factory architecture,
carrying the best available denial rule, produced a **near-coin-flip win rate with a 22%
catastrophe rate and a rating ~9 points below the resident**. Its disposition is "*clean but weak
provisional 98-game evidence*".

This cuts **against** D89a and I record it as such: the one route that has actually been
measured in the Arena was measured at rank 127/131.

### 6.3 The comparison, stated without hedging `[INFERRED, from measured inputs]`

**D89a is ahead of Route A on steps 1, 2, 3 and 4-as-measurement.** It has a working mechanism,
a hash-locked analyzer that does not block its own reference, a runnable candidate, and a
quantified failure. Route A has none of these: no working mechanism, an instrument that rejects
93% (raw) / 49% (calibrated) of games for a bot identical to the thing it protects, a base whose
required repair is rated possibly-infeasible, and zero candidates in ~5 days and six rounds.

**D89a is behind on exactly one thing, and it is the thing that matters**: its remaining problem
is a **value/safety** failure with no measured solution, whereas Route A's remaining problems are
engineering ones with known (if expensive) shapes. Seven of nine repair classes for D89a are
closed by measurement or arithmetic; the two that remain are a selector grammar one prior attempt
failed to find, and a throttle whose only measured endpoint (R4) came out at `1.822`. Route A's
problems are at least *addressable in principle* — Phase 1 in particular is "highest value, zero
bot risk" and is not blocked on anything. And §6.2b adds the one hard outcome D89a has that Route
A does not: an Arena placement, at rank 127/131.

### 6.4 Where this cuts against my own line — stated plainly

The honest reading is **not** "Route A is fine and D89a is dead". It is:

1. `[MEASURED]` **Route A's six gate rounds are worthless as evidence.** Its own disposition
   review says so: they are "*verdicts issued by an instrument that was blocking its own
   reference implementation and had never been asked whether it did… They must not be cited as
   evidence about any candidate again.*" A week of my line's output has no evidential value.
2. `[MEASURED]` **Route A's critical prerequisite may be infeasible.** Raw D-1 = 0 on this parent
   is "*not reachable at a cost proportionate to the 12 games it would unblock.*" That is my own
   accepted scoping, arguing against my own line.
3. `[MEASURED]` **D89a's infrastructure is strictly better than Route A's.** The freeze manifest,
   the analyzer, the harness, the candidate source and all 8 opponents are present and
   hash-consistent. Route A cannot say any of that.
4. `[INFERRED]` **The `NOT_REPAIRABLE` verdict I have reached is therefore *not* a licence to
   proceed with Route A.** If it is read that way, this document has been misread. The correct
   reading is that the *banana-production programme as a whole* — both lines — is blocked on a
   fact neither line can change: in this architecture, production feeds the opponent at a
   measured exchange rate no lever has ever beaten.

I considered, and reject, the case that D89a is the better route and Route A should be wound
down *in favour of D89a*. Not because it would embarrass my line — §6.3 concedes D89a is ahead
on four of five dimensions — but because D89a's single remaining problem has **seven measured or
arithmetic closures and two thin `UNRESOLVED`s**, and because the one time the architecture was
actually put in front of the Arena it placed at rank 127/131 with a 22% catastrophe rate. Route
A's problems, though larger, are at least of a kind the programme knows how to attack. Winding
down Route A **in favour of nothing** (see §9) is a separate and, on these numbers, defensible
option.

`[INFERRED]` The honest summary of the route question the owner actually asked — *is repairing
D89a a better use of effort than the R2 wrapper line?* — is **no, but not because the R2 wrapper
line is good.** It is: the leak is structural, the D89a route's cheap remaining question (U4) is
worth hours and should be run, and after that the banana-production direction should be closed
regardless of which line nominally owns it.

---

## 7. Verdict

**`NOT_REPAIRABLE`.**

For the exact D89a controller, against the exact `<= +1` mean-opponent-score gate, by any
mechanism the corpus contains:

- `[MEASURED]` **Seven of nine repair classes were already executed and rejected, or are closed by
  arithmetic** — source separation (D90a, removes 0.23% of the leak), shack blockade (D90b,
  causally inert during the productive phase), denial composition (D92, both arms), denial
  composition with the *best* rule in the corpus (R2.1, leak ratio rises to `1.130`), orchard
  bounding (R4, built, geometrically correct, `1.822` exchange rate, margin `+7.44 -> -18.75`),
  capacity expansion (D94b/c), and contested-free geometry (R8, already applied at full strength
  in the frozen protocol).
- `[MEASURED]` **On the factory substrate, every leak-reducing lever costs more than it removes**:
  1.130, 1.459, 1.822, 4.791, 8.508, and infinite. Six for six. The one sub-unity denial rule in
  the whole repository (`b100_e6`, exchange rate 0.090) removes `5.342` points — **15.3x too
  small** — degrades monotonically with dose, and when actually composed with D89a produced a
  *worse* ratio than D89a alone.
- `[MEASURED]` **The largest opponent-score suppression ever achieved by any implemented
  controller in this repository, at any cost, is `-37.650`.** D89a's leak is `+82.863` — **2.2x
  the entire measured reach of denial**.
- `[MEASURED]` **The tail and the leak are orthogonal.** Oracle abstention on the 96 worst-margin
  tasks (37.5% of the panel) still leaves mean Δopponent at `+58.044` against a `+1` ceiling.
  Fixing the tail does not touch the leak.
- `[ASSUMED/MEASURED]` **Rate-limiting is arithmetically infeasible** under proportional scaling:
  the opponent gate needs `k <= 0.0121`, the margin gate needs `k >= 0.0504` — disjoint by 4.2x.
- `[MEASURED]` **Gate relaxation does not rescue it.** Under D91c's own successor ratio gate
  (`<= 0.40`) D89a still fails at `0.511`, *and* independently fails the worst-family, p10 and
  worst-margin gates.
- `[MEASURED]` **The corpus's standing ★★★ constraint** already records this as one of three
  independent confirmations that production is structurally negative for this architecture, with
  a reopening condition (change harvest capability **AND** demonstrate denial is preserved) that
  D89a satisfies only halfway.

**Two `UNRESOLVED` sub-questions**, neither of which changes the verdict on any near horizon:

- **`R3` — an implementable pre-treatment activation selector.** An oracle target exists
  (70/256, Δopponent `+0.829`, Δmargin `+129.957`, 15/16 maps, cluster CI `[+14.248, +56.822]`).
  One grammar was tried and failed on map-cluster support. Whether a better grammar exists is
  genuinely open. Note that even if it succeeds it repairs the *gate*, not the mechanism: the
  controller would still leak on the 186 tasks it abstains from running at all.
- **`R1`/`R9` — the concavity of own-score vs leak in the production rate / conversion timing.**
  No throttled-D89a arm has ever been measured. R4 is the tightest geometric throttle ever built
  and it came out at `1.822`, which is evidence against, but it throttles extent rather than rate.

**Strongest single piece of evidence behind the verdict:** D92's trained-only isolation.
`[MEASURED]` It produced **898** opponent-crop denial target selections against D89's incidental
**166** — a **5.4x** increase in denial volume, with the productive starter policy proven
unchanged by source tests — and the opponent's score moved by **`+0.188`**, i.e. *upward*, while
ours fell `5.422`. That is a direct, controlled measurement (n = 256 paired tasks, both seats,
eight families) that the obvious repair for the identified mechanism has **zero** efficacy on this
substrate at 5x the dose.

Its strongest **independent** corroboration, from a different panel twelve days later: composing
D89a with `b100_e6` — the only denial rule in the repository that has ever removed opponent score
more cheaply than it cost us — produced a leak ratio of `1.130`, *worse* than D89a alone, and a
margin of `-17.062` against the denial-only baseline (§4.2.1). The obvious repair does not merely
fail to work; when it is the best available and is applied directly, it makes the ratio worse.

---

## 8. What would settle each `UNRESOLVED`

| # | question | evidence that would settle it |
|---|---|---|
| U1 | the `+12.453` / `+76.508` split (§2.2) | The 20 provenance columns `4 x opponent_from_{natural,ours,opponent,unknown}` + `16 x opponent_fruit_from_{natural,ours,opponent,unknown}_{plum,lemon,apple,banana}`. **The original bytes are unrecoverable** — see below. Only a re-run would produce them, and it would not be byte-comparable. |
| U2 | the `+36.441` own-side residual (§2.3 check 3) | Same rows, own-side columns. Until then the result document's own-side sentence is an **unverified figure** and should be cited with that caveat. |
| U3 | does D89a lengthen games? (§3.3) | `terminal_turn` is read by the analyzer but not emitted. A one-line analyzer change + re-run, or the raw rows. |
| U4 | `R3` — is the §4.3.1 core selectable from pre-treatment state? | An offline, read-only experiment on the D91 activation snapshot (140 fields, already proven pretreatment) against the oracle-70 labels: fit and cross-validate under map-held-out splits. **No controller, no host game, no fresh maps required** — the labels are in the committed JSON and the snapshot exists. This is by far the cheapest open question in either route. |
| U5 | `R1`/`R9` — the concavity of the production/leak curve | A throttled-D89a arm (e.g. cap concurrent tracked crops at 2/4/8, and vary conversion timing) on the consumed panel — three points on the curve. R4 supplies one endpoint already. |

**U1 is definitively closed as an archival question `[MEASURED]`.** The D89a panel TSVs were never
committed on any of the 52 refs (`git log --all --diff-filter=A --name-only -- '*d89a*'` lists
only the analyzer, its test, the four md/json documents and the 2026-08-07 scoping task).
`.gitignore` excludes `/artifacts` and `/outputs` as external-backed bulk roots;
`docs/storage-policy.md` puts them under `/media/tarstars/medium_data/database/troll_farm`, and
**`/media/tarstars` does not exist on this host** — corroborated by a dangling symlink in the
checkout (`data/analysis/live-agent-6553250/training-denial-telemetry.json` -> that path). A
filesystem sweep of `/home/tarstars` for `*9914*` and `*rows-{a,b}.tsv` found nothing but git
blobs of the already-committed documents.

Worse for a re-run: the panel binary `rust/src/bin/ownership_aware_complete_economy.rs` in the
current tree emits **240 columns**, whereas D93a records "*All 140 fields shared with the original
D89 discovery panel*" — the schema grew by ~100 columns (48 `worker3_*`, 14
`banana_factory_worker_three_bridge_*`, and others) after D89a froze. A re-run would therefore
**not** reproduce the frozen `358160eaf53b31fb53e50fb2f3db5a5e109f84aa5fc042e8447acf3be5f630ab`
TSV hash, so it could not be certified as the same measurement. `[INFERRED]` U1 and U2 are
permanently `UNRESOLVED` at the level of the frozen artifact; only a *new*, separately-frozen
measurement can answer them.

`[INFERRED]` **U4 is the single highest-value next step in this whole area** and costs a read-only
analysis, not an experiment cycle. If a map-held-out selector cannot separate the oracle-70 core
from the rest, `R3` closes and the verdict becomes unconditional. If one can, the D89a route
reopens with a concrete, cheap, prospectively testable candidate — and Route A's Phase 3 should
not start before that is known.

---

## 9. Recommendation (advisory; the owner signs)

`[INFERRED]` Do not revive D89a as a candidate line. Do not restart Route A implementation either.
Sequence:

1. **Run U4** (read-only, hours, no host game, no fresh maps). It resolves the only live
   repairability question and it is cheap.
2. **Route A Phase 1 in parallel** (measurement repair) — it is the only work in either line that
   is unblocked, zero-risk, and unambiguously valuable regardless of which line survives, and it
   must add the schedule/opponent-production invariant class the coordinator identified as a
   structural blind spot: *"a future design can satisfy all 29 invariants, pass D-6, and still
   lose in exactly the way that killed the best banana mechanism we have built."*
3. **Do not open Route A Phase 2/3 until U4 returns.** Phase 2 invalidates every baseline and the
   resident's Arena qualification; committing to it while the cheaper question is open is the
   wrong order.
4. If U4 closes negative, record D89a's closure in `CONSTRAINTS.md` as the **fourth and fifth**
   confirmations of the ★★★ production constraint — the August `b100_e6` composition (leak ratio
   `1.130`) and the bounded-ring smoke (`1.822` exchange rate, margin `+7.44 -> -18.75`) are both
   confirmations that the standing entry does not yet cite — and treat the banana-production
   direction as terminal for this architecture.
5. Regardless of U4: the `CONSTRAINTS.md` ★★★ entry's reopening condition ("*do not reopen
   production without first changing harvest capability **AND** demonstrating denial is
   preserved*") should be amended to record that D89a satisfied the first conjunct in full
   (10,729 harvests, 252/256 sustained) and still failed — so the binding half is **denial
   preservation**, and no future proposal should be accepted on harvest capability alone.

---

## Appendix A — reproduction scripts

All scripts read only the committed discovery JSON
(`d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a`).

```bash
git show origin/main:data/analysis/live-agent-6553250/\
d89a-banana-seed-factory-discovery-result-2026-07-21.json > d89a.json
sha256sum d89a.json
```

**A.1 — headline recomputation and family table (§2.1)**

```python
import json, statistics, math
from collections import defaultdict
P = json.load(open('d89a.json'))['pairs']
m = lambda f: statistics.mean(f(x) for x in P)
print(m(lambda x: x['delta']['margin']),        # 79.441406
      m(lambda x: x['delta']['score']),         # 162.304688
      m(lambda x: x['delta']['opponent_score']),# 82.863281
      m(lambda x: x['delta']['owned_chop_wood']))# 40.648438
fam = defaultdict(list)
for x in P: fam[x['opponent']].append(x)
for k in sorted(fam):
    g = fam[k]
    print(k, len(g),
          statistics.mean(y['delta']['margin'] for y in g),
          statistics.mean(y['delta']['score'] for y in g),
          statistics.mean(y['delta']['opponent_score'] for y in g),
          min(y['delta']['margin'] for y in g),
          sorted(y['delta']['margin'] for y in g)[math.floor(0.10*(len(g)-1))])
```

**A.2 — correlations (§3.2)**

```python
def corr(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x-ma)**2 for x in a)); db = math.sqrt(sum((y-mb)**2 for y in b))
    return num/(da*db)
y = [x['delta']['opponent_score'] for x in P]
for k in ('harvest_successes','renewable_plant_successes','trained_role_rewrites',
          'tracked_live_crops','shadow_divergence_turns','activation_turn'):
    print(k, corr(y, [x[k] for x in P]))
for k in ('score','plants','own_crop_harvest','owned_chop_wood'):
    print('delta.'+k, corr(y, [x['delta'][k] for x in P]))
```

**A.3 — oracle activation restriction (§4.3.1)**

```python
core = sorted([x for x in P if x['delta']['margin'] >= -60],
              key=lambda x: x['delta']['opponent_score'])
best = max(k for k in range(1, len(core)+1)
           if statistics.mean(x['delta']['opponent_score'] for x in core[:k]) <= 1.0)
sub = core[:best]                       # best == 70
print(best,
      statistics.mean(x['delta']['opponent_score'] for x in sub),   # +0.829
      statistics.mean(x['delta']['margin'] for x in sub),           # +129.957
      len({x['opponent'] for x in sub}), sorted({x['seat'] for x in sub}),
      len({x['seed'] for x in sub}))                                # 8, [0,1], 15
sel = {(x['seed'], x['seat'], x['opponent']) for x in sub}
byseed = defaultdict(list)
for x in P:
    byseed[x['seed']].append(x['delta']['margin']
                             if (x['seed'], x['seat'], x['opponent']) in sel else 0)
means = [statistics.mean(byseed[s]) for s in sorted(byseed)]
ctr = statistics.mean(means)
rad = 1.959963984540054*statistics.stdev(means)/math.sqrt(len(means))
print(ctr-rad, ctr+rad)                 # +14.248, +56.822
```

**A.4 — tail-only oracle abstention (§4.0)**

```python
S = sorted(P, key=lambda x: x['delta']['margin'])
for k in (0, 16, 32, 48, 64, 80, 96):
    sub = S[k:]
    fam = defaultdict(list)
    for x in sub: fam[x['opponent']].append(x['delta']['margin'])
    print(k, len(sub),
          sorted(x['delta']['margin'] for x in sub)[math.floor(0.10*(len(sub)-1))],
          min(x['delta']['margin'] for x in sub),
          min(statistics.mean(v) for v in fam.values()),
          statistics.mean(x['delta']['opponent_score'] for x in sub),
          statistics.mean(x['delta']['margin'] for x in sub))
```

**A.5 — rate-limit disjointness (§4.1)**

```python
own, opp, marg = 162.304688, 82.863281, 79.441406
print(1.0/opp,  (1.0/opp)*own,  (1.0/opp)*marg)   # k<=0.01207 -> own +1.96, margin +0.96
print(4.0/marg, (4.0/marg)*opp)                   # k>=0.05035 -> opp +4.17
```

**A.6 — ring/factory paired smoke deltas (§4.2.1, §4.4.1)**

```bash
git show origin/main:data/analysis/live-agent-6553250/\
banana-ring-b100-smoke-20260802T-r5.json > ring.json
sha256sum ring.json   # 3b8e596d837b1fd1549975ea84a13d8f8e36964d3365610e3ed0d955e7e35818
```

```python
import json, statistics
A = json.load(open('ring.json'))['arms']
base = {(r['seed'], r['seat']): r for r in A['fallback_b100_e6']['rows']}
for name in ('fallback_b100_e6', 'live_unbounded_factory', 'bounded_ring'):
    rows = A[name]['rows']
    do = statistics.mean(r['score'] - base[(r['seed'], r['seat'])]['score'] for r in rows)
    dp = statistics.mean(r['opponent_score']
                         - base[(r['seed'], r['seat'])]['opponent_score'] for r in rows)
    dm = statistics.mean(r['margin'] - base[(r['seed'], r['seat'])]['margin'] for r in rows)
    print(name, statistics.mean(r['margin'] for r in rows),
          statistics.mean(r['score'] for r in rows),
          statistics.mean(r['opponent_score'] for r in rows), dm, do, dp, (dp/do) if do else None)
# fallback_b100_e6        +24.500 185.688 161.188   0.000    0.000    0.000    -
# live_unbounded_factory   +7.438 316.562 309.125 -17.062 +130.875 +147.938  1.130
# bounded_ring            -18.750 258.500 277.250 -43.250  +72.812 +116.062  1.594

u = {(r['seed'], r['seat']): r for r in A['live_unbounded_factory']['rows']}
rows = A['bounded_ring']['rows']
print(statistics.mean(r['margin']         - u[(r['seed'], r['seat'])]['margin'] for r in rows),
      statistics.mean(r['score']          - u[(r['seed'], r['seat'])]['score'] for r in rows),
      statistics.mean(r['opponent_score'] - u[(r['seed'], r['seat'])]['opponent_score']
                      for r in rows))
# ring vs unbounded factory: -26.188  -58.062  -31.875  => 1.822 own per opponent point
```
