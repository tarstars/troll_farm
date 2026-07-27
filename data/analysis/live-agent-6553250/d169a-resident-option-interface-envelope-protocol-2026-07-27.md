# D169a — resident-native option interface: unified crop-safe envelope (B2.1 gate)

Status: FROZEN protocol, authored 2026-07-27 (Fable). Execute exactly; no threshold, arm,
horizon, or vocabulary change after any outcome is seen. This is the go/no-go gate for the
closed-loop program (B2.2/D170).

## Question

Does a unified, resident-native, crop-safe option vocabulary — evaluated as a per-task
hindsight envelope over the exact resident — contain ≥ +10 mean paired margin on the full
1,024-task consumed panel, with clean tails and no negative family? (D162 measured +12.7
[+9.0, +16.3] on a narrower vocabulary and a 128-task panel; this is the same question at
full scale, unified vocabulary, and observable-trigger arming.)

## Panel and baselines

- All 1,024 consumed D148/D161 tasks, both seats, exactly as loaded by the D161/D167/D168
  harness. No fresh seeds anywhere in this experiment.
- CONTROL = exact warmed resident. It must reproduce D161 on every shared terminal,
  score, workforce, crop, mechanics, action-hash, and state-hash field (D168 already
  demonstrates this harness property; reverify).

## Frozen option vocabulary (reuse frozen implementations; do NOT reimplement semantics)

Each option: bounded, routes at most one worker (exact D162 machinery), exact-resident
fallback on abort/horizon, armed at most once per task per arm.

1. `OPT_RETURN` — the D168 ARM_A BANK_SEED successor return, byte-identical semantics
   (arm at first P→S transition completion; PICK most-abundant banked seed, ties
   BANANA>APPLE>PLUM>LEMON; resident-preferred legal cell; PLANT; horizon 24; aborts:
   empty bank, no legal cell, horizon). Reuse `d168a_bank_seed_successor_option.rs`.
2. `OPT_FRUIT`, `OPT_IRON`, `OPT_PROTECT` — the three D163 components exactly as frozen
   there (fruit harvest/banking, IRON routing/banking, consumption protection; 32-turn
   horizon; shadow reserve `[3,3,2,0,3,0]`; no controller TRAIN). Reuse the frozen D163
   module. Arming variants per component:
   a. fixed starts 72 / 104 / 136 (as in D163), and
   b. `TRIG` start: the first turn the observed opponent worker count reaches ≥ 3
      (the B3.1 early-warning trigger; observable in the input each turn).
3. Arm inventory: 1 (`OPT_RETURN`) + 3 components × 4 starts = 13 arms, plus CONTROL —
   14 policies × 1,024 tasks = 14,336 episodes. Local CPU, 20 threads (expect a few
   hours; the byte-identity repeat doubles it).

## Integrity gates (all must pass before any value field is read)

- CONTROL reproduces D161 exactly (all shared fields, 1,024/1,024).
- Every inactive (task, arm) pair is byte-exact vs CONTROL.
- Controller-command purity: only the routed worker deviates; vocabulary limited to the
  frozen option's commands; zero provenance/ownership/deposit-prediction/reward-identity
  violations; workforce and crop accounting paired.
- One-thread vs 20-thread full-matrix products byte-identical (SHA-256 both).
- Frozen D162/D163/D167/D168 modules unmodified (hash-verify against their locks).
- Locale rule: use `LC_ALL=C` for any text-matching verification (D168 lesson).

## Envelope computation (frozen)

- Crop-safety filter first: an (task, arm) result is envelope-eligible only if its crop
  creation is ≥ CONTROL's for that task (relative rule, D122).
- Per-task envelope value = max(paired margin over {CONTROL} ∪ eligible arms).
- Report: mean envelope, map-clustered 95% CI, % tasks improved (envelope > control),
  per-family means, per-arm selection counts, catastrophe count (margin ≤ −100) and
  negative-margin mass of the envelope selection vs CONTROL.
- Diagnostic (reported, not gated): the same envelope restricted to `TRIG`-armed and
  `OPT_RETURN` arms only (the deployability-relevant, observable-trigger subset).

## Value gates (frozen)

- Coverage: ≥ 60% of tasks have ≥ 1 armable option state; else FAIL (representation too
  narrow), independent of value.
- **PASS (opens D170 authoring):** mean envelope ≥ **+10.0** AND clustered CI lower bound
  ≥ **+5.0** AND ≥ 30% of tasks improved AND no negative family mean AND catastrophes ≤
  CONTROL AND negative-margin mass ≤ CONTROL.
- **KILL (< +5.0 mean):** the resident-native option class is dead. Record in
  CONSTRAINTS; per BACKLOG, hold at Tier 0/3. No rescue.
- **BORDERLINE (+5.0 ≤ mean < +10.0 or any single non-mean gate missed):** exactly one
  predeclared extension, D169b — add joint two-worker concrete assignments (D97
  semantics, rebuilt resident-anchored) to the vocabulary and rerun this protocol
  unchanged once. No other modification is authorized.

## Prohibitions

No selector or policy fitting on this run's outcomes (the envelope is an upper bound,
not labels — D100b/D163); no tuning of frozen option parameters; no fresh maps; no
candidate, TestSession, Arena, submission, or YT-write; do not modify frozen modules —
extend by composition only.

## Outputs (house convention)

`d169a-resident-option-interface-envelope-{lock,result}*` in
`data/analysis/live-agent-6553250/` (lock before run: SHA-256 of this protocol, all
runners, and reference inputs); runner `rust/src/bin/d169a_resident_option_envelope.rs`
+ focused tests; analyzer `cgauto/analyze_d169a_resident_option_envelope.py`; bulk rows
on external `artifacts/experiments/d169a-resident-option-envelope/`. Result doc ends with
explicit per-gate verdicts and the overall PASS / KILL / BORDERLINE verdict.

## After the run (pre-adjudicated decision tree — executors follow, do not improvise)

- **PASS** → record in ledger vol 2 + STATE §4 as "READY FOR FABLE ADJUDICATION (D170
  authoring)". STOP Tier-2 work. Cheap sessions may run Tier-3 fillers.
- **BORDERLINE** → run D169b once, then STOP for Fable adjudication regardless of its
  outcome.
- **KILL** → record closure in CONSTRAINTS + ledger + STATE; proceed only with Tier 0/3
  items. Tier-2 is closed pending user decision.
