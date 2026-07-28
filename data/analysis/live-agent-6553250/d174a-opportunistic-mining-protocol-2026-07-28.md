# D174a — opportunistic mining: lift the workforce-2 mining gate

Status: FROZEN protocol, authored 2026-07-28 (Fable), from the B3.9 audit. Execute
exactly; no scope, threshold, or gate change after any outcome is seen. This is the
project's strongest execution-class candidate to date: a one-site candidate-generation
defect standing between the bot and a priced outcome (B4.3: 2→4 workers ≈ +5.2 rating).

## Root cause being fixed

`iron_candidates()` (`yamo_orchard_live.rs:936–961`) is the sole MINE-candidate
constructor; its only call site is `early_candidates:887`, reachable only while
`own_units < 2` (`:1560`/`:3486`, dispatch `:1581`/`:3545`). After worker two exists the
bot never mines again: 0 MINE actions across 4,090 legal-but-idle workforce-≥2 turns.
Every trained unit already has `chop_power ≥ 1` (`opening_options:1887`), so no capability
change is required.

## Phase 0 — TRAIN-trigger preflight (frozen, decides scope)

Affordability is useless if the bot will not spend it. On ≥64 already-consumed tasks,
synthetically credit the deposited bank to exactly cover a cheap-helper bill at a chosen
turn and observe the unmodified resident: **does it issue TRAIN within 10 turns?**
- If YES in ≥ 80% of trials → the fix is mining only (Delta 1 below); proceed.
- If NO → a second candidate-generation gate exists on TRAIN. Record it as a finding,
  declare it in the lock, and include the minimal TRAIN-gate repair in the same cycle
  (same lineage, same one-site character). Do not silently expand scope: the lock must
  state which variant is being tested.

## Delta 1 — the fix (exact scope; nothing else may change)

Emit a MINE candidate for a unit at workforce ≥2 when ALL hold, evaluated fresh each turn
(no cross-turn state — the D171a stale-arm lesson):
(a) the unit stands on, or orthogonally adjacent to, an iron source;
(b) the unit has free carry capacity;
(c) an unmet TRAIN bill for the cheapest currently-planned worker spec still needs IRON
    (deposited + carried across all own units < bill IRON);
(d) the unit's assigned action for this turn is not itself bill-critical (do not displace
    a PICK/DROP that pays the same bill).
Score it to win over the unit's current action for that turn only; the previous task
resumes next turn. **Opportunistic only** — no routing, no detours, no reservation, no
new state machine. Explicitly NOT the D94 funding-bridge design (which trained worker
three in 147 tasks and lost 91.6 margin through 47,707 turns of dedicated funding).
Edit only the formatted dev copy; the diff must be the candidate emission (+ its call
site) and tests. Restore byte-exact (SHA prefix `fff6669b`) if the verdict is CLOSED.

Unit tests: emitted when standing on iron at workforce ≥2 with a pending IRON bill; NOT
emitted when the bill's IRON is already covered, when carry is full, when the unit is
mid-bill-critical action, or at workforce 1 (that path is unchanged); previous task
resumes next turn.

## Panel

Fresh seeds **9,855,000–9,855,127** (pre-lock grep both ledger volumes for `9,855`;
sealed ranges untouched) × 8 families × both seats = 2,048 paired episodes vs exact
resident control, reusing the frozen control snapshot
(`rust/src/d171a_control_resident_snapshot.rs`, SHA-verified equal to the dev copy).
Compile-then-restore flow as in D173. Byte-identity jobs1-vs-jobs20; `LC_ALL=C`.

## Integrity gates (all before value)

Inactive episodes byte-exact vs control; command purity (diffs begin at a MINE emitted
under the stated conditions); crop/workforce/reward accounting paired; dev-copy scope
check; `troll_farm::resident_policy` re-export intact; all six waste-sweep detectors run
on both arms.

## Mechanism gates (frozen)

- IRON acquired per game rises to **≥ 4.0** (control ≈ 0.68; top-5 ≈ 13.02).
- Unmined-reachable iron episodes at workforce ≥2 fall **≥ 50%**.
- **Worker-3 TRAIN occurs in ≥ 25% of tasks** (control: 0% — D160's zero windows). This is
  the causal test of the whole B3.8/B3.9 chain; the counterfactual predicted 84.4%
  affordability for the cheap spec, so a large shortfall here is itself the finding.
- No waste-sweep detector worsens by >10% (displacement guard).

## Value gates (frozen)

Overall paired mean ≥ **+1.0** with clustered 95% CI lower bound ≥ **0.0**; worst opponent
family ≥ **−1.0**; catastrophes ≤ control; negative-margin mass ≤ **1.05 ×** control;
activated-subset mean ≥ **+1.0**. (The family/tail floors are the ones both D173 variants
failed; they are retained deliberately — a fix that buys mean value by fattening the tail
is not promotable.)

## Verdict

All mechanism AND value gates pass → **QUALIFIED**: build the candidate pair (formatted +
slim via the existing pruning pipeline, sha256 sidecars,
`candidate-agent6561795-opportunistic-mining.{rs,min.rs}`) and **STOP at the arena gate** —
promotion requires a NEW owner authorization (no prior grant carries over). Mechanism
passes but value fails → **CLOSED-AT-VALUE**, and record precisely which gate: this
distinguishes "scaling doesn't pay for us" from "the fix is wrong", which matters for
everything downstream. Mechanism fails → **CLOSED-AT-MECHANISM** with the shortfall
quantified against the 84.4% counterfactual prediction. No tuning in any case.

## Outputs

`d174a-opportunistic-mining-{lock,result-2026-07-28.md,result.json}`; phase markers to
`.superpowers/sdd/d174a-phase-markers.md` (preflight / fix+tests / restore / panel /
analysis); fix preserved as a patch regardless of verdict; bulk rows external
(`artifacts/experiments/d174a-opportunistic-mining/`). Ledger integration is the
controller's.
