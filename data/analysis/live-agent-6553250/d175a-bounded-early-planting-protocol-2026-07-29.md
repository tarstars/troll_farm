# D175a — bounded early planting: break the "chopping always wins" priority

Status: FROZEN protocol, authored 2026-07-29 (Fable), from B4.4 + B4.5. Execute exactly;
no scope, threshold, or gate change after any outcome is seen. This targets the root cause
the week's audits converged on: the resident farms only when idle, plants at median turn
191.5 versus peers' 21–29, and reaps 0.93% versus every other two-worker agent's 15–17%.

## What is being fixed, and what is NOT

Fixed: the **priority defect**. PLANT is reachable only through an idle-regeneration
fallback that requires a worker to have nothing left to CHOP (`yamo_orchard_live.rs:
3084-3145`, `:3200-3253`); chopping always outranks planting.

NOT touched, deliberately: the `banana_factory_*` subsystem and its one-shot selector
(`:4077`, `:5216-5234`) — dead code in the dev copy, absent from the deployed slim artifact,
selector fires 5.9%, and its D89/D91 lineage failed on map-cluster support. Do not
resurrect or tune it. Also untouched: `can_train`'s hard 2-worker cap (D174a) — scaling is
a separate, later question; this experiment is about having an economy at roster 2, where
B4.4 showed we are already at parity with strong peers (58.2% vs 58.3%).

## The fix (exact scope)

One stateless candidate-priority rule, recomputed each turn. Emit a PLANT candidate that
outranks CHOP for a worker when ALL hold:
(a) the worker carries a plantable seed (or can PICK one from an adjacent own-bank source
    this turn under the resident's existing pick logic — do not add new routing);
(b) our live own-crop count is **< 6** (the peers' measured ceiling is ~5–6 concurrent);
(c) the turn is **≤ 120** (early-economy window; peers plant at 21–29 and we already reach
    roster 2 at median turn 7, so the constraint is priority, not timing);
(d) a legal plant cell exists within BFS distance ≤ 2 of the worker's current position
    (no detours — the D174a lesson: diverting workers for distant resources is strictly
    harmful);
(e) the displaced CHOP is not bill-critical or endgame (turn > 250 excluded outright).
No cross-turn state, no reservations, no new state machine (D171a's stale-arm lesson).
Edit only the formatted dev copy; diff = the candidate emission plus tests. Restore
byte-exact (SHA prefix `fff6669b`) on any CLOSED verdict. Compile-then-restore flow as in
D173/D174.

Unit tests: emitted under the full conjunction; NOT emitted at 6+ live crops, after turn
120, with no seed, with no cell within distance 2, when the CHOP is bill-critical, or in
endgame; CHOP resumes next turn.

## Panel

Fresh seeds **9,856,000–9,856,255** (256 maps — deliberately wider than D91's 16, because
D91's actual failure was map-cluster support, CI [−1.74, +63.76]) × 8 families × both seats
= **4,096 paired episodes** vs exact resident control (frozen snapshot
`rust/src/d171a_control_resident_snapshot.rs`, SHA-verified). Pre-lock: grep both ledger
volumes for `9,856` overlaps; sealed ranges untouched. Byte-identity jobs1-vs-jobs20;
`LC_ALL=C`.

## Integrity gates

Inactive episodes byte-exact vs control; command purity (diffs begin at a PLANT emitted
under the stated conjunction); crop/workforce/reward accounting paired; dev-copy scope
check; `troll_farm::resident_policy` re-export intact; all six waste-sweep detectors on
both arms.

## Mechanism gates (frozen)

- Median turn of first successful PLANT falls to **≤ 60** (control ≈ 191.5; peers 21–29).
- Own-crop reap rate rises to **≥ 5%** (control 0.93%; peers 15–17%).
- Peak concurrent own crops stays **≤ 8** (peer reference ~5–6; guards against D89's
  unbounded dump).
- No waste-sweep detector worsens by > 10%.

## Value and safety gates (frozen)

- **Safety ratio, reinstated unweakened from D89/D91: Δopponent score ≤ 0.40 × Δown
  score.** This is the gate D89 failed (+82.9 opponent) and the field says the leak is
  real (+20.8 opponent score for higher-planting peers, CI [1.8, 38.0]).
- Overall paired mean ≥ **+1.0**, clustered 95% CI lower bound ≥ **0.0**.
- Worst opponent family ≥ **−1.0**; catastrophes ≤ control; negative-margin mass ≤
  **1.05 ×** control. (These are the floors both D173 variants and D174a failed; retained.)
- Activated-subset mean ≥ **+1.0**.

## Verdict

All mechanism, safety, and value gates pass → **QUALIFIED**: build the candidate pair
(formatted + slim via the pruning pipeline, sha256 sidecars,
`candidate-agent6561795-bounded-early-planting.{rs,min.rs}`) and **STOP at the arena
gate** — promotion requires a NEW owner authorization. Mechanism passes, safety ratio
fails → **CLOSED-AT-SAFETY**, and record it as the third independent confirmation that our
production feeds the opponent more than it feeds us (D89, field correlation, this) — that
would make the leak a structural property of our economy rather than of any one design.
Mechanism fails → **CLOSED-AT-MECHANISM** with the shortfall quantified. Value-only failure
→ **CLOSED-AT-VALUE**. No tuning in any case.

## Outputs

`d175a-bounded-early-planting-{lock,result-2026-07-29.md,result.json}`; phase markers to
`.superpowers/sdd/d175a-phase-markers.md` (fix+tests / fidelity / restore / panel /
analysis); fix preserved as a patch regardless of verdict; bulk rows external
(`artifacts/experiments/d175a-bounded-early-planting/`). Ledger integration is the
controller's.
