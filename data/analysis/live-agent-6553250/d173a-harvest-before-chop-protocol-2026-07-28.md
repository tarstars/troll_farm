# D173a — harvest-before-chop: bounded fix for the missing HARVEST candidate class

Status: FROZEN protocol, authored 2026-07-28 (Fable), from the B3.5 diagnosis
(`scratchpad b35-harvest-slack-diagnosis-report.md`; findings in ledger vol 2). Execute
exactly; no scope, threshold, or gate change after any outcome is seen. Execution-class
waste-cut; the diagnosis's honest net estimate for the scoped subset is ~2.81 pts/game
gross (202 events / 576 pts on the 205-game corpus).

## Root cause being fixed

`YamoBot::main_candidates`/`endgame_candidates` (`yamo_orchard_live.rs:3084–3145`,
`:3200–3339`) construct no HARVEST candidate for busy units; the only fruit-aware
fallback (`idle_harvest_candidates:3340–3387`) is gated behind endgame AND
no-other-target — structurally unreachable. Result: a harvest-capable unit standing ON a
fruited tree it is chopping destroys the fruit with the tree. 33.4% of all slack
episodes are this exact `chop_or_mine_shadows_harvest` pattern.

## The fix (exact scope; nothing else may change)

In the busy-unit candidate construction, add ONE stateless candidate class, reusing the
existing `fruit_candidates` pattern (`:910–919`): when a unit is **harvest-capable**
(its actual `harvest_power ≥ 1` — the starter), its current chop target is a tree
**bearing ripe fruit**, and that tree is at **shack-distance ≤ 2**, emit a HARVEST(fruit)
candidate scored to win over the chop for exactly that turn (the chop resumes next turn;
banking follows the resident's normal logic). Constraints, binding:
- `opening_options`' hardcoded `harvest_power: 0` for trained units is **untouched**
  (D167's BANK_SEED regularity depends on it; changing capability is strategy, not
  execution).
- The orchard/reserve machinery (`ScarceIntent`, `idle_harvest_candidates`,
  `force_unique_door_clear`) untouched.
- No new state machine, no cross-turn memory (the D171a stale-arm lesson) — the
  candidate is recomputed from current state each turn.
- Edit only the formatted dev copy; diff = the one candidate-emission block (+ tests).
  Dev copy must be restored byte-exact (SHA prefix `fff6669b`) if the verdict is CLOSED.
Unit tests: candidate emitted exactly under the triple condition (capable + ripe-fruited
own chop target + shack≤2); not emitted for trained (hp=0) units, unfruited trees,
distance >2, or non-chop assignments; chop resumes after harvest.

## Panel

Fresh seeds **9,854,000–9,854,127** (pre-lock grep both ledger volumes for `9,854`;
sealed ranges untouched) × 8 families × both seats = 2,048 paired episodes vs exact
resident control. Byte-identity jobs1-vs-jobs20; `LC_ALL=C`.

## Integrity gates (all before value)

Inactive episodes (condition never met) byte-exact vs control; command purity (diffs
begin at a HARVEST emitted under the triple condition); crop/workforce/reward accounting
paired; dev-copy scope check (`git diff` confined to the declared block + tests);
`troll_farm::resident_policy` re-export intact.

## Mechanism and value gates (frozen)

- **Mechanism:** on the panel, `waste_sweep.py`'s harvest_slack episodes restricted to
  the chop-shadow-shack≤2 sub-class reduced **≥ 70%** vs control; total harvest_slack
  (all sub-classes) not increased; the other five waste detectors not worsened (no
  displacement).
- **Value:** overall paired mean ≥ **0.0**, clustered CI lower bound ≥ **−0.5**;
  activated-subset (episodes where the new candidate fired) paired mean ≥ **+1.0**;
  worst family ≥ −1.0; catastrophes ≤ control; negative mass ≤ 1.05 × control.
- **Verdict:** all pass → **QUALIFIED** — build the candidate pair (formatted + slim via
  the existing pruning pipeline, sha256 sidecars,
  `candidate-agent6561795-harvest-before-chop.{rs,min.rs}`) and **STOP at the arena
  gate**: promotion requires a NEW owner authorization (no prior grant applies). Any
  gate fails → **CLOSED** — restore the dev copy byte-exact, record; no tuning of the
  distance bound, scoring, or condition.

## Outputs

House convention `d173a-harvest-before-chop-{lock,result-2026-07-28.md,result.json}`;
phase markers to `.superpowers/sdd/d173a-phase-markers.md` (fix+tests / panel / analysis);
bulk rows external (`artifacts/experiments/d173a-harvest-before-chop/`); fix preserved as
a patch regardless of verdict. Ledger integration is the controller's.
