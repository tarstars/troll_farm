# Legend score-25.40 experiment cycle — volume 4 (opened 2026-08-04)

Objective and live state: `docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` — check before
proposing. Volume 3 (`legend-top3-experiment-cycle-vol3-2026-07-30.md`) is frozen after the
owner-directed round-36 simplified E7a deployment.

Per-experiment obligations: one entry here; a CONSTRAINTS bullet for anything closed; a STATE.md
§4 update. The first session ending with this file over 100 KB freezes it and opens volume 5.

<!-- entries below -->

## 2026-08-04 — round-36 settled standing

The owner requested a settled position/game-count read for exact round-36 agent `6594200`,
submission `41090606`. At 16:25:25Z both platform score endpoints agree: **22.81, rank 32/137**,
with **160/160 games complete** and zero pending. The submission-scoped audit records 93W/2T/65L,
mean margin +8.925, 21 catastrophes, negative-margin mass 6,381, zero runtime signals, and clean
identity. Exact checkpoint SHA is `0f476514...`.

This read is recorded without Arena mutation. Round 36 remains active.

## 2026-08-04 — round-36 full replay corpus exported

The 160 settled games for agent `6594200`, submission `41090606`, are now available to agents
without platform access as a sanitized full-frame Git LFS corpus under
`data/shared-lfs/r36-agent-6594200/`. All 160 public replay fetches succeeded, with 86,940 frames
and exact game-ID equality to the settled checkpoint. The 40,006,551-byte staging set compresses
to 5,774,722 bytes at SHA `59f6283b...`; personal/session fields are removed and player names are
replaced by positional placeholders.

Payload commit `936cf577` uploaded successfully. A fresh smudge-disabled clone exposed the exact
LFS pointer and then reproduced the full payload and hash through an exact-path selective pull.
This was read-only with respect to both Arena and the collector-owned `data/raw/games/` cache.

## 2026-08-04 — banana restoration R2 handoff rejected before value testing

Claude's 74,725-byte candidate SHA `f29efd0e...` rebuilds exactly and independently reproduces
its compile, empty-input, 23 detector-test, 7/7 TIER-P, and 8/8 reported TIER-C results. Those
engineering checks are not sufficient: the candidate's own all-green lifecycle trace harvests
two bananas, carries both, then plants at turns 58 and 61 before banking, directly falsifying
I-9's one-seed/surplus-bank rule. The source also lacks the reviewed conversion-or-abandon branch
for an unripe contested mother, and the handoff lacks a complete compilable readable source for
the mandatory research/compact equality gate.

Verdict for exact SHA `f29efd0e...`: **IMPLEMENTATION_INVALID**. Remaining host replay and value
gates stop for these bytes; no Arena mutation occurred. This does not reject bounded banana
production as an algorithm. A successor needs a new hash and non-vacuous regressions for the
failed behaviors. Full report: `banana-restoration-r2-host-review-2026-08-04.md`.

## 2026-08-05 — banana restoration R2 successor rejected before host replay

Claude's 76,386-byte successor SHA `280ed777...` fixes the first handoff's three defects. The exact
source compiles; the new non-vacuous one-seed/surplus-bank, ownership-loss abandon, and
ownership-loss convert regressions and their controls pass; detector self-tests pass 23/23; and a
complete readable source is present.

The successor is still **IMPLEMENTATION_INVALID**. Its conversion predicate estimates chop time
as `ceil(current_health/chop_power)`, ignoring banana growth and health gain during the chop
sequence. A size-2, health-4, cooldown-1 tree with chop power 1 is reported as four turns but needs
five, which can reverse the required strict race against the opponent. The D-8/I-10a conflict also
remains untested: the passing convert fixture starts from a pre-existing mother, so D-8's
own-planted history never applies.

Integrator ruling: after a real ownership flip, an exact feasible I-10a conversion overrides
diagonal-mother protection; discretionary chopping while the mother remains owned is still
forbidden. The next revision needs growth-aware travel/chop simulation and a red/green boundary,
plus an amended detector and a non-vacuous own-planted flip/convert trace with an owned-mother
negative control. Host replay/value gates remain stopped; no Arena mutation occurred. Full report:
`banana-restoration-r2-successor-host-review-2026-08-05.md`.

## 2026-08-05 — banana restoration R2 round 3 still implementation-invalid

Claude's 76,750-byte SHA `2f58edef...` replaces the static chop estimate with the source's exact
tree-transition helpers. Independent rebuild/compile, all eight R-1..R-3 and control checks, the
old-`280ed777...` red result, and 27 detector tests reproduce.

The candidate still stops before host replay/value gates. Its advertised own-planted
flip/conversion t5 is a scripted command stream, not candidate behavior. Running the actual bytes
on that scenario yields PICK, MOVE, PLANT, then resident WAIT through turn 20; there is no flip
response or conversion. The invariant, candidate, and D-8 detector also compare conversion against
different arrival/ripening deadlines and time origins, while the candidate-level R-3 trace does not
exercise growth-added health during chopping.

Verdict: **IMPLEMENTATION_INVALID** for exact SHA `2f58edef...`. Integrator clarification is to use
one absolute-time oracle: conversion completion versus the opponent's earliest executable HARVEST,
with exact travel, growth, fruit production, and action timing. The next revision needs that oracle
in spec/code/regression/D-8 plus candidate-driven own-planted flip/conversion evidence. No Arena
mutation occurred. Full report: `banana-restoration-r2-round3-host-review-2026-08-05.md`.

## 2026-08-05 — banana restoration R2 round 4 fails the first broad host panel

Claude's 77,397-byte SHA `9f5ef833...` materially repairs round 3. The exact rebuild and both
compact/readable compiles pass; 28 detector tests and the one-oracle self-test pass; the real
candidate now plants, observes a real ownership flip, and converts under the strict absolute-time
oracle. Old `2f58edef...` remains RED for the expected feasible-edge and flip-response failures.

The first broad continued-referee panel finds a new terminal injury before replay/value work. On
map `9,854,000`, seat 0, against `gold_adaptive`, worker 2 is full with two wood and alternates
between `(8,4)` and `(8,3)` on turns 34--258 inclusive: 225 turns with no DROP, cargo loss, or
progress. Parent margin +68 becomes candidate -93. This directly falsifies I-19/I-20/I-21 and D-1;
the exact contract was written to prevent this same class of live injury.

Verdict: **IMPLEMENTATION_INVALID** for exact SHA `9f5ef833...`. The banana-live, exact
`897829265`, value, and Arena gates stop. Claude's new pipeline pre-review passes its 24 tests but
also misses this class because its critical-claim list excludes the banking/oscillation invariants;
the finding must enter the permanent failure ledger and a candidate-driven red/green gate. No
Arena mutation occurred. Full report: `banana-restoration-r2-round4-host-review-2026-08-05.md`.

## 2026-08-06 — banana round 5 withdrawn; FSM design requires revision

Claude withdrew 77,299-byte SHA `47c98f53...` before host execution after its new deterministic
120-map/two-seat fuzz gate blocked 141/240 candidate games. The prior mother-forbidden fix removed
one mechanism but not the class: 37 games still exhibited full-cargo coordination failures through
a stationary resident and articulation/occupancy interaction. The panel also exposed fruit-safety,
stall, oscillation, diagonal-chop, lost-fruit, and planting-bound violations. Round 6
`eac2eb36...` cuts the blocking set to 47/240 but is explicitly not a handoff. No host, value, or
Arena work ran for either SHA.

Independent review of Claude's replacement 11-state/six-channel design accepts the design-first
method, latched-mother claim, transit neutrality, lost-worker release, and verification ordering.
It remains **REVISION_REQUIRED**: simultaneous events lack atomic priority; EV7 and the founding
guard use proxy ETA thresholds rather than one exact harvester/chopper survival oracle; parent
slot divergence is causal only on an aligned prefix; and unconditional resident priority conflicts
with the carrier-progress invariant. Post-release veto scope, impossible-commitment exits, and the
exact bounded-enumeration manifest are also open. Full report:
`banana-restoration-r2-fsm-design-review-2026-08-06.md`.

## 2026-08-07 — resident denial scoring: the starter is the denial unit

Read-only source audit answering an owner question ("we choose one of lemon or plum and
concentrate on chopping it out — is that correct?"). Partly: `focus_type` picks ONE species,
by smaller summed BFS distance from OUR shack, frozen for the game; the denial term is then an
additive `900/(1+manhattan-to-opponent-shack)` bonus on top of a `1000*wood/turns` base, not a
clearing phase, with no completion condition and no revision.

Because `wood` is capped by carry capacity and chop turns scale with chop power, the base term
differs ~8x between worker classes while the bonus is identical. Crossover distance — where the
bonus stops outweighing wood efficiency — is **16-21 cells for the starter (1/1/1) but only 1-5
for a trained worker (3/3/3)**. An unassigned division of labour follows: the starter is the
denial unit, the trained worker the economy unit, and the allocation is inverted relative to
capability. Pulled to a size-4 focus tree by the opponent shack, the starter spends 25 turns to
bank one wood; the trained worker would take 9 turns for three. This is a visible mechanism for
the previously measured "pre-fruit denial recovers 18.8 opponent points while forfeiting 81.5
own".

Also recorded: `opponent_trolls <= 2` is already a scale-conditioned abort, so the owner's
proposed give-up rule exists as a trigger; what is missing is a destination, since the abort
falls back to undifferentiated wood maximisation. This qualifies B3.1's "the resident never
conditions on it" — it does condition here, only to switch denial off.

Descriptive only; reopens nothing. N6 already closed the weight ("keep 900"), and H4 closed
denial as bill prevention (`NO_MATERIAL_DENIABLE_BILL`, strict rate 0.0). Source
`fff6669b...` unmodified. Full report: `resident-denial-scoring-audit-2026-08-07.md`;
reproduce with `python3 cgauto/analyze_resident_denial_scoring.py`; drift guard
`tests/test_analyze_resident_denial_scoring.py` (9 tests).

## 2026-08-08 — D-9 calibration: the proxy clause does not measure displacement

Phase 1 item 1 of the consolidated hardening plan, read-only over the committed 240-game
parent-vs-parent floor self-test (`322895ee…`, parent `a8eb3b2b`). Verdict
**`MISCALIBRATED_RETIRE_OR_REPAIR`**.

D-9's unpaired `banana_before_train` clause (spec A10 read literally) fires **196 times across
74 games in a run where TRAIN displacement is zero by construction** — the parent judged against
itself cannot displace its own TRAIN. All three paired clauses that actually observe
displacement (`train_late`, `train_missing`, `train_stats_differ`) correctly fired **zero**
times. The paired path was genuinely enabled: `fuzz_panel.eval_p1` forwards `parent_cmds`
through `td.run_all` into `detect_d9`, so their silence is a measurement, not a disabled branch.

The 196 episodes split exactly 98 PICK / 98 PLANT — the resident's own shack-ring orchard at
`yamo_orchard_live.rs:1193`. The clause flags designed, shipped behaviour as displacement.

**Consequence: D-9 is the largest single source of the broken floor — retiring it alone takes
118 blocking games to 46, a 61% reduction.** Recommended repair (proposed, NOT applied): drop
the proxy clause, keep the paired ones, which cover displacement directly. Re-introducing a
parent-differential exemption is rejected — that is the round-6 ROOT-A gate the owner removed.

Also supplies Phase 1 item 3: **D-2, D-3, D-7 and D-8 have zero episodes across all 240 games**
— UNPROVEN, not passing. The plan named only D-2/D-3/D-8; D-7 belongs on the list.

Binding: no detector change I author enters a verdict until `claude_1` and `chatgpt_1` each
review it independently. Report: `d9-calibration-result-2026-08-08.md`; reproduce with
`python3 cgauto/analyze_d9_calibration.py`; tests `tests/test_analyze_d9_calibration.py` (8).

## 2026-08-08 — Phase 1 items 5 and 9: gate architecture revised; D-1 has two duration modes

**Item 5 — gate architecture (`local_claude_1/gate-architecture-revision-2026-08-08.md`).**
Revision against chatgpt_1's AR-1..AR-9. Three-verdict lattice `GATE_UNREADY`/`BLOCK`/`ACCEPT`,
because a binary gate must assert something about the candidate even when the instrument is
unfit. Evaluation order puts a validated blocker's firing ahead of the readiness check:
positives and negatives are not symmetric, so `BLOCK` stays issuable on a partly-ready gate
while `ACCEPT` requires full readiness. **Detector validity is two axes, not one, and D-9 proves
it** — it passes both bite-tests and fires 196 false positives, so implementation validity
(obeys its spec) and calibration validity (the spec is true) need separate evidence. D-1/D-4
restored to hard pre-state absolutes (AR-1); **no waiver ledger specified at all**, stricter
than AR-4 asked, since an exemption mechanism that exists gets used; comparative detection
dormant with multiset dominance its only permissible form (AR-5); frozen calibration corpus so
a candidate cannot influence its own classification (AR-6); full dependency closure (AR-9).

**Premise correction.** My first draft claimed no negative controls existed and nothing was
validated. False: `test_trace_detectors.py` has **28 passing bite-tests giving a trigger and a
near-miss for all nine detectors**, committed 2026-08-04 — three days before the plan named them
missing. Phase 1 item 4 is therefore re-scoped from building fixtures to auditing whether the
existing pairs discriminate the property or merely the implementation. Zero floor episodes for
D-2/D-3/D-7/D-8 is **not** a gap: the fixtures prove they can fire, so silence is evidence the
parent lacks those defects.

**Item 9 — D-1 mode structure (`local_claude_1/d1-mode-structure-2026-08-08.md`).** Orthogonal
to claude_1's mechanism analysis, which stands. The 35 episodes are sharply bimodal: SHORT
(15 episodes, 6-34 turns, 12 games, none terminal) and LONG (20 episodes, 62-194 turns, 13
games, **15 running to game end**; longest occupies 194 of 200 turns). Counting distinct games,
**the LONG mode has zero `chopper_aggressor` opponents** against a 30.0% panel share, p≈0.0097;
SHORT is 6/12 chopper. Hypothesis (untested): D1-A needs a parked adjacent peer, and an
aggressive opponent dissolves that condition before the bounce becomes terminal. Yields a
falsifiable criterion — **a correct fix must eliminate the LONG mode entirely**, not merely
reduce counts, which is exactly how D176a passed its own gate and left the worst run at 247
turns. Also noted: raw D-1 = 0 is gate compliance, **not** score — oscillation's measured value
is +0.045, CI [-0.024,+0.114].

## 2026-08-08 (correction) — D-9 is INAPPLICABLE, not repairable-by-retiring-the-proxy

`claude_1`'s execution review (`5e123018`) refuted my recommendation and I accept it in full.
I had argued the paired clauses were "demonstrably correct — zero false positives where zero is
the truth". **Invalid.** `detect_d9` guards the whole paired block with `if p_train is not
None:` (`trace_detectors.py:1210`) and the parent emits **no TRAIN at all** (0/60 measured), so
the block **never executes**. Zero output from a branch that never ran is not evidence of
correctness — the same "PASS on zero evidence" error I had just criticised, made by me one
section later.

**Mechanism now resolved** (was `UNRESOLVED` and blocking claude_1's item 4), from the committed
panel source — two independent causes, each ~half the panel: (1) `fuzz_panel.py:486-495` injects
a second worker (id 2) with probability `second_worker_bias`=0.5, and the resident's `can_train`
returns false at `if n >= 2` (`yamo_orchard_live.rs:836`) — TRAIN is hard-blocked, not merely
unaffordable; (2) otherwise `_inventory` grants PLUM ≤ 1 at p=0.15 against a cost of 2. **The
panel is built so TRAIN cannot occur**, deliberately, because it starts the bot in the
post-TRAIN state where banana logic lives.

**Correct disposition: `INAPPLICABLE`** — the harness cannot exhibit the property, so no fixture
on this panel can validate or refute D-9. This is a new precondition to the two-axis model in
`gate-architecture-revision-2026-08-08.md` §3, checked before either axis; an inapplicable
detector left in the required set makes the gate permanently `GATE_UNREADY` for an unfixable
reason. Do **not** build a D-9 fixture here. Options are (a) drop D-9 from the required set
recording `INAPPLICABLE`, or (b) extend the harness to start some games pre-TRAIN — a
calibration-corpus change under AR-6. Retiring the proxy remains right, and its defect is worse
than measured: with `first_train` never set, "before TRAIN" means the entire game, so it is
unbounded.

**Also corrected: the floor without D-9 is 55, not 46.** My method counted only
`detector_counts` and ignored detector-less P-tier violations — the floor has 30 P4 and 4 P2.
D-9 is sole blocker in 63 games; 118 − 63 = 55. claude_1's figure was right and it asked for my
definition rather than asserting mine was wrong. All prior citations of 46 are superseded.
Report: `local_claude_1/d9-inapplicable-2026-08-08.md`; tool and tests updated (9 tests).

## 2026-08-08 — the panel referee has no TRAIN, and its worst two games score cleanest

`chatgpt_1`'s revision-2 blocker 3 refused my "TRAIN cannot occur by construction" claim on the
grounds that initial unaffordability is not a reachability proof. It was right. Full-width
measurement (`cgauto/probe_panel_train_reachability.py`, 240/240, evidence
`local_claude_1/verification/panel-train-reachability-2026-08-08.json`): **2 of 240 games emit
TRAIN**, both one-worker, both map `m040`. `claude_1`'s 0/60 was correct for its sample and does
not generalise — m040 was not in the prefix. Two agents agreed on a conclusion neither had
established; the peer who refused it is the one who cannot run the code.

The injected-worker half stands as an exact proof (142 games, `can_train` false at `if n >= 2`).
The affordability half does not: 2/98 one-worker games reach TRAIN, 2.04%.

**Root cause: `FuzzReferee` does not implement TRAIN** — the token appears zero times in
`fuzz_panel.py`, and its docstring lists only MOVE/HARVEST/CHOP/PLANT/PICK/DROP. The command is
silently discarded, so `n` never rises, `can_train` stays true, and the bot re-emits every turn:
**166 and 182 consecutive turns, 83% and 91% of each game.**

**The finding that matters: both games are among the cleanest on the panel** — `block=False`,
all nine detectors zero, P4 liveness included. The panel's two most pathological games score as
two of its best, and a candidate could be *rewarded* for provoking this state, since emitting a
discarded command forever is invisible to every check while displacing real work.

D-9 `INAPPLICABLE` is **withdrawn as stated**: the paired clauses are reachable in 2/240, so the
property is not unobservable — but the TRAIN they would compare has no effect, so the comparison
is a phantom. This makes chatgpt_1's demand exact: "parent TRAIN absent" is not an adequate scope
guard, because parent TRAIN is sometimes present and still meaningless. Recommended (not
applied): the harness should reject unknown verbs loudly rather than discard them. Full report:
`local_claude_1/panel-train-defect-2026-08-08.md`.

## 2026-08-08 — `readable__no_orchard` named; it oscillates, and the oscillation is inherited

**Owner-assigned reference name** for `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
(SHA `98628e98`, agent/submission `6593838`/`41089629`, registry `e7a-readable-no-orchard-code-cost`).
Full record: `docs/reference/readable__no_orchard.md`.

Three properties hold together and no other registered bot has any two: it is the **only
human-readable submitted source** (1,475 lines; every other is a single 55-99 kB line); it is the
**smallest bot we have** at 46,859 chars of real code with formatting normalised away, against
54,720 for the bot now live; and it holds the **highest mature score we have measured** — 24.76,
rank 21/137 over 160 games. It is `displaced_superseded`: we replaced it with `e7a-r36-simplified`
at 22.81/rank 32, which is 17% larger and ~2 points worse. Governing caveat, raised by the
registry itself: **one mature run**, and the related `e7a-r28-no-orchard-ablation` scored 23.27 on
its own single run.

Owner ruling 2026-08-08: **minification is behaviour-preserving, so minified and expanded forms of
the same code are the same bot.** Applying that test does NOT pool the two no-orchard runs —
normalised they are 46,859 vs 55,116 chars, ~8,000 chars of genuinely different code. Also
verified: `readable__no_orchard` has **no minified twin committed anywhere**, so the readable file
IS the submitted artifact, not a reconstruction; and the orchard is genuinely absent (all nine
remaining `BANANA` references are generic plumbing — item index, enum, parse/format, cooldowns,
health params, carry lookup).

**Oscillation measured on owner expectation — confirmed, and inherited.** 34 D-1 episodes across
32/240 games, median 155 turns, worst **194 of 200**; 20 in the terminal ≥62-turn mode; unit 2
accounts for 25. Against the banana parent `a8eb3b2b`: 35 episodes / 32 games / 20 terminal / max
194 — and **the identical 32 of 32 (map, seat) pairs oscillate in both**. The oscillation is
therefore inherited from the shared E7a movement core and has **nothing to do with the orchard**,
which this bot lacks. Consistent with claude_1's D1-A root cause (same-tree contention against a
memoryless detour tie-break). **Stripping the orchard is not an oscillation fix.** The panel's
`GATE_UNREADY` ruling does not void this: it names D-9/P4 not D-1, the TRAIN defect touches only
`m040`, and `m040` contributes **zero** D-1 episodes in either run.
