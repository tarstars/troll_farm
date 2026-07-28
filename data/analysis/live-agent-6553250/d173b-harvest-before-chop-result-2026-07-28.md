# D173b harvest-before-chop trigger-fidelity repair — result

Date: 2026-07-28.
Verdict: **CLOSED** (mechanism gate fails all three sub-gates; value gate fails three of
six sub-gates). Trigger-fidelity repair itself (Delta 1) is fully verified as correct
(Delta 2 gate: 100%, 64/64) — this run definitively rules out "wrong trigger scope" as the
cause of a mechanism-gate failure, and isolates a different, previously-undiagnosed root
cause (below).

## What was built and how it ran

Delta 1 revised the D173a patch's trigger from candidate-existence to a true
assignment-outcome read. Architecturally this could not stay inside `main_candidates`/
`endgame_candidates` (both run per-unit, before `MoisanBot::select` has seen every unit's
candidates, so "would this unit's assignment actually pick CHOP" is not yet knowable at
that point) — instead the fix is a new stateless fn `harvest_before_chop_rewrite(view,
commands, scarce_farmer_id, early)`, called once from `commands()` as the last
transformation of `selected` before `out.extend(selected)` (placed immediately after, and
running after, the existing `apply_opponent_crop_harvest_contact` rewrite it is modeled
on). It scans the resident's own already-computed final assignment for `CHOP {id}` entries
and rewrites to `HARVEST {id}` only when: the unit is not the scarce farmer and this is not
an early-opening turn (both guard the fix to exactly the two candidate generators D173a's
protocol scoped it to, since `scarce_farmer_candidates`/`early_candidates` are the only two
branches that route a unit's command outside `main_candidates`/`endgame_candidates`);
`harvest_power >= 1` and `free_capacity() > 0`; the plant at the unit's own cell (CHOP is
always same-cell in this engine — confirmed against `apply_chop_on_cells`/`apply_harvest`
in `rust/src/game/engine.rs`, both keyed by unit id only) has `fruits > 0`; shack BFS
distance `<= 2`. Reading the literal already-selected command makes the fix exact for both
regimes without reproducing `MoisanBot::select`'s 1-unit / 2-unit-joint / N-unit-greedy
branching: it automatically respects `endgame_candidates`' own hardcoded-10,000 "finish
what you started" CHOP override (fires only when that override actually won), and
automatically excludes `main_candidates`' transit-passthrough case (a same-cell CHOP
candidate that loses the scoring contest never reaches `selected`, so the rewrite never
sees it).

9 new unit tests (`cargo test --bin yamo_orchard_live`: 32/32 pass, 23 pre-existing + 9
new), including the two Delta 1 explicitly requires (transit unit whose real
`MoisanBot::select` winner is MOVE, built with a real losing CHOP candidate, is NOT
rewritten; unit whose real winner is CHOP on its fruited own-cell tree IS rewritten), the
D173a guard-condition set (hp=0, unfruited, distance>2), two new scope-fidelity tests
(scarce-farmer unit / early-opening turn both suppress the rewrite), a chop-resumes test,
and an `endgame_candidates` override-integration test. Diff: one new fn + one 1-line call
site + tests (`d173b-fix-as-tested.patch`, 250 lines).

Built `rust/src/bin/d173b_harvest_before_chop_panel.rs` and
`cgauto/analyze_d173b_harvest_before_chop.py` as mechanical d173a→d173b renames of the
D173a panel runner/analyzer (identical seeds/families/gates/methodology; the D173a
originals are untouched, frozen). `cargo build --release --bin
d173b_harvest_before_chop_panel` with the fix present in the dev copy (bakes it in via the
`troll_farm::resident_policy` alias), verified same control-snapshot SHA `fff6669b...` as
the dev copy, then **immediately restored the dev copy byte-exact** (`git checkout --`, SHA
re-verified `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`, re-verified
again at the very end of the session — clean both times) and confirmed via
`D173B_DEBUG_TASK=9854000,0,6` that the already-built binary still exhibits the fix
post-restore (control 116/21, candidate 138/27, first_divergence_turn=90 — identical to
D173a's own reading for this same task, evidently a genuine chop-shadow case both triggers
agree on).

## Delta 2 — pre-panel trigger-fidelity verification: PASS (100%, 64/64)

Ran the full panel first (jobs20, 20 threads, with trajectory dumping) specifically to
obtain the activation sample Delta 2 requires: 2,048 rows, **805 activated (39.3%)**,
sharply below D173a's 50.9% as the protocol anticipated. A one-off verification script
(not checked in) reproduced the Rust panel runner's own `find_divergence` logic directly
from the trajectory NDJSON (sorted per-turn own-command comparison, seat-aware c0/c1
selection) rather than trusting the TSV's `first_divergence_turn` column blindly, and
cross-checked that column for free (0 mismatches over the sample). It verified the
divergence at that turn is always a pure single-unit CHOP-to-HARVEST substitution (0
anomalies), then checked, for a size-64 fixed-seed (173002) random sample of the 805
activated tasks, whether CONTROL issued `CHOP {id}` for the diverging unit at the
divergence turn or either of the two turns immediately before it. **Result: 64/64 (100%)
show CHOP at the divergence turn itself.** Given the assignment-outcome trigger's own
construction, this was expected to land at or near 100% rather than being a genuinely open
question the way D173a's 19/60 was — it exists to catch an implementation bug reproducing
D173a's failure, and finds none. Output:
`artifacts/experiments/d173b-harvest-before-chop/d173b-trigger-fidelity-check.json`. **Not
BLOCKED** — proceeded to the full panel.

## Integrity — clean

All pass: 2,048/2,048 rows, task matrix exact, all games done, 1,243/1,243 inactive tasks
byte-exact to control (0 mismatches), jobs1/jobs20 byte-identical
(`99d1a03584e0f94f5b91a13181dc577e47130ed5e22d2fbaa817eb30273f0f1d` both).

## Why it failed — mechanism (fails all three sub-gates, similar magnitude to D173a)

- Targeted sub-class (`harvest_slack` restricted to chop-shadow-shack<=2) reduced only
  **21.3%** (3,407 → 2,681 episodes) — *worse* than D173a's own 23.6%, despite the trigger
  now being 100%-verified assignment-faithful.
- Total `harvest_slack` (all sub-classes) **increased** 22,059 → 23,882 (+8.3%), again
  slightly worse than D173a's +7.8%, failing "not increased."
- Of the other five detectors: `door_queue` +21.2% (1,530 → 1,855 episodes) and
  `idle_with_work` +11.9% (74,174 → 83,002 episodes) both worsen (less severely than
  D173a's +30.0%/+15.3%, but still a clear displacement pattern); `late_train_window` and
  `repeated_failed_command` hold flat (both near-zero); `unbanked_carry` actually
  *improves* this time (122 → 113 episodes, unlike D173a's slight worsening).

**Root cause, traced directly** (not inferred from gate numbers alone — this is a new
finding distinct from D173a's diagnosis, which this run's 100% Delta-2 fidelity result
rules out as the explanation here): decomposed every surviving candidate-side
chop-shadow-shack≤2 subclass episode (1,368 of them, all confined to the 805 activated
tasks) by the harvest_power of the dominant on-cell chopper. **1,367/1,368 (99.93%)** have
a dominant chopper with `harvest_power == 0` — i.e., a trained "pure chopper" specialist,
whose capability is fixed by `opening_options`' hardcoded `harvest_power: 0` for trained
units, a binding constraint this fix (inherited unchanged from D173a) is explicitly
forbidden from touching ("D167's BANK_SEED regularity depends on it; changing capability is
strategy, not execution"). Restricting the same census to CONTROL, on the identical
805-task activated subset: of 2,094 subclass episodes, **1,002 have a harvest-capable
(hp>=1) dominant chopper** and are therefore genuinely addressable by this fix; **1,092
already have an hp=0 dominant chopper** and were never addressable by any version of this
fix. Within the addressable population, the fix works almost perfectly: 1,002 → 1 surviving
(**99.9% reduction**). But the *inaddressable* hp=0 population does not merely hold flat —
it *increases*, 1,092 → 1,367 (**+25.2%**), as a downstream cascading consequence of the
fix's own local corrections reshaping subsequent turns' game states (different fruit/carry/
timing after a capture ripples into different unit scheduling later in the same 300-turn
game, occasionally producing new hp=0 chop-shadow situations that would not have existed in
the counterfactual control trajectory). Net effect on the subclass count: −1,001 (addressable)
+275 (cascading, inaddressable) = **−726**, exactly the observed 3,407→2,681 delta. This is
the same "displacement, not elimination" shape the aggregate gates already show (total
`harvest_slack` +8.3%; `door_queue` +21.2%; `idle_with_work` +11.9%) but now traced to a
specific, quantified mechanism: **roughly half of the protocol's own targeted sub-class
population is constitutionally unreachable under the frozen harvest_power:0-untouched
constraint, and fixing the reachable half's local waste event moves enough downstream state
to create comparable new waste elsewhere.**

## Value — passes on central tendency (weaker than D173a), fails on tail/robustness

- Overall paired mean **+1.0625** (>= 0 floor, pass) — roughly a third of D173a's +2.935,
  consistent with a far smaller, more surgically-scoped activated population (805 vs 1,043
  tasks) that excludes the broad trigger's often-small-positive transit-passthrough
  diversions.
- Map-clustered 95% CI **[−0.056, +2.181]** (lower bound >= −0.5 floor, pass, though the
  point estimate itself is now barely on the positive side of zero — a much thinner margin
  than D173a's [+1.346, +4.524]).
- Activated-subset mean **+2.703** on 805 tasks (>= +1.0 floor, pass) — well below D173a's
  +5.763; the genuinely-scoped activation set is *less* concentrated in value than D173a's
  broader one, not more, suggesting the excluded transit-passthrough diversions were on
  average mildly positive themselves (small "free" pickups on the way to a better target),
  consistent with D173a's own characterization ("most of the time grabbing nearby fruit is
  a small net positive").
- Worst family **compact_gold, −1.391** (fails the >= −1.0 floor; same worst family as
  D173a, smaller magnitude than D173a's −2.06).
- Catastrophes: candidate 52 vs control 49 (fails "not above control"; D173a was 54 vs 49).
- Negative-margin mass ratio **1.081** (fails the <= 1.05x ceiling; improved from D173a's
  1.096 but still over).

## Standing conclusions

1. Delta 1 (assignment-outcome trigger) is verified correct and effective at its own
   narrow, literal job: it activates on a sharply smaller, more precisely-targeted
   population (39.3% vs 50.9% of tasks) with 100% same-turn CHOP fidelity, and it captures
   99.9% of the addressable (harvest-capable-chopper) subclass population. D173a's
   diagnosed failure mode (candidate-existence firing on transit-passthrough) is fully
   closed; it is not why this run also fails.
2. The mechanism gate fails for a different, newly-isolated reason: the
   `chop_or_mine_shadows_harvest`/shack<=2 sub-class, as currently defined by
   `is_chop_shadow_shack2`, is dominated (>=99.9% of what survives, ~52% of the activated
   population's total) by episodes whose chopper is a harvest-incapable (hp=0) trained
   specialist — structurally outside this fix's reach under its own binding, inherited
   constraint. No trigger-precision improvement within that constraint can move this gate
   past ~50% (roughly the addressable share), let alone the required 70%, without either
   (a) redefining the sub-class metric to condition on chopper harvest-capability, or (b)
   relaxing the harvest_power:0-untouched constraint (which the D173a protocol explicitly
   ruled out as strategy, not execution).
3. Even within the fix's own addressable population, near-complete local success (99.9%
   subclass reduction there) does not translate to a passing aggregate mechanism gate: the
   cascading/displacement effect on the *inaddressable* population (+25.2%) plus worsening
   in `door_queue`/`idle_with_work` roughly offsets the local gain. This is the same
   "redistributes waste rather than removing it" shape D173a and D171a both hit, now with a
   concrete accounting of where the offset comes from.
4. The value signal remains real but is now weaker and thinner-margined than D173a's
   (smaller mean, CI point estimate near zero, smaller activated-subset mean) — a
   more-precisely-scoped trigger, in this instance, is not simply "D173a's value minus the
   bad tail"; it is a materially different, smaller population whose own central tendency
   is lower, even though the very worst outliers (worst family, catastrophes, negative
   mass) are all somewhat less bad than D173a's.
5. A successor attempt at this fix concept would need to either restrict the mechanism gate's
   sub-class definition to harvest-capable choppers only (measuring what the fix can
   actually address) or accept that this exact execution-class idea, as scoped by the
   frozen `harvest_power:0`-untouched constraint, cannot pass a subclass-reduction gate
   defined over the full (capable + incapable) chop-shadow population. Per protocol: no
   tuning of the distance bound, scoring, or condition attempted; dev copy already restored
   byte-exact (`fff6669b...`, re-verified twice).

## Reproducibility

Result JSON: `d173b-harvest-before-chop-result.json` (verdict CLOSED, all gate values);
Delta-2 fidelity check:
`artifacts/experiments/d173b-harvest-before-chop/d173b-trigger-fidelity-check.json`; panel
TSVs `artifacts/experiments/d173b-harvest-before-chop/d173b-jobs{1,20}-9854000-9854127.tsv`
(byte-identical); trajectory NDJSON
`artifacts/experiments/d173b-harvest-before-chop/d173b-trajectories-{control,candidate}-9854000-9854127.ndjson`;
fix diff `d173b-fix-as-tested.patch` (250 lines); control snapshot
`rust/src/d171a_control_resident_snapshot.rs` (unmodified, shared with D173a); panel runner
`rust/src/bin/d173b_harvest_before_chop_panel.rs`; analyzer
`cgauto/analyze_d173b_harvest_before_chop.py`; protocol + phase markers
(`.superpowers/sdd/d173b-phase-markers.md`) as recorded. D173a's own artifacts
(`d173a-*`) are untouched and remain the frozen record of the prior, broader-trigger
variant.
