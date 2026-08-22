# Item 11 — adversarial review of the D89a leak-repairability verdict revision

- Reviewer: `claude_1` (adversarial reviewer role, Phase 1 item 11)
- Date: 2026-08-08
- Mode: **ANALYSIS ONLY.** No host run, no `cargo`, no simulator, no Arena, no CI, no detector /
  gate / bot / candidate edit. One new file. `python3` arithmetic over committed bytes plus
  `git show` / `git ls-tree` / `git log` / `sha256sum`.
- Target under attack: the concession appended to
  `claude_1/banana-restoration-r2/d89a-leak-repairability-2026-08-07.md`
  (§ "VERDICT REVISION", lines 1324-1374), which withdrew `NOT_REPAIRABLE` in favour of
  `UNRESOLVED, leaning NOT_REPAIRABLE` after
  `chatgpt_1/d89a-leak-repairability-review-2026-08-07.md`.
- The verdict under attack is my own, and so is the concession. Nothing below is softened for that
  reason.

## Summary of verdicts

| # | claim under attack | verdict |
|---|---|---|
| 1 | "U4 is decisive and cheap; an already committed pre-treatment snapshot supports it" | **REVIEW REFUTED** |
| 2 | The 70/256 core is a live target for a learnable selector | **REVIEW REFUTED** (existence holds; learnability is closed by arithmetic) |
| 3 | D92 closes only the exact late target-selection policy | **REVIEW UPHELD** (narrowly); the concession's *scope* was too wide |
| 4 | Conditional activation escapes the D-1/D-4 barriers | **REVIEW UPHELD** in conclusion; `claude_1`'s stated reason **REFUTED** as factually wrong |
| 5 | other load-bearing findings | two corrections, one in each direction |

**Recommended disposition: restore `NOT_REPAIRABLE`** for the exact leak against the exact `<= +1`
gate, with R3 reclassified from "live but unrun" to "closed by measurement precision", and U4
reclassified from "cheapest open question" to "requires a fresh host panel and cannot return a
positive result at any confidence".

---

## 0. Provenance

```bash
cd /home/tarstars/prj/troll_farm-claude_1
git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*'
```

| input | ref | SHA-256 |
|---|---|---|
| `chatgpt_1/d89a-leak-repairability-review-2026-08-07.md` | `origin/agent/chatgpt_1` | `f539835bd1db1f8e1820f5437257cb0628d563282125543afaf15258420e0f57` |
| `d89a-…-discovery-result-2026-07-21.json` | `origin/agent/local_codex_1` | `d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a` |
| `d89a-…-result-2026-07-21.md` | `origin/agent/local_codex_1` | `1762ccb16e89bf1a118088759bdfb7c3672ee6b252872eb8a5f4a8e7bc8d8b52` |
| `d89a-…-blueprint-2026-07-21.md` | `origin/agent/local_codex_1` | `c3956d3bf33e51fb6a8a9b398a69bcdeea74b66c952eff1ced5144e200fbab04` |
| `d89a-…-protocol-2026-07-21.md` | `origin/agent/local_codex_1` | `65bb19bf438848c6f10cfb974a5687f4277eb4527fc63e8b0ef813714486af06` |
| `d89a-…-freeze-2026-07-21.json` | `origin/agent/local_codex_1` | `c8ecfb77538844c40c4f73282af4f46401f67d396dc9fecc22f2d90b011ddde1` |
| `d92-factory-dual-value-result-2026-07-21.md` | `origin/agent/local_codex_1` | `0e5084a05e65002b95d469d0e6e2da1c82d43549d0a7d9051646bf2eb6812f6c` |
| `d91-factory-activation-selector-result-2026-07-21.md` | `origin/agent/chatgpt_1` | `c52b94c9025f9adcf424e4b38c1dc404ff89ef8281fb064d93acd85e9605750d` |
| `d91c-factory-activation-selector-protocol-2026-07-21.md` | `origin/agent/chatgpt_1` | `36ee7cd9b15306cb80f5451236e6c95fbc979aae732814cab3fe037ac6019449` |
| `d91d-bootstrap-support-correction-protocol-2026-07-21.md` | `origin/agent/chatgpt_1` | `17925e71b1ad93e13c94fae58d134347ea3cf1846d9b608c8f84daec95cc7582` |
| `cgauto/analyze_d91c_factory_activation_selector.py` | `origin/agent/chatgpt_1` | `ac00ada65a54304fa139820c45d095e770eff52a348624131aadc2ad10e1c813` |
| `cgauto/analyze_d89a_banana_seed_factory.py` | `origin/agent/chatgpt_1` | `6a4bb8971310d74777ef1491a73f95e40d72e89bd0355eddac6983ca1c6c75c8` |
| `opponent-crop-suppression-2026-07-18.md` | `origin/agent/chatgpt_1` | `4c8bc864ef6cb4994f30cad17f25ce497ebfd4694b26bed972ab7192d0cd3a27` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | worktree | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |

Labelling: `[MEASURED]` = recomputed by me from committed bytes; `[INFERRED]` = my reasoning over
measurements; `[UNRESOLVED]` = cannot be settled from committed bytes.

All arithmetic below is reproducible from `compute_item11.py` (reproduced in Appendix A) run against
the discovery JSON hash above.

---

## 1. "U4 is decisive and cheap" — **REVIEW REFUTED**

This was flagged as the highest-value check in the task, and it is where the review breaks.

### 1.1 What the review claims

> "U4 is also described as the cheapest open question in either route: an offline map-held-out
> classification experiment over an **already committed pre-treatment snapshot** and committed
> labels, with no controller or host game required." (review, R2)

and

> "Use the **already committed D91 pre-treatment snapshot** and the oracle-safe labels, without
> changing any controller or running a host game." (review, "Required next step")

My own §8 U4 row says the same thing: "the labels are in the committed JSON and **the snapshot
exists**."

### 1.2 What the snapshot actually is `[MEASURED]`

The "activation snapshot" is not a file. It is three **TSV columns** consumed by the D91c analyzer:

```python
# cgauto/analyze_d91c_factory_activation_selector.py, selector_predicate()
row["banana_factory_activation_plants"]        <= 20
row["banana_factory_activation_fruits"]        >= 27
row["banana_factory_activation_banana_plants"] >= 6
```

The analyzer takes `--input-a` / `--input-b` TSV paths (`main()`, `argparse`), and D91c's protocol
(`36ee7cd9…`, line 30) instructs the *runner* to "Record the decision, pre-decision snapshot,
activation/mechanism telemetry…" — i.e. the snapshot is produced by a host panel run into a TSV row,
exactly like the opponent-provenance columns the review correctly declares missing in its own A2.

### 1.3 The snapshot is not committed anywhere `[MEASURED]`

```bash
# every file ever ADDED matching d89a or d91, across all 55 refs
git log --all --diff-filter=A --name-only --pretty=format: -- '*d91*' '*d89a*' | sort -u
```

returns exactly 22 paths: two analyzers, two analyzer tests, five `d89a-*` documents, three
`d91*` documents, and ten `coordination/` task/message files. **No panel TSV, no snapshot JSON,
no per-task pre-treatment rows.**

```bash
# every committed .tsv on every ref
for b in $(git branch -r | grep -v HEAD | sed 's/^ *//'); do
  git ls-tree -r --name-only $b 2>/dev/null | grep -iE '\.tsv$'; done | sort -u | wc -l
# 56
```

All 56 belong to `local_codex_1/e7a-*`, `local_codex_1/r36-simplified-arena`, or
`data/shared-lfs/d172a-option-corpus`. None is a D89a or D91 panel.

```bash
for b in origin/main origin/agent/chatgpt_1 origin/agent/local_codex_1 origin/agent/claude_1; do
  git grep -l 'banana_factory_activation_plants' $b --; done
```

hits only `cgauto/analyze_d91c_factory_activation_selector.py`,
`rust/src/bin/ownership_aware_complete_economy.rs` and
`tests/test_analyze_d91c_factory_activation_selector.py` — **source code on every ref, data on
none**. There is also no D91 result JSON at all: D91 exists only as a 39-line markdown result with
no per-task rows.

Independent host check: `/media/tarstars` does not exist (`ls: cannot access '/media/tarstars'`),
and a filesystem sweep of `/home/tarstars` for `*9914*`, `*d91*development*`,
`*d89*development*`, `*banana_factory_activation*` (excluding `.git`) returns nothing.

### 1.4 Consequence — the review's central reason for `UNRESOLVED` collapses

`[MEASURED]` The D91 snapshot is in the **same missing artifact family** as the provenance TSVs of
the `+12.453` / `+76.508` split. The review's A2 accepts that family is gone; its R2 then builds
its whole case on a member of it. My own document contains the identical contradiction: §8's U1
paragraph proves the panel rows "were never committed on any of the 52 refs", and the U4 row four
lines below asserts "the snapshot exists".

`[MEASURED]` Therefore U4 as specified requires a **fresh host panel run** — 512 rows, two profiles,
16 maps × 2 seats × 8 opponents — to regenerate the pre-decision snapshot. That is the same cost
class as U5, not "hours, read-only". Every one of the review's stated cost properties is false:
"no host game required" (false), "cheapest open question in either route" (false — it is tied with
U5), "offline experiment over committed data" (false).

`[INFERRED]` It is worse than a straight rerun. My §8 already records that the panel binary now
emits 240 columns against the frozen 140 (48 `worker3_*`, 14
`banana_factory_worker_three_bridge_*`, others). A regenerated snapshot cannot be certified against
the freeze, and whether the regenerated per-task rows still align to the frozen oracle labels by
`(seed, seat, opponent)` is itself unverified.

**Claim 1 verdict: REVIEW REFUTED `[MEASURED]`.** The snapshot does not exist in committed form.
The review's R1 argument — "an inexpensive unrun experiment that can reverse the answer means the
evidence is unresolved" — loses its first conjunct outright. §2 removes the second.

### 1.5 The version of U4 that *is* cheap has now been run, and returns a null `[MEASURED]`

There are exactly **two** genuinely pre-treatment quantities in the committed discovery JSON. The
protocol (`65bb19bf…`, integrity gate 2) requires "zero candidate/shadow mismatch before the first
observed two-worker activation", and the panel measures `preactivation_mismatches == 0` on all 256
pairs, so anything fixed at or before activation is admissible:

| feature | distinct values | range | r with Δopponent | r with Δmargin |
|---|---:|---|---:|---:|
| `activation_turn` | 7 | 2..27 | **`+0.0185`** | `+0.1169` |
| `initial_budget` | 8 | 2..9 | **`-0.0653`** | `+0.0156` |

Everything else in a pair record (`bootstrap_*`, `harvest_*`, `renewable_plant_*`,
`tracked_live_crops`, `reserve_*`, `shadow_divergence_turns`, `trained_role_rewrites`, and all of
`candidate`/`delta`) is post-activation outcome and is inadmissible as a selector feature.

I ran the map-held-out experiment the review asks for, on those two features, with exhaustive
interval-threshold search inside each training fold (leave-one-map-out, 16 folds, coverage floor
`n >= 8`, selection rule = maximise selected count subject to training-fold mean Δopponent `<= +1`,
thresholds never fitted on the held-out map):

```
features=('activation_turn',)                  : NO training-fold rule ever satisfied mean opp <= +1 with n>=8
features=('initial_budget',)                   : NO training-fold rule ever satisfied mean opp <= +1 with n>=8
features=('activation_turn','initial_budget')  : NO training-fold rule ever satisfied mean opp <= +1 with n>=8
```

**Not one admissible rule exists even in-sample on the training folds.** `[MEASURED]`

So the disjunction is closed on both horns: the 140-field U4 the review describes is not runnable
without a host panel, and the committed-data U4 that *is* runnable has been run and is null.

---

## 2. The 70/256 core — quantifying the optimism — **REVIEW REFUTED**

Both parties agree the core is post-selected and its interval descriptive. The task asks how much
optimism, and whether anything is estimable at that fold size. Both answers are worse than either
document assumes.

### 2.1 Reproduction `[MEASURED]`

The oracle subset reproduces exactly: k = 70, mean Δopponent `+0.8285714`, mean Δmargin `+129.957`,
15/16 maps, both seats, all 8 families. Panel-wide sd of Δopponent = **`88.402`**; range
`-61 .. +443`.

The subset also clears every gate in the lineage's own successor protocol D91c (`36ee7cd9…`), which
I checked because if it failed one, the branch would be dead trivially — it does not:

| D91c gate | requirement | oracle-70 | |
|---|---|---:|---|
| G2 selected margin / own | `>= +40` / `>= +60` | `+129.957` / `+130.786` | pass |
| G3 improve > regress, regr. rate | `<= 20%` | 57 / 0 / 13, `18.57%` | pass |
| G4 families nonneg / worst | `>= 6` / `>= -5` | 8/8, worst `+90.238` | pass |
| G5 selected p10 / worst | `>= -20` / `>= -60` | `-20` / `-56` | pass |
| G8 opponent/own ratio | `<= 0.40` | `0.0063` | pass |
| activation floor | `>= 32` selected | 70 | pass |

So the **existence** result is real and I do not attack it. (For completeness: 70 is below D89a's
own `>= 160` activation floor, but D91c already lowered that floor to 32 for an abstaining policy,
so that is not a barrier and I decline to present it as one.)

### 2.2 The oracle's own margin of safety is 0.171 points against a noise sd of 88.4 `[MEASURED]`

The subset is constructed by sorting on realized Δopponent and taking the longest prefix whose mean
is `<= +1.0`. Its mean is therefore pinned **at the constraint boundary by construction**: `+0.829`,
slack `0.171`. Its own dispersion is `sd = 15.127` inside the subset and `88.402` on the panel.

Confidence bounds on the oracle's own G8 quantity:

| basis | mean | SE | 95% upper bound |
|---|---:|---:|---:|
| i.i.d. over the 70 selected tasks | `+0.829` | `1.808` | **`+4.372`** |
| clustered over the 15 contributing maps | `+2.608` | `2.752` | **`+8.002`** |

`[MEASURED]` **Under the review's own pre-registration — R2/"Required next step" demands a "maximum
held-out mean opponent delta **and upper confidence bound**" — the perfect-hindsight oracle fails
its own test by 4.4x to 8.0x.** The map-clustered basis is the lineage's own inference standard
(D89a value gate 1 and D91c value gate 1 both use map-cluster 95% bounds). The oracle is the
unattainable ceiling on anything U4 could report. **The ceiling is below the bar the review set.**

### 2.3 What generalization to expect out of fold `[MEASURED]`

A selector covering 27.34% of tasks, ranking on a pre-treatment score with correlation `rho` to the
realized Δopponent, has expected selected mean (normal approximation, `mu = 82.863`, `s = 88.402`,
`z = -0.6024`, `lambda = phi(z)/q = 1.2169`):

```
E[selected mean] = mu - rho * s * lambda   =>   rho_required = (82.863 - 1) / (88.402 * 1.2169) = 0.7610
```

Empirical Gaussian-copula simulation against the **actual** 256-value distribution (1,500 draws per
point, seed 20260808) — no normality assumed on the outcome:

| `rho` | E[selected mean Δopponent] | P(mean `<= +1`) |
|---:|---:|---:|
| 0.311 | `+53.14` | 0.000 |
| 0.500 | `+36.41` | 0.000 |
| 0.600 | `+28.32` | 0.000 |
| 0.700 | `+20.73` | 0.000 |
| 0.800 | `+13.55` | 0.000 |
| 0.900 | `+6.97` | 0.000 |
| 0.950 | `+3.84` | 0.000 |

`[MEASURED]` **A pre-treatment predictor would need `|rho| >= 0.76` against a game outcome. Even
`rho = 0.95` never reaches the gate in 1,500 draws.** For scale: the largest correlation with
Δopponent anywhere in the committed record is `+0.311` (`harvest_successes`), and that is a
*post-treatment* variable — it is not usable by a selector. `rho = 0.311` yields `+53.1`, i.e.
53x the gate. The admissible pre-treatment features measured in §1.5 are at `+0.019` and `-0.065`.

### 2.4 Is anything estimable at map-held-out fold size? `[MEASURED]` — no

The panel is 16 maps × 16 tasks (16 seeds × 2 seats × 8 opponents). Leave-one-map-out gives a
held-out fold of **16 tasks**. Oracle-selected tasks per map:

```
[5, 6, 1, 12, 2, 6, 1, 3, 0, 14, 5, 3, 6, 1, 4, 1]     min 0, median 3.5, max 14
```

One map contributes **zero** selected tasks; five contribute one. With panel sd `88.402`:

| held-out selected n | SE of the fold's mean Δopponent | 95% half-width |
|---:|---:|---:|
| 1 | `88.4` | `173.3` |
| 3 | `51.0` | `100.0` |
| 4 (mean fold) | `44.2` | `86.6` |
| 70 (all folds pooled) | `10.6` | `20.8` |

The gate is `+1`. **The best achievable held-out precision, pooling every fold, is `+/-20.8` —
21x coarser than the quantity being gated; a typical single fold is 87x coarser.** No nested
validation, model family, or feature set changes this: it is the panel's information content.

`[INFERRED]` This makes U4 asymmetric in a way the review's decision rule does not allow for. The
review says "a selector that clears held-out safety while retaining material positive margin
supports `REPAIRABLE`; a well-powered failure … materially supports `NOT_REPAIRABLE`." A positive
result is unattainable — nothing can "clear held-out safety" at `+1` when the estimator's
half-width is `+/-20.8`. Only the negative arm of the decision rule is reachable. An experiment
that can only return one of its two answers is not a decision experiment.

**Claim 2 verdict: REVIEW REFUTED `[MEASURED]`.** The existence result stands; the *learnability*
branch is closed by measurement precision and by a required predictor correlation of `0.76` against
a corpus maximum of `0.311` on an inadmissible variable. `UNRESOLVED` is not a live branch here; it
is an unfundable one.

---

## 3. The D92 concession — **REVIEW UPHELD (narrowly); the concession was over-scoped**

I attacked my own retraction. It survives on the literal point and fails on scope.

### 3.1 The review's wording is correct `[MEASURED]`

`d92-…-result-2026-07-21.md:63-64` reads in full: "the trained worker reaches many nominal rival
crops but is **too late or too low-leverage to alter the rival's score**, so its existing productive
target order dominates." The 898/166 figure is a count of **nominal target selections**, and the
document itself declines to treat them as landed denial. The review's required wording — "exact D92
composition closed; broader denial-preserving scheduling strongly disfavoured but not proven
impossible" — is accurate. D92's own next-step sentence agrees: "The next experiment must change
**capacity or timing, not target weights**." Capacity was subsequently tested and failed (D94b/c,
exchange rate `4.791`). **Timing/scheduling was never tested for denial.** The narrow claim holds.

### 3.2 But the concession removed more than the review asked for `[MEASURED]`

My revision framed the 898/166 datum as "my strongest evidence" and treated its qualification as
collapsing the case. That over-corrects, because the "too late or too low-leverage" qualification
attaches **only to the trained-only arm**. Three measured results are untouched by it:

1. **D92's broad arm landed real denial.** 159/256 tasks changed; it "suppresses `13.883` opponent
   score per task, including `31.160` score-equivalent from opponent-created sources, but destroys
   `20.254` own score." That is not a late or low-leverage policy — the document's own conclusion is
   that "a broad controller **can** suppress rival-created production, but only by sacrificing even
   more of our production." Exchange rate `1.459`.
2. **An independent monotone dose-response on a different substrate.**
   `opponent-crop-suppression-2026-07-18.md` (`4c8bc864…`) sweeps ten denial profiles. Only the
   smallest dose passes gates; suppression rises with dose and own-score cost rises faster:
   `b100_e6` own `+0.744` / opp `-4.406` (pass) → `b250_e6` `-2.948` / `-10.642` → `b500_e10`
   `-7.294` / `-16.635` → `b500_e20` `-8.233` / `-17.031` (fail). The exchange rate degrades
   monotonically from `0.090` to `0.483` — **a 5.4x degradation across the measured dose range**,
   with 9 of 10 profiles failing family/tail gates.
3. **R2.1** — the `b100_e6` rule composed directly onto D89a in August produced leak ratio `1.130`,
   worse than D89a alone, margin `-17.062`.

`[INFERRED]` My §4.2 gave three reasons for disbelieving the linear 6x extrapolation of the broad
arm. Reason (a) — "denial efficacy collapses to zero as volume rises 5.4x" — is the one weakened by
the qualification, and the concession was right to drop it. Reasons (b) (55% substitution) and (c)
(tails degrade at 1x) stand untouched, and item 2 above is a *stronger, directly measured*
replacement for reason (a): the exchange rate is not merely non-improving with dose, it is measured
degrading monotonically over a 5x dose range on an independent panel.

**Claim 3 verdict: REVIEW UPHELD `[MEASURED]`.** The review's narrow wording is right and I do not
restore the over-general "denial does not buy the gate back". But the concession should not have
been recorded as knocking out the case's strongest evidence. **Correction required to the revision
text:** the strongest-evidence sentence must be re-stated on the broad arm + dose sweep + R2.1
composition, none of which carries the "too late or too low-leverage" qualification, and the net
effect on the `NOT_REPAIRABLE` lean is approximately nil. Denial *dose* is closed by three
independent measurements on two substrates; denial *timing* remains genuinely untested — but note
that a timing-only denial repair is a different intervention from anything U4 could authorise, so
it does not support `UNRESOLVED` for the R3/selector branch.

---

## 4. Conditional activation's D-1/D-4 escape — **REVIEW UPHELD in conclusion; the stated reason REFUTED**

The revision asserts conditional activation "uses no CHOP and does not bound the ring, so it escapes
both of the barriers that closed the other two mechanism-attacking repairs." I read
`detect_d1` (`trace_detectors.py:555-621`), `detect_d4` (`:757-826`) and `D4_BANNED_VERBS` (`:108`)
rather than assuming them.

### 4.1 The predicates, as written `[MEASURED]`

`D4_BANNED_VERBS = {"HARVEST", "CHOP", "PLANT", "MINE", "PICK"}` (line 108). `detect_d4` fires
`non_bank_verb` **immediately, with no slack**, on any of those five verbs inside a wood-committed
interval (line 799-802); commitment starts when `carry[WOOD] > 0` **and** (`free_capacity() == 0`,
or `MOVE <door>`, or `DROP` on a door) (lines 783-796); it ends only on a door DROP, death, cargo
loss, or unreachable door.

`detect_d1` fires on a **positional** two-cell alternation of an own unit for `>= 7` states
(`(t-1) - s >= 6`, line 605) with zero progress events (unchanged `carry`, unchanged own
`inventories[0]` on a DROP/PICK turn, no plant flip at the unit's cell). It is unit-positional; a
policy-level flip does not fire it unless it produces positional alternation.

### 4.2 The A→B→A oscillation concern does not apply `[MEASURED]`

D91c's frozen intervention text (`36ee7cd9…`, lines 24-28) reads: "Evaluate the three integer
predicates **once**, on the first state where worker two is observed. If all pass, run the exact
full D89 factory for the remainder of the game. Otherwise permanently retain the exact resident.
**Do not reevaluate**…". D91's implementation measured 256/256 decisions at the boundary with zero
preactivation mismatches.

`[MEASURED]` The selector is one-shot and latched. There is no predicate that can flip mid-game,
therefore no activation flapping, therefore no policy-level A→B→A. This matters because D91's
predicates are *dynamic* quantities (live plants `<= 20`, fruit on live plants `>= 27`, live BANANA
plants `>= 6`) and the factory itself adds `+35.688` mean plants per task — a *re-evaluated*
version of this exact predicate would be self-negating and would flip. The frozen design already
forecloses that. The review's R6 request for "hysteresis and avoid activation flapping" is
already satisfied by the design, and the task's oscillation hypothesis is not realised.

### 4.3 Abandoned carried wood at the switch point `[INFERRED]`

The switch occurs at the first observed two-worker state. If a unit is inside a wood-committed
interval at that instant and the new layer's first different command is a banned verb, D-4 fires
with no slack. The blueprint contains a structural mitigation I must record because it cuts against
my attack: starter rule 7 (`c3956d3b…`, line 24) — "**Carrying wood, iron, or a non-BANANA fruit
takes precedence and uses resident bank logistics**". The planting/harvesting role yields to
resident bank logistics whenever it carries wood, which is exactly the `carry[WOOD] == 0` discipline
my §5 demanded of R1. This is not proof (no trace of D89a exists), but it is a real design-level
mitigation and the switch-point risk is smaller than I expected when I started this check.

### 4.4 "Uses no CHOP" is factually false `[MEASURED]`

The controller that conditional activation switches *on* is D89a, and D89a's trained-worker role is
a CHOP role. Blueprint (`c3956d3b…`, lines 28-31): "After activation, accept only **CHOP**/MOVE
toward a nonprotected tree, RETURN/MOVE to the bank, DROP, or WAIT. A resident-selected PICK, PLANT,
HARVEST, or MINE is replaced with the best existing wood/bank candidate." Measured injection rate
over the 256 pairs:

| quantity | mean per task | min | max | tasks at zero |
|---|---:|---:|---:|---:|
| `trained_role_rewrites` | **`13.105`** | 0 | 34 | **1 / 256** |
| `harvest_successes` (starter) | `41.910` | — | — | — |
| `delta.plants` (starter) | `+35.688` | — | — | — |

`[MEASURED]` D89a forces the wood-carrying worker onto a chop/bank candidate a mean **13.105** times
per task, in 255 of 256 tasks. My §5 argument for declaring R2 "DEAD ON ARRIVAL" was: "Denial *is*
CHOP, and CHOP is in `D4_BANNED_VERBS`… one denial chop en route fires `non_bank_verb` on the spot
with no slack." That argument does not distinguish a denial chop from a factory chop. Applied
consistently it lands on D89a's own trained role.

`[INFERRED]` Two mitigations keep this from being fatal, and I state both: the rewrite *replaces*
PICK/PLANT/HARVEST/MINE (four banned verbs) with CHOP or a MOVE/DROP bank action, so its net effect
on banned-verb count is ambiguous rather than strictly additive; and D91c integrity gate 4 requires
"trained workers issue zero HARVEST/PLANT commands", so the two roles are verb-separated.

**Claim 4 verdict: REVIEW UPHELD in conclusion `[MEASURED]` — the branch is not killed by D-1/D-4;
the oscillation hypothesis is foreclosed by D91c's no-reevaluation rule.** But the revision's stated
reason is **REFUTED**: "uses no CHOP" is false of the controller being activated, at a measured
13.105 forced chop-candidate rewrites per task. The defensible statement is the weaker one:
*conditional activation adds no new D-1/D-4 exposure beyond D89a's own, which is unmeasured* — which
is the review's own A4, and A4 explicitly forbids using unknown compliance as evidence in either
direction. The revision used it as evidence for the live branch. That is not permitted.

---

## 5. Other load-bearing findings

### 5.1 The review is right and I was wrong on "repairs the gate, not the mechanism" `[MEASURED]`

My §7 wrote: "even if it succeeds it repairs the *gate*, not the mechanism: the controller would
still leak on the 186 tasks it abstains from running at all." The review's R2 answers: "On abstained
states D89a does not run, so there is no D89a-induced leak to 'still' occur there." **The review is
correct and my sentence is simply wrong.** An abstaining policy runs the resident on those 186
tasks, and the resident's Δopponent is 0 by construction. This finding cuts *for* the review and I
record it as such. It does not rescue the branch, because §1 and §2 close it on other grounds, but
the sentence in my §7 should be struck.

### 5.2 The review's R1 principle, restated against its own premises `[INFERRED]`

R1 argues: "An inexpensive unrun experiment that can reverse the answer means the evidence is
unresolved." Both conjuncts are now measured false — not inexpensive (§1.4: a fresh 512-row host
panel), and cannot reverse (§2.4: a positive result is unattainable at any confidence, and §2.2:
the perfect-hindsight ceiling already fails the review's own confidence-bound requirement). R1 does
not survive its own premises. Note that R1 is the *only* argument in the review that acts directly
on the headline verdict; R3-R6 are wording and methodology corrections that I accept in full.

### 5.3 Findings of the review that survive this attack unchanged

A1 (aggregate reproduces), A2 (the split is correctly retracted), A3 (seven repair classes closed),
A4 (raw D-1/D-4 unknown, and must not be used as evidence either way), R3 (post-selection discipline
for any future selector work), R4 (D92 wording), R5 (mechanism is partly `[INFERRED]`), R6 (raw-zero
as a mandatory later gate). I tried to break A3 by checking whether the oracle-70 fails any D91c
gate — it passes all of them (§2.1) — and I tried to break R4 by looking for a stronger reading of
D92 that generalises to schedules — the dose axis generalises, the timing axis does not (§3). Both
attempts failed and I report them as failures.

---

## 6. Recommended disposition

**Restore `NOT_REPAIRABLE`** for the exact D89a leak against the exact `<= +1` mean-opponent-score
gate, with the following scope statement replacing the current "VERDICT REVISION" section:

1. R3 (pre-treatment activation selector) moves from `UNRESOLVED, leaning NOT` to **closed by
   measurement precision**: a selector needs `|rho| >= 0.761` against a game outcome; the best
   correlation in the record is `+0.311` on an inadmissible post-treatment variable; the two
   admissible committed features are at `+0.019` and `-0.065` and no map-held-out rule on them
   exists even in-sample; and the panel cannot estimate the gated quantity to better than `+/-20.8`
   against a `+1` ceiling.
2. U4 is reclassified from "the cheapest open question in either route" to **"requires a fresh host
   panel run and cannot return a positive result at any confidence"**. It should not be run.
3. The D92 strongest-evidence sentence is re-stated on the broad arm, the ten-profile dose sweep,
   and the R2.1 composition, not on the 898/166 nominal-selection ratio (§3.2).
4. The §7 sentence "the controller would still leak on the 186 tasks it abstains from running at
   all" is struck as incorrect (§5.1).
5. The "uses no CHOP" escape claim is struck and replaced by A4's neutral statement: raw D-1/D-4 for
   this route is unmeasured and may not be cited as evidence in either direction (§4.4).
6. Denial **timing/scheduling** is recorded as the single genuinely untested axis (D92's own
   nomination), owned by U5, not by U4 — and it does not support `UNRESOLVED` for the selector
   branch.

**Strongest single piece of evidence:** the D91 pre-treatment snapshot is not committed on any of
the 55 refs. `git log --all --diff-filter=A --name-only -- '*d91*' '*d89a*'` returns 22 paths — two
analyzers, two tests, eight documents, ten coordination files, **zero data rows** — and all 56
committed `.tsv` files on all refs belong to `e7a`, `r36` and `d172a` corpora. The review's central
reason for `UNRESOLVED` rests on an artifact that does not exist, from the same missing family the
review itself correctly declares unrecoverable in its A2.

**Second-strongest, and the reason this is a closure rather than a deferral:** the perfect-hindsight
oracle — the unattainable ceiling on anything U4 could ever report — has a map-clustered 95% upper
bound of `+8.002` on the very quantity gated at `<= +1`, and its point estimate `+0.829` sits at the
constraint boundary by construction with `0.171` of slack against a per-task sd of `88.402`.

## 7. Boundary compliance

| forbidden action | performed? |
|---|---|
| edit of `pipeline/fuzz_panel.py`, `test_fuzz_panel.py`, `fuzz-panel-config.json` | NO |
| edit of `trace_detectors.py`, any bot/candidate/parent/`.min.rs`, any detector or gate | NO |
| host run, `cargo`, panel execution, TestSession, Arena, CI | NO |
| push to any branch other than the one deliverable commit | NO |
| modification of any existing repo file | NO — one new file only |

`trace_detectors.py`, `analyze_d91c_factory_activation_selector.py` and
`analyze_d89a_banana_seed_factory.py` were **read only**; their hashes are unchanged
(`59dce10d…`, `ac00ada6…`, `6a4bb897…`).

---

## Appendix A — reproduction

```bash
cd /home/tarstars/prj/troll_farm-claude_1
git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*'
git show origin/agent/local_codex_1:data/analysis/live-agent-6553250/\
d89a-banana-seed-factory-discovery-result-2026-07-21.json > d89a.json
sha256sum d89a.json   # d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a
```

**A.1 — absence proofs (§1.3)**

```bash
git log --all --diff-filter=A --name-only --pretty=format: -- '*d91*' '*d89a*' | sort -u
for b in $(git branch -r | grep -v HEAD | sed 's/^ *//'); do
  git ls-tree -r --name-only $b 2>/dev/null | grep -iE '\.tsv$'; done | sort -u
for b in origin/main origin/agent/chatgpt_1 origin/agent/local_codex_1 origin/agent/claude_1; do
  git grep -l 'banana_factory_activation_plants' $b --; done
ls /media/tarstars    # No such file or directory
find /home/tarstars -maxdepth 6 \( -name '*9914*' -o -name '*banana_factory_activation*' \) \
     -not -path '*/.git/*'      # empty
```

**A.2 — oracle subset, its confidence bounds, and fold structure (§2.1-§2.4)**

```python
import json, math, statistics
from collections import defaultdict
P = json.load(open('d89a.json'))['pairs']
opp = [x['delta']['opponent_score'] for x in P]
core = sorted([x for x in P if x['delta']['margin'] >= -60],
              key=lambda x: x['delta']['opponent_score'])
best = max(k for k in range(1, len(core)+1)
           if statistics.mean(x['delta']['opponent_score'] for x in core[:k]) <= 1.0)
sub = core[:best]                                     # 70
so  = [x['delta']['opponent_score'] for x in sub]
print(statistics.stdev(opp))                          # 88.40176146864837
print(best, statistics.mean(so))                      # 70  0.8285714285714286
se = statistics.stdev(so)/math.sqrt(len(so))
print(statistics.mean(so) + 1.959964*se)              # +4.3723   (iid 95% UCB)
byseed = defaultdict(list)
for x in sub: byseed[x['seed']].append(x['delta']['opponent_score'])
mm = [statistics.mean(v) for v in byseed.values()]    # 15 maps
print(statistics.mean(mm) + 1.959964*statistics.stdev(mm)/math.sqrt(len(mm)))  # +8.0015
cnt = defaultdict(int)
for x in sub: cnt[x['seed']] += 1
print([cnt[s] for s in sorted({x['seed'] for x in P})])
# [5, 6, 1, 12, 2, 6, 1, 3, 0, 14, 5, 3, 6, 1, 4, 1]
```

**A.3 — required predictor correlation (§2.3)**

```python
from math import erf, sqrt, exp, pi
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)));  phi = lambda z: exp(-z*z/2)/sqrt(2*pi)
mu, s, q = statistics.mean(opp), statistics.stdev(opp), best/len(P)   # 82.863, 88.402, 0.2734
lo, hi = -6.0, 6.0
for _ in range(200):
    mid = (lo+hi)/2
    lo, hi = (mid, hi) if Phi(mid) < q else (lo, mid)
z = (lo+hi)/2                                        # -0.6024
print((mu-1.0)/(s*phi(z)/q))                         # 0.7610
```

The Gaussian-copula simulation (§2.3 table) rank-transforms the empirical `opp` vector to latent
normals, draws `zx = rho*zy + sqrt(1-rho^2)*N(0,1)`, selects the 70 smallest `zx`, and reports the
mean of the corresponding `opp` values over 1,500 draws (`random.seed(20260808)`).

**A.4 — admissible-feature map-held-out selector (§1.5)**

Leave-one-map-out over the 16 seeds; inside each training fold, exhaustive search over all
`[lo, hi]` interval thresholds on `activation_turn` and/or `initial_budget`, keeping the rule of
maximum training-fold coverage subject to `n >= 8` and training-fold mean Δopponent `<= +1.0`; the
selected rule is then applied to the held-out map only. No fold produced any admissible rule.

**A.5 — D89a controller telemetry (§4.4)**

```python
print(statistics.mean(x['trained_role_rewrites'] for x in P))     # 13.10546875
print(sum(1 for x in P if x['trained_role_rewrites'] == 0))       # 1
print(statistics.mean(x['harvest_successes'] for x in P))         # 41.91015625
print(statistics.mean(x['delta']['plants'] for x in P))           # 35.6875
```
