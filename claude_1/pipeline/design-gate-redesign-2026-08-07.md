# Acceptance-gate re-design proposal

- Author: `claude_1` (fable)
- Date: 2026-08-07
- Status: **PROPOSAL — for cross review.** Not implemented. Nothing here changes the
  gate until reviewers and the owner accept it.
- Scope: `claude_1/pipeline/fuzz_panel.py` (the panel/verdict layer) and the tiering of
  `claude_1/banana-restoration-r2/trace_detectors.py` (the detector layer).
- Supersedes as a design: the round-6 "ROOT-A" D-9 parent-differential rule (already
  removed) and the D-1 inherited-report-only rule (already removed).

---

## 1. Why re-design instead of continuing to patch

Three consecutive candidate cycles were adjudicated by an instrument that could not
support the verdicts asked of it. The failures were not bad luck; they were the same
architectural defect surfacing three times.

Evidence, all re-run by me from committed tools (`claude_1/pipeline/verification/`,
commit `37050adc`), 240 games per run, parent
`a8eb3b2b…` (`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`):

| run | raw gate (repair #1) | raw + P4 calibration (repair #2) |
|---|---|---|
| **parent vs itself (the FLOOR)** | 223 / 240 | **118 / 240** |
| chatgpt_1 `bbe54a48` | 217 | **116** |
| chatgpt_1 tip `7ad9d784` | 221 | **146** |

Two facts drive this proposal.

**(a) The gate blocked its own reference implementation.** Under the raw rule the shipped,
arena-rated parent failed 93% of games, and *both* candidates scored better than it — the
instrument ranked a known regression above the bot it was supposed to be a regression
against. A gate that rejects its own baseline is a constant `BLOCK`: it carries no
information and cannot certify anything.

**(b) The dominant terms were measurement artifacts, not defects.** P4 counted the
post-completion coast to the sim horizon as a liveness stall — **198 of 204 stall windows
ended at turn 199**, the last turn. After calibration P4 dropped 204 → 30. D-9 blocks
**exactly 74 games in all three runs** — floor, `bbe54a48`, and tip alike — i.e. its
contribution to the verdict is insensitive to which bot is under test.

> **Units note (reconciliation, 2026-08-07).** Two correct counts of the same run differ by
> unit: **games** (report rows; a game blocks once however many episodes it contains) and
> **episodes** (the sum of per-game `count`). The coordinator's independently-run floor
> reports D-9 = 196 and D-1 = 35 in *episodes*; my 74 and 32 are the same runs in *games*.
> Both are right. Verified across all three runs:
>
> | detector | floor games / episodes | `bbe54a48` | tip `7ad9d784` |
> |---|---|---|---|
> | D-9 | 74 / 196 | 74 / 196 | 74 / **176** |
> | D-1 | 32 / 35 | 27 / 29 | 0 / 0 |
> | D-4 | 6 / 6 | 6 / 6 | 35 / 46 |
>
> This refines — and partly weakens — the claim in §5. D-9 is invariant in its **gating
> contribution** (74 games in every run, so it can never change an accept/reject decision),
> but it is *not* strictly invariant in episodes: the tip differs (176 vs 196). The
> zero-information argument therefore holds **for the verdict**, which is what the tier
> rule keys on, and not as a claim about the raw episode stream. Everywhere this document
> says "variance", it means variance in blocking games.

The prior parent-relative exemptions were not a bad rule so much as a *mask* over these
artifacts. Removing them (owner ruling, 2026-08-06) was correct and did its job: it made
the miscalibration visible instead of averaged away. But it also proved that raw-on-
everything is unsatisfiable, because the parent itself violates five detectors.

## 2. Root cause: three different questions gated by one mechanism

Each detector silently answers one of three incompatible questions:

1. **Safety** — "does the candidate violate an absolute invariant?" Parent-independent.
2. **Regression** — "did the candidate make things worse than the parent?" Inherently
   comparative; D-9's `train_late` clause *literally* compares to the parent's TRAIN turn.
3. **Calibration** — "is the harness measuring anything real?" Never asked at all.

The gate applied one uniform attribution rule to all three. Under the old mixed rules,
question 2 leaked into question 1 as invisible exemptions (which is where fabricated
verdicts could hide). Under the raw rule, question 1's rule was applied to question-2 and
question-3 detectors, which made the gate unsatisfiable. **Neither rule is wrong; applying
either one uniformly is.**

A further defect: several detectors use a *proxy* that assumes a causal link, and the link
is false on this lineage. D-9's unpaired clause treats "PLANT/PICK BANANA before TRAIN"
as evidence that banana displaced the TRAIN. The shipped parent does its own pre-TRAIN
banana funding and trains anyway, so the proxy fires on a bot that displaces nothing.

## 3. Design principles

- **P1. The baseline is measured, never assumed.** Every gate run measures the parent
  against itself and reports it. No verdict exists without its floor.
- **P2. A detector's tier is assigned by evidence, not by opinion.** Its floor count and
  its variance across candidates determine how it may gate.
- **P3. No invisible masking.** Any tolerance is a finite, enumerated, hash-pinned,
  owner-ratified list — never a runtime "the parent also failed, so skip it."
- **P4. A detector that cannot discriminate cannot gate.** Zero variance ⇒ zero
  information ⇒ report-only.
- **P5. Proxies are banned in blocking tiers.** A blocking detector must test the thing
  itself (world state), not a correlate of it.
- **P6. Tolerance is debt, not a resting state.** Every tolerated floor violation carries
  an owner, a cause, and a disposition.

## 4. Proposed architecture

### 4.1 The Floor Self-Test (FST) — mandatory

Every gate invocation runs the parent as its own candidate and emits per-detector floor
counts. It is not optional and not cacheable across tool changes: the FST is keyed by
(parent sha256, detector-module sha256, config sha256, seed set). If the FST does not
reproduce its pinned baseline, the run aborts as **HARNESS DRIFT** — no verdict. This
catches the class of change where a detector edit silently moves the goalposts.

### 4.2 Detector tiers

| tier | definition | gating rule |
|---|---|---|
| **A — absolute** | floor = 0 and demonstrably exercised | any candidate episode BLOCKS, raw, no tolerance |
| **B — lineage-violated** | floor > 0 and variance > 0 across candidates | BLOCKS on **per-map delta > 0** vs the pinned floor, minus ratified waivers |
| **Q — quarantined** | variance = 0 across candidates, or floor > 0 with no ratified cause | report-only; may never contribute to a verdict |
| **U — unexercised** | floor = 0 **and** zero episodes on every candidate | report-only, and flagged as **unproven** — see 4.5 |

Tier is recomputed by the tool from the FST each run and printed in the verdict. A
detector cannot be assigned a tier by hand.

### 4.3 Current classification from measured data

All counts are **blocking games** (see the units note in §1); episodes in parentheses.

| detector | floor | `bbe54a48` | tip | variance | tier |
|---|---|---|---|---|---|
| D-9 second-worker TRAIN displacement | 74 (196) | 74 (196) | 74 (176) | **0 games** | **Q** |
| D-1 A→B→A movement | 32 (35) | 27 (29) | 0 (0) | yes | B → **see §6a** |
| D-4 abandoned carried wood | 6 (6) | 6 (6) | 35 (46) | yes | B → **see §6a** |
| D-6 opponent-favored fruit | 9 (15) | 9 (15) | 0 (0) | yes | B |
| D-5 unbounded planting | 1 (1) | 1 (1) | 0 (0) | yes | B |
| D-7 lost harvested fruit | 0 (0) | 2 (2) | 35 (67) | yes | **A** |
| D-2 repeated PICK/DROP | 0 | 0 | 0 | 0 | **U** |
| D-3 same-target contention | 0 | 0 | 0 | 0 | **U** |
| D-8 diagonal-mother chop | 0 | 0 | 0 | 0 | **U** |
| P4 liveness (calibrated) | 30 | 25 | 79 | yes | B |
| P2 asset survival | 4 | — | — | tbd | B |
| P3 orchard byte-inertness | 0 | 0 | 0 | n/a | **A** (absolute by construction) |

D-7 is the model Tier-A detector: zero floor, and it discriminates hard (0 / 2 / 35). It is
the only detector currently earning an unconditional block.

### 4.4 The waiver ledger (replaces runtime parent-comparison)

Tier B needs *some* tolerance or it is unsatisfiable. The proposal is deliberately **not**
the banned mechanism. The distinction is the whole point:

- **Banned (old):** at runtime, if the parent also failed this episode, skip it. Unbounded,
  invisible, recomputed every run — and precisely where a fabricated CLEAR could hide.
- **Proposed:** `claude_1/pipeline/waiver-ledger.json` — a finite, enumerated list of known
  parent defects keyed by `(seed, map_id, detector, episode_signature)`, each with a cause,
  an owner, and a ratification reference. Anything not on the list blocks raw. The ledger is
  hash-pinned into every verdict, append-only, and reviewable in one sitting.

A new defect cannot hide in an enumerated list the way it can hide in a runtime rule. This
keeps the owner's intent — no invisible masking — while making the gate satisfiable.

### 4.5 Unexercised detectors are not passing detectors

D-2, D-3, D-8 never fire, on anything. That is **not** evidence they are clean; it is
evidence they are untested (failure class `UNSAMPLED_STATE_SPACE`, already in the ledger).
Each Tier-U detector needs one adversarial map that provably triggers it, committed as a
bite-test. Until then the verdict must print them as `UNPROVEN`, never as `PASS`. A gate
that reports green from a detector that has never fired is how we got here.

### 4.6 Verdict rule

```
ACCEPT  iff  FST reproduces pinned baseline           (else HARNESS DRIFT)
        and  every Tier-A detector: 0 episodes
        and  every Tier-B detector: per-map delta <= 0 vs floor, modulo ratified waivers
        and  P3 orchard inertness holds
        and  no Tier-A/B detector is in tier U (unproven) without an owner exception
Tier Q  reported, never blocking.
```

Aggregate counts never decide; **per-map delta** does. Aggregates let a candidate hide a
new failure on map X behind a fixed failure on map Y.

### 4.7 Anti-fabrication provenance

Every verdict emits a manifest: parent sha256, candidate sha256, detector-module sha256,
config sha256, waiver-ledger sha256, tool sha256, seed set, per-detector floor counts,
per-detector candidate counts, per-map deltas. A CLEAR lacking its floor run or its
manifest is **structurally invalid** and must be rejected on sight. This is a direct
response to the 2026-08-06 fabricated-CLEAR incident: the reviewer no longer has to trust
the claim, because the claim cannot be stated without the evidence that refutes it.

## 5. The D-9 fix (referred, not applied)

D-9's unpaired clause should test the causal claim it is making: fire only when a TRAIN was
**affordable at that turn** and the bot spent on banana instead. That is world-state
grounded, parent-independent, and consistent with the raw ruling. Expected effect: floor
74 → near 0, promoting D-9 from Q to A or B.

I have **not** implemented this. `trace_detectors.py` is a shared acceptance artifact the
integrator runs as a host gate, and it encodes spec invariants I-16..I-18; changing it
changes what every agent's gate accepts. Detector semantics are integrator/owner scope by
standing convention. Referred here for decision.

## 6a. Self-reported incompatibility with the standing strict rule

The coordinator's policy `20260807T093500Z` requires any proposal element that would weaken,
waive, or reclassify **D-1** or **D-4** to be reported as incompatible rather than argued.
**One element of this proposal does exactly that, and I am flagging it against my own work:**

§4.3 classifies D-1 (floor 32 games) and D-4 (floor 6 games) as **Tier B**, which would gate
them on per-map delta against the floor and permit ratified waivers. Under owner ruling
2026-08-07 (raw `D-1 == 0`, `D-4 == 0`, no inherited-parent or aligned-prefix exemption)
that classification is **not available**. The tiering machinery is descriptive — it reports
what the evidence shows — but it does not have the authority to place D-1 or D-4 anywhere
that tolerates a nonzero count.

**Resolution adopted here, pending review:** D-1 and D-4 are **carved out of Tier B by
ruling**. They gate raw at zero, no waiver-ledger entry may reference them, and the FST
reports their floor purely as a *repair backlog*, not as a tolerance. Tier B therefore
applies only to detectors the strict rule does not name (D-5, D-6, P4, P2). The rest of the
architecture — floor self-test, evidence-assigned tiers, per-map delta, verdict manifest,
UNPROVEN reporting — is unaffected and remains compatible with the strict rule.

The consequence is the one the owner has already accepted: **the parent lineage must be
repaired.** Reaching raw D-1 = 0 and D-4 = 0 on delivered bytes means eliminating the
parent's own 32 D-1 games (35 episodes) and 6 D-4 games (6 episodes) — work on the inner
policy, not on the banana wrapper. Scoping that honestly is a separate deliverable I owe as
work owner, and an infeasibility finding on the current parent is an admissible outcome.

## 6. What this does NOT change

- No detector predicate is weakened. Tiering changes *how a detector may gate*, never what
  it detects.
- P3 orchard byte-inertness stays absolute (candidate == parent commands on orchard-eligible
  maps). It is a requirement, not an exemption.
- The owner's raw ruling stands for Tier A and for everything outside the enumerated ledger.
- No candidate is retroactively accepted. Under this design both `bbe54a48` and
  `7ad9d784` still fail (tip: +28 net maps worse than parent).

## 7. Open questions for reviewers

1. **Is the waiver ledger meaningfully different from what was banned?** I argue yes
   (finite, enumerated, hash-pinned, ratified vs unbounded, invisible, runtime). This is the
   proposal's load-bearing claim and the one I most want attacked. **Scope after §6a:** the
   ledger may never reference D-1 or D-4, so the question is whether it is defensible for
   the detectors the strict rule does not name (D-5, D-6, P4, P2) — or whether, once D-1/D-4
   are carved out, it earns too little to justify the mechanism at all. A verdict of
   "drop the ledger entirely" is a legitimate review outcome.
2. **Should Tier B gate on per-map delta ≤ 0, or strictly = 0 (no new failure anywhere,
   ever)?** Delta ≤ 0 permits trading a failure on map X for a fix on map Y.
3. **Who owns `trace_detectors.py` changes** — and is the D-9 affordability fix in scope for
   me, for the integrator, or for a joint round?
4. **Is the 240-game panel the right sample** for per-map delta, given Tier-U detectors show
   it does not exercise D-2/D-3/D-8?
5. **Does the FST belong in `pre_review.py` too**, making it impossible to hand off without
   a floor run?

## 8. Acceptance criteria for this re-design

The re-design itself is only accepted when it demonstrates, on committed evidence, that:

1. the FST reproduces a pinned floor for an unchanged parent;
2. tiers are computed from data, and D-9 lands in Q without anyone naming it;
3. an injected synthetic regression (a deliberately broken candidate) is BLOCKED, and the
   unmodified parent is ACCEPTED — the two-sided test the current gate fails;
4. every Tier-U detector has a bite-test that fires;
5. a verdict without a manifest is rejected by the tool.

Criterion 3 is the one that matters: **the gate must accept the parent.** No instrument
that rejects its own baseline is fit to adjudicate a successor.
