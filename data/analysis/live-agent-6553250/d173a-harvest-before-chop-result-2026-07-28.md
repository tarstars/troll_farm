# D173a harvest-before-chop — result

Date: 2026-07-28.
Verdict: **CLOSED** (mechanism gate fails decisively; value gate fails on tail/robustness
sub-gates despite a strong positive central tendency).

## What was built and how it ran

The fix implemented the frozen spec's literal scope exactly: one new stateless fn
`harvest_before_chop_candidate(view, unit, chops) -> Option<Candidate>` (impl `YamoBot`),
called from both `main_candidates` and `endgame_candidates` immediately after their
existing `let chops = Self::yamo_chop_candidates(...)`, returning early with the harvest
candidate on fire. Trigger: `unit.stats.harvest_power > 0`; `chops` contains a
`CHOP {unit.id}` candidate for the unit's own cell; that cell's plant has `fruits > 0`;
own-door BFS shack distance `<= 2`. Score 5,000.0 (below `bank_candidates`'
7,000-8,000 floor and the 6,000-12,000 PLANT/scarce-farmer band, comfortably above CHOP's
provable max for a cc=1 unit). No cross-turn state; diff confined to 3 hunks (+48 lines)
in `rust/src/bin/yamo_orchard_live.rs` — the new fn plus one 4-line call-site insertion at
each of the two candidate generators, plus 7 new unit tests. `cargo test --bin
yamo_orchard_live`: 30/30 pass. `git diff` confined to the declared scope (verified).

A due-diligence check beyond the protocol's own text: traced whether a selected
`HARVEST {id}` from this new path could be swept into the pre-existing
`regeneration_commitments`/`fresh_harvest_regeneration` tracker
(`remember_selected_regeneration`). Confirmed the live resident's actual constructor chain
sets `persistent_regeneration = true` but leaves `fresh_harvest_regeneration = false` — the
tracker's `HARVEST` match arm never fires for the live resident regardless of this fix.
Also confirmed the orchard mother-tree protection needs zero new code (two independent
pre-existing filters already strip any candidate — including this new one — targeting the
protected cell).

Built `rust/src/bin/d173a_harvest_before_chop_panel.rs` (new file; reuses
`rust/src/d171a_control_resident_snapshot.rs` unmodified as CONTROL, verified same SHA
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` as the dev copy),
release-built with the fix still present in the dev copy (baking the fix into the compiled
binary via the `troll_farm::resident_policy` `#[path]` alias), then **immediately restored
the dev copy byte-exact** (`git checkout --`, SHA re-verified `fff6669b...`, re-verified
again at the end of the session — clean both times) and confirmed via
`D173A_DEBUG_TASK` that the already-built binary still exhibits the fix post-restore. Fix
preserved as `d173a-fix-as-tested.patch` regardless of verdict.

Panel: 128 fresh seeds (9,854,000-9,854,127) x 8 families x 2 seats = 2,048 paired tasks,
run at 1 and 20 threads; TSVs byte-identical
(`a51ddf52074632cd767fa69bfd337430979f5e3bb694fc9fe16b4223f0087ce6` both). 1,043/2,048
tasks (50.9%) activated. Full per-turn trajectories (units, plants, banks, both players'
commands) captured for CONTROL always and CANDIDATE for the 1,043 activated tasks
(inactive tasks are provably byte-identical to CONTROL by induction, so re-decoding them
would only reproduce CONTROL's own counts), bridged into
`cgauto.waste_sweep.build_decoded_game` — the function's own docstring sanctions exactly
this reuse — so all six standing waste detectors ran unmodified over both arms via the new
`cgauto/analyze_d173a_harvest_before_chop.py`.

## Integrity — clean

All pass: 2,048/2,048 rows, task matrix exact, all games done, 1,005/1,005 inactive tasks
byte-exact to control (0 mismatches), jobs1/jobs20 byte-identical at 1 vs 20 threads.

## Why it failed

**Mechanism — fails all three sub-gates:**

- Targeted sub-class (`harvest_slack` restricted to chop-shadow-shack<=2) reduced only
  **23.6%** (3,407 -> 2,604 episodes), far short of the >=70% floor.
- Total `harvest_slack` (all sub-classes) **increased** 22,059 -> 23,782 (+7.8%), failing
  "not increased" outright — the fix makes the detector it targets worse in aggregate.
- Of the other five detectors, three worsen: `door_queue` +30.0% (1,530 -> 1,989 episodes),
  `idle_with_work` +15.3% (74,174 -> 85,551 episodes), `unbanked_carry` +1.6% by episode
  count (122 -> 124, though flagged turns fell slightly). Only `late_train_window` and
  `repeated_failed_command` (both near-zero in this population) hold flat. This is a clear
  no-displacement failure, structurally the same shape as D171a's own mechanism failure
  (a fix that looks locally correct but redistributes waste rather than removing it).

**Root cause, traced directly** (diff-inspected the divergence turn of the worst-margin
task and a 60-task sample of first-divergence contexts, not inferred from gate numbers
alone): the trigger's "current chop target" check — `chops` contains a `CHOP {id}`
candidate for the unit's own cell — is satisfied whenever a live fruited plant merely sits
under the unit *at candidate-generation time*. It does **not** verify CHOP is the unit's
actual winning/selected action that turn. In `main_candidates` (unlike
`endgame_candidates`'s hardcoded 10,000 "finish what you started" override), a same-cell
CHOP candidate routinely loses the scoring contest to a MOVE toward a bigger or
closer-to-completion tree elsewhere — the fix fires regardless, redirecting the unit into a
harvest-then-bank detour away from a genuinely better in-flight plan.

Concrete example (worst task in the panel, seed 9854052/seat 0/gold_adaptive,
margin_delta -218): at turn 10, CONTROL's own selected command was `MOVE 0 8 5` (heading
toward a different tree) while unit 0 stood momentarily on a separate fruited cell it had
only just transited onto — CANDIDATE fires `HARVEST 0` instead. Sampled 60 activated
tasks for whether CHOP had actually been issued in the two turns immediately preceding
activation (a proxy for "was this a genuine sustained chop-shadow" vs. "the unit merely
passed through"): only **19/60 (31.7%)** show a recent CHOP; **41/60 (68.3%)** show none —
consistent with B3.5's own `transit_passthrough` sub-class (58.7% of the raw population,
and the one sub-class the B3.5 report itself flagged as loss-tilted), not the targeted
`chop_or_mine_shadows_harvest` sub-class the protocol scoped this fix to. This single gap
explains every observed number: a diluted subclass reduction (the fix hits a materially
different, broader population than the one it was measured against), an *increase* in
total waste (diverting a unit with a better in-flight plan into a detour is a new
inefficiency, not a cure), and the value tail failure below (interrupting a better plan
occasionally cascades badly on individual tasks).

**Value — passes on central tendency, fails on tail/robustness:**

- Overall paired mean **+2.935** (>= 0 floor, pass) — remarkably close to the B3.5
  diagnosis's own ~2.81 pts/game gross ceiling estimate for this scoped subset.
- Map-clustered 95% CI **[+1.346, +4.524]** (lower bound >= -0.5 floor, pass).
- Activated-subset mean **+5.763** on 1,043 tasks (>= +1.0 floor, pass comfortably —
  the single strongest number in this experiment).
- Worst family **compact_gold, -2.06** (fails the >= -1.0 floor).
- Catastrophes: candidate 54 vs control 49 (fails "not above control" — the fix
  *increases* catastrophic losses).
- Negative-margin mass ratio **1.096** (fails the <= 1.05x ceiling).

The central-tendency numbers alone would look like a clean win — the mean and the
activated-subset mean both land close to or above what the diagnosis predicted. The
tail/robustness gates are exactly what catch the real cost the broader-than-intended
trigger imposes: most of the time grabbing nearby fruit is a small net positive, but on a
meaningful minority of tasks (the same passthrough-diversion mechanism above) it
materially worsens the game, enough to move both the catastrophe count and the negative
mass ratio the wrong way.

## Standing conclusions

1. The B3.5 diagnosis's mechanism (an absent HARVEST candidate) and its "chop resumes next
   turn" framing were correct for the genuine `chop_or_mine_shadows_harvest` population,
   but the frozen trigger condition as literally specified ("its current chop target is a
   tree bearing ripe fruit") is satisfiable by a strictly larger population — any unit
   merely standing on a fruited, choppable cell, whether or not CHOP was actually about to
   be selected. This gap is closed by construction in `endgame_candidates` (whose own
   "finish what you started" override already forces CHOP to win when present) but *not*
   in `main_candidates`, where CHOP-on-own-cell is one candidate among several and
   frequently loses.
2. Do not retune the score, the shack-distance bound, or the trigger's fruit/capacity
   checks within *this* frozen spec — per protocol. A successor attempt at this same idea
   would need a materially different trigger: verifying CHOP is actually the winning
   candidate among `chops` (or, more simply, gating on genuine same-cell persistence —
   e.g., the unit having *just* chopped that exact cell last turn, which would exclude
   transit-passthrough arrivals by construction) before this mechanism can be expected to
   hit the intended sub-class cleanly.
3. The underlying value signal is real and sizeable (+2.9 mean, +5.8 activated-subset,
   both close to or above the diagnosis's own predictions) — this is not a "no effect"
   result like D170b, nor a subtle state-machine bug like D171a. It is a scope-too-broad
   result: a real, roughly-diagnosis-sized gain sits inside a distribution whose tail the
   frozen gates correctly refuse to accept as-is.
4. The candidate was never built (QUALIFIED-only per protocol); the live resident and the
   dev copy are byte-exact and untouched; no owner authorization was sought or needed.

## Reproducibility

Result JSON: `d173a-harvest-before-chop-result.json` (verdict CLOSED, all gate values);
lock: `d173a-harvest-before-chop-lock.json`; panel TSVs
`artifacts/experiments/d173a-harvest-before-chop/d173a-jobs{1,20}-9854000-9854127.tsv`
(byte-identical); trajectory NDJSON
`artifacts/experiments/d173a-harvest-before-chop/d173a-trajectories-{control,candidate}-9854000-9854127.ndjson`;
fix diff `d173a-fix-as-tested.patch` (193 lines); control snapshot
`rust/src/d171a_control_resident_snapshot.rs`; panel runner
`rust/src/bin/d173a_harvest_before_chop_panel.rs`; analyzer
`cgauto/analyze_d173a_harvest_before_chop.py`; protocol + phase markers as recorded.
