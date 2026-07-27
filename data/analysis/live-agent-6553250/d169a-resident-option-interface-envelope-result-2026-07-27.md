# D169a — resident-native option interface: unified crop-safe envelope — result

Date: 2026-07-27
Verdict: **PASS** — mean envelope `+10.671` [+9.420, +11.922] clears every frozen B2.1 gate
(mean ≥ +10.0, clustered CI lower bound ≥ +5.0, ≥30% improved, no negative family, tails
not worse than CONTROL). Opens D170 authoring per the protocol's pre-adjudicated decision
tree; STOP Tier-2 work pending Fable adjudication.

## Reproducible execution

D169a evaluates exact resident (CONTROL) plus 13 bounded options on all 1,024 consumed
D148/D161 tasks: maps `9,844,136–9,844,199`, both seats, all eight frozen opponent
families — 14 policies × 1,024 tasks = 14,336 rows per run.

- **OPT_RETURN** reuses D168a's ARM_A ("post-return") BANK_SEED successor-option
  mechanism byte-for-byte (entry-detection, species tie-break, nearest-legal-plant-cell
  BFS, 24-turn horizon, abort set `{EMPTY_BANK_AT_PICK, NO_LEGAL_CELL, HORIZON}` plus the
  defensive `WORKER_MISSING`).
- **OPT_FRUIT / OPT_IRON / OPT_PROTECT** reuse D163's three resource-control components
  (F/I/P singly enabled, 32-turn horizon, shadow reserve `[3,3,2,0,3,0]`, no controller
  TRAIN) at D163's own fixed starts `72/104/136`, plus a new `TRIG` start (first turn the
  observed opponent worker count reaches ≥3) whose only new code is *when* to hand D163's
  own unmodified `ResourceConfig.start` to its own unmodified activation check — the
  reused component logic itself is untouched.
- Both the D162 bounded-option base machinery and (for OPT_FRUIT/IRON/PROTECT) the D163
  resource-control component logic are reused via the project's established `include!`
  composition pattern (D162 via the existing `build.rs`-generated include, unchanged) and
  literal, clearly-marked, unedited copies (D163's component mechanism, D168a's ARM_A
  logic, and D166/D167's underlying entry-detection bookkeeping) inside a new file,
  exactly mirroring the precedent D163/D167a/D168a themselves already established for
  reusing one another. No frozen module file was edited.

**Determinism.** The 1-thread (1,434.415 s) and 20-thread (168.992 s, 8.49×) runs are
byte-identical, SHA-256 `a51a64119a148f4855e29e474626f12c2fcb5924cb0d84161014ef8a68ec1762`
both directions, over the full 14,336-row matrix.

**CONTROL reproduces D161** exactly on all 20 shared terminal/score/workforce/crop/hash
fields for all 1,024 tasks (0 mismatches).

**Cross-validation against the frozen precedents it reuses** (not itself a protocol gate,
reported for confidence): OPT_RETURN activates on exactly the same 164/1,024 tasks as
D168a's own ARM_A (set-identical, not just count-identical), and every one of those 164
activated rows reproduces D168a's own own/opponent score and both hashes exactly
(0/164 mismatches) — confirming the ARM_A reuse is behaviorally byte-identical, not just
structurally similar.

**Integrity gates — all pass** (17/17; see `integrity` in the result JSON):

| Gate | Result |
|---|---|
| Schema exact (84 columns, both runs) | pass |
| Row count exact (14,336 both runs) | pass |
| Unique rows / full task×policy matrix exact | pass |
| 1-thread vs 20-thread byte-identical | pass |
| Reserved maps `9,844,200–9,844,215` excluded | pass |
| CONTROL reproduces D161 exactly | pass |
| Inactive `(task, arm)` pairs byte-exact vs CONTROL | pass |
| Resource arms' own workforce paired with CONTROL | pass |
| All games done; reward-identity error ≤ 1e-6 | pass |
| Zero provenance/vocabulary/purity/ambiguous-crop/controller-TRAIN failures | pass |
| CONTROL never activates; no double commit-and-abort; workforce cap ≤ 3 | pass |
| Frozen D162/D163/D167/D168 modules + build.rs + engine/state/mapgen/rl_macro unmodified (hash-verified against lock) | pass |

One methodological note surfaced during integrity verification and was resolved without
touching any frozen module or threshold: an initial, self-imposed workforce-parity check
compared *all* workforce fields (including `opponent_workers`) between CONTROL and every
resource arm. It failed on 97/12,288 checked rows — but only ever on `opponent_workers`,
never on `own_workers`/`max_own_workers`/`successful_trains`. This is the expected,
correct behavior of a genuinely causal intervention: the opponent is an independently
reacting bot that legitimately trains at different turns against a perturbed trajectory.
The check was narrowed to our own seat's workforce (D163a's actual claim — "a
workforce-independent comparison" — was always about our own seat), which then passes
0/9,216 mismatches. No frozen module was touched; only my own new diagnostic check's scope
was corrected before interpreting any value number, per protocol.

## Coverage gate

`>= 60%` of tasks must have `>= 1` armable option state, independent of value.

| Metric | Result |
|---|---:|
| Tasks with ≥1 arm activated (of 13 non-control arms) | 1,024 / 1,024 |
| Rate | 100.0% |
| Gate | **PASS** |

## Per-arm activation and value

Every individual fixed arm is negative on its own activated-subgroup mean (as D162a and
D163a already found for this vocabulary's fixed-policy form); the positive result below
comes entirely from the heterogeneous, per-task *envelope* selection, not from any single
arm being a viable standalone policy.

| Arm | Activated | Rate | Mean margin (active) | Improve/Regress (active) | Committed | Aborted |
|---|---:|---:|---:|---:|---:|---:|
| opt_return | 164 / 1,024 | 16.0% | −6.732 | 31 / 123 | 105 | 55 |
| opt_fruit_t072 | 1,024 / 1,024 | 100.0% | −3.653 | 360 / 462 | 0 | 1,022 |
| opt_fruit_t104 | 1,024 / 1,024 | 100.0% | −2.917 | 319 / 449 | 0 | 1,007 |
| opt_fruit_t136 | 1,014 / 1,024 | 99.0% | −2.980 | 267 / 424 | 0 | 961 |
| opt_fruit_trig | 182 / 1,024 | 17.8% | −9.489 | 65 / 86 | 0 | 180 |
| opt_iron_t072 | 1,024 / 1,024 | 100.0% | −6.169 | 291 / 619 | 0 | 1,024 |
| opt_iron_t104 | 1,024 / 1,024 | 100.0% | −6.360 | 269 / 619 | 0 | 1,016 |
| opt_iron_t136 | 1,014 / 1,024 | 99.0% | −5.763 | 234 / 605 | 0 | 984 |
| opt_iron_trig | 182 / 1,024 | 17.8% | −12.066 | 56 / 106 | 0 | 182 |
| opt_protect_t072 | 1,024 / 1,024 | 100.0% | −0.061 | 5 / 11 | 0 | 1,022 |
| opt_protect_t104 | 1,024 / 1,024 | 100.0% | −0.459 | 12 / 52 | 0 | 1,004 |
| opt_protect_t136 | 1,014 / 1,024 | 99.0% | −0.750 | 36 / 98 | 0 | 947 |
| opt_protect_trig | 182 / 1,024 | 17.8% | −0.104 | 2 / 3 | 0 | 181 |

`opt_return`'s 164/1,024 (16.0%) activation and its −6.732 activated-subgroup mean margin
exactly match D168a's own ARM_A measurement (cross-validated above). Note the resource
arms' "Aborted" counts routinely exceed "Activated" because `aborted` accumulates every
turn the horizon-deadline check fires after activation in this telemetry convention for
D163's own reused controller; this matches D163's own frozen module behavior and is not a
D169a-specific artifact — no resource arm's `committed` field is ever meaningful (D163's
components never train, by protocol design), which is why `committed = 0` throughout.

## Envelope result (14 policies: CONTROL + 13 arms)

Crop-safety filter: an `(task, arm)` result is envelope-eligible only if its own crop
creation is `>=` CONTROL's for that task (D169a's own stated D122 relative rule — a
stricter filter than D162a's own looser "not literally zero" version, implemented exactly
as D169a's protocol states it, not as D162a's precedent implemented it).

| Metric | Result | Frozen threshold | Gate |
|---|---:|---:|---|
| Mean envelope margin | **+10.671** | ≥ +10.0 | **PASS** |
| Median envelope margin | +5.000 | (descriptive) | — |
| Map-clustered normal 95% CI | **[+9.420, +11.922]** | lower bound ≥ +5.0 | **PASS** |
| Strict improvements / ties / regressions | 666 / 358 / 0 | ≥30% improved | **PASS** (65.04%) |
| Mean own-score / opponent-score delta | +4.970 / −5.701 | (descriptive) | — |
| Positive families / worst family | 8 / 8; **+5.141** (`resident`) | no negative family mean | **PASS** |
| Catastrophes (CONTROL / envelope selection) | 22 / 14 | ≤ CONTROL | **PASS** |
| Negative-margin mass (CONTROL / envelope selection) | 5,001 / 3,622 | ≤ CONTROL | **PASS** |

Regressions are structurally impossible by construction (the envelope always includes
CONTROL itself as a fallback selection), confirmed empirically at exactly 0/1,024.

**Per-family envelope means** (all eight positive; worst is `resident`, the hardest
opponent family in this project's standing finding):

| Family | Mean margin |
|---|---:|
| resident | +5.141 |
| script_boss | +8.016 |
| silver_boss | +9.898 |
| norx_native_three | +11.242 |
| legend_balanced | +11.422 |
| compact_gold | +11.750 |
| mybot | +13.312 |
| gold_adaptive | +14.586 |

**Per-arm selection counts** (which policy the per-task oracle picked; CONTROL itself
"wins" 358/1,024 tasks, i.e. no eligible arm improves on it there):

| Policy selected | Tasks | Policy selected | Tasks |
|---|---:|---|---:|
| control | 358 | opt_iron_t072 | 96 |
| opt_fruit_t072 | 187 | opt_iron_t104 | 72 |
| opt_fruit_t104 | 109 | opt_iron_t136 | 64 |
| opt_fruit_t136 | 87 | opt_iron_trig | 13 |
| opt_fruit_trig | 25 | opt_protect_t072 | 1 |
| opt_return | 10 | opt_protect_t136 | 2 |

1,021 of the 13,312 candidate `(task, arm)` pairs were excluded by the crop-safety filter
before this selection.

## Diagnostic (reported, not gated): TRIG + OPT_RETURN envelope only

The same envelope construction restricted to the four observable-trigger-armed arms
(`opt_return`, `opt_fruit_trig`, `opt_iron_trig`, `opt_protect_trig`) plus CONTROL — the
deployability-relevant subset, since the fixed `t072/t104/t136` starts are not themselves
an observable early-warning signal, just an always-available clock.

| Metric | Result |
|---|---:|
| Mean envelope margin | +1.801 |
| Median envelope margin | 0.000 |
| Map-clustered normal 95% CI | [+1.234, +2.368] |
| Strict improvement rate | 10.84% (111/1,024) |
| Worst family mean margin | +0.141 |
| Selection counts | control 913; opt_fruit_trig 48; opt_iron_trig 34; opt_return 27; opt_protect_trig 2 |

This diagnostic is positive but an order of magnitude below the full 14-arm envelope and
far below the +10.0/+5.0 thresholds — nearly all of the full envelope's edge comes from
the three always-on fixed-turn resource starts, not from the narrower, genuinely
observable-trigger-armed subset. This bears directly on what "deployable" means for
whatever D170 designs next; it is reported here exactly as the protocol requires,
descriptively, and is not part of the gate.

## Gate evaluation (frozen, exact protocol text)

- **PASS (opens D170 authoring):** mean envelope ≥ +10.0 AND clustered CI lower bound ≥
  +5.0 AND ≥ 30% of tasks improved AND no negative family mean AND catastrophes ≤ CONTROL
  AND negative-margin mass ≤ CONTROL. **All six conditions hold.**
- KILL (< +5.0 mean): not applicable (mean is +10.671).
- BORDERLINE (+5.0 ≤ mean < +10.0 or any single non-mean gate missed): not applicable —
  mean clears +10.0 and every non-mean gate also passes.

## Verdict (frozen rule)

**PASS.** Per the protocol's pre-adjudicated decision tree: record in ledger vol 2 + STATE
§4 as "READY FOR FABLE ADJUDICATION (D170 authoring)"; STOP Tier-2 work (cheap sessions may
run Tier-3 fillers). This experiment does not itself authorize D170, a candidate, Arena, or
submission — a PASS opens authoring, per protocol; the controller process integrates this
into the ledger/STATE/BACKLOG documents.

No selector or policy was fit on this run's outcomes; the envelope is reported as an upper
bound, not as labels, per the protocol's prohibitions. No frozen option parameter was
tuned, no fresh map was used, and no candidate/TestSession/Arena/submission/YT-write action
occurred.

## Reproducibility

- protocol: `a09af90724bfe739e8fe9bea0a2cfb165ba2db0518c1594b9741853969fc9a78`
- lock: `beaad47d6ef1f3d0ff9b63114d232fd9b6a648bfc03f1b0c6ee481eeb79980e4`
- Rust runner (`rust/src/bin/d169a_resident_option_envelope.rs`):
  `ec51121a1a49251f4a3ee001cbc2fe832179be7db7dba41ea247a8aa1862760a`
- analyzer (`cgauto/analyze_d169a_resident_option_envelope.py`): see result JSON
  `input_hashes` for the live re-hash at analysis time
- summary rows (jobs1 == jobs20, 14,336 rows):
  `a51a64119a148f4855e29e474626f12c2fcb5924cb0d84161014ef8a68ec1762`
- reference inputs (unchanged from their own freeze, reverified byte-for-byte before this
  run): D161 resident panel
  `144d8f880be8eb58e19e1ef0a3547c04280dac8644340628b60101c1c47c988b`; D162 runner
  `8c82a27191ecb999c945d969cd525afcd0073caaa1c2f5412cdca9d136879668`; D163 runner
  `08c669d60f2bc6681760e963070ff67e3d0157914cdde00bfbef65e88f94e7fc`; D167a runner
  `fdd0e985304e9fac8fc725c349141f472a941379eccfbd83b23b0497976a1032`; D168a runner
  `02efa8ff95f55b8e1bf24122cfd1ed7d5b2dab213ea45621ce074691e7884eb3`; `rust/build.rs`
  `e06e96bf7ba9f1b2a3eb99444a7cd380058e493f4377a0116f13d287921e5c6f`.

Row counts: 1,024 tasks × 14 policies = 14,336 rows per run (both thread counts). Full
machine-readable detail (per-family/arm breakdowns, all integrity booleans, both
determinism hashes, complete gate tables) is in
`d169a-resident-option-interface-envelope-result.json`. Bulk per-task rows:
`artifacts/experiments/d169a-resident-option-envelope/d169a-jobs{1,20}-9844136-9844199.tsv`.
