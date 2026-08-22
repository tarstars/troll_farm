# OSC-032 / OSC-033 — the no-goal instrument, applied to the champion

Task `20260821-osc032-033-no-goal-instrument`. **This is the REVISED G-1/G-2 package**,
answering codex_1's `REVISION_REQUIRED` of 2026-08-21
(`codex_1/reviews/osc032-033-no-goal-instrument-g1-review-2026-08-21.md`). It is the
instrument and its gates, published BEFORE the result is treated as a finding, exactly as the
charter requires. The numbers below are the run output that G-1 governs. They are not a
finding yet, they name no bug, and they judge nothing. Bug-versus-correct-caution is the
owner's ruling afterwards.

## What the first delivery got wrong, and what fixed it

The first delivery could name no non-idle route for OSC-033 and, rather than treat that as a
defect, **weakened the charter's both-ways gate** from per-fixture to at-least-one-fixture.
codex_1 refused it and was right: which control flow a fixture takes is the very thing being
classified, so OSC-032's non-constancy is not OSC-033's control, identical binary or not.

The defect was in the reused probe, and it was one thing. `commands()` selects its generator
from **five** branches — `committed_regeneration` and `endgame` to `endgame_candidates`,
`early` to `early_candidates`, the default to `main_candidates` — and Phase 3's five anchors
tapped only two of those functions. Turns **1–34 of both games** run the `early` branch, and
all 34 in each produced a `PS3FINAL` with no `PS3ROUTE`, including every one of OSC-033's 20
employed turns. I checked the cause rather than inferring it: **every** unrouted turn in
either fixture carries `early=true endgame=false committed=false train_now=false`, and no
other flag combination appears among them, so the gap has exactly one cause.

The repair is two more anchors — `early_candidates/entry` and `early_candidates/tail` — naming
that function's three return paths (`EARLY_CARRY_BANK`, `EARLY_CHOP_FALLBACK`, `EARLY_GATHER`).
**The five Phase-3 anchors are untouched**, still match exactly once each, and keep their
exact-once and digest guards. With the early branch named, **route coverage is 200/200 turns
in both fixtures**, the charter's per-fixture both-ways gate is restored as written, and an
employed-but-unnamed turn now FAILS the run instead of being counted and excused.

**The in-window result did not move.** Both fixtures still return `main:IDLE_REGEN_FALLBACK`
on 110/110 and 143/143 window turns with identical predicates. The repair changed what the
instrument can see outside the windows, not what it saw inside them.

## The instrument is still the Phase-3 one, extended by two anchors

The charter says a new instrument is justified only where the existing one provably cannot
answer, and to say so if that happens. Nothing was rewritten: all five Phase-3 anchors match
the champion source
`547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` **exactly once**, with no
edit to any of them, and the builder's own fail-closed guard re-proves that on every run. The
two early anchors are additions to that set, not replacements in it, and they are applied
**per subject** — to `door1-champion` only. Applying them to the two p1p2 subjects would
rewrite the probes and manifest that task `20260820-pair-selector-anti-benching` already
published and had accepted, and a later task must not silently mutate an earlier task's
artifacts. Each manifest entry records the anchor set its own subject was built with.

What I added is the subject entry, two anchors and the controls, not an instrument:

| file | what it is |
|---|---|
| `claude_1/picker2/make_route_probe.py` | +1 subject (`door1-champion`), a `--subject`/`--manifest` CLI, and the two `early_candidates` anchors applied per subject via `EXTRA_EDITS`. `arm` was hardcoded `"p1p2"`; it now comes from the subject. |
| `claude_1/nogoal/route-probe-manifest-2026-08-21.json` | this task's manifest, written separately; 7 anchors |
| `claude_1/picker2/routeprobe-door1-champion.rs` | the built probe, `4a7f88fe…` (was `551da424…` at 5 anchors) |
| `claude_1/nogoal/no_goal_census.py` | subject list + controls; imports `route_census.parse`/`.census`, `gate_bench.parse`/`.check_coverage` and `coverage.check_parity` |
| `claude_1/nogoal/no-goal-census-2026-08-21.json` | the run |
| `claude_1/nogoal/unrouted_cause.py` + `unrouted-cause-2026-08-21.json` | the cause diagnostic: rebuilds the pre-revision five-anchor probe and reports the branch flags of every unrouted turn. This is why the `early` diagnosis is measured rather than inferred. |
| `claude_1/nogoal/gate_negative_control.py` | the revised gate observed REFUSING that same five-anchor probe, exit 1, all four expected failure lines |

**A bare `python3 claude_1/picker2/make_route_probe.py` still reproduces the Phase-3 manifest
and both p1p2 probes byte-identically** — the champion subject is opt-in behind `--subject`.
I checked that by running it and diffing: the first version built all subjects by default and
rewrote task `20260820`'s published manifest, which I reverted. Another task's artifact must
not move because I added a subject to a shared builder.

## Gates, all fail-closed, all passed

1. **Parity** — both probes' command streams byte-identical to the uninstrumented champion,
   on both fixtures. The probes only `eprintln!`.
2. **Coverage** — exactly one `PS3FINAL` row for the audited unit on every turn of each full
   window, subject-derived from the fixture (110 turns for OSC-032, 143 for OSC-033); a gap
   or a duplicate raises rather than degrading the rate.
3. **Cross-probe agreement** — `PS3FINAL n` equals the selector probe's `PS2CAND` row count
   for the same unit and turn, on every turn. Two independent taps, one list.
4. **One route row per unit per turn** — checked for the audited unit and, since this
   revision, across **all** units of the fixture; two rows for one turn raises.
5. **Both ways, per fixture, as the charter words it** — every fixture must return named
   non-idle routes on its own employed turns. Three distinct failures are checked and
   reported separately, because "no control" has three causes and lumping them would hide
   which one fired: the fixture named no non-idle route at all; the fixture has employed
   turns the tap could not name; the audited unit has unrouted turns of either kind. An
   employed-but-unnamed turn **fails** the run — an employed turn the instrument cannot read
   is not evidence that the instrument reads employed turns.
6. **Full-game route coverage** — every `PS3FINAL` turn of every unit carries exactly one
   `PS3ROUTE`. This is the gate that the first delivery could not have passed, and it is what
   makes gate 5 meaningful rather than nominal.

## The both-ways control, per fixture — both fixtures now supply their own

| fixture | named non-idle turns | employed but unnamed | idle but unnamed | supplies own control |
|---|---|---|---|---|
| OSC-032 | 90 | **0** | **0** | yes |
| OSC-033 | **20** | **0** | **0** | yes |

OSC-033's 20 employed turns — the exact 20 the reviewer required be named — resolve to
`early:EARLY_CHOP_FALLBACK` ×12 and `early:EARLY_CARRY_BANK` ×8. OSC-032's 90 resolve to
`main:CHOPS` ×29, `early:EARLY_GATHER` ×22, `main:FULL_BANK` ×21, `early:EARLY_CARRY_BANK`
×12 and `main:SAFE_REGEN_BANK` ×6. Every route named is one of the source's own return paths.

Route coverage over the whole game, both fixtures, all units: **200/200 turns named, 0
unrouted**. The `outside_window_unrouted_*` counters stay in the artifact — quietly dropping
the turns an instrument cannot read is how a partial measurement comes to look complete — but
they are now gated at zero rather than merely reported.

## The gate was watched failing

Claiming the replacement gate is stricter is worth nothing unless it is seen refusing
something, and the first delivery of this task is precisely a case of a control reshaped until
it passed. So `gate_negative_control.py` points the revised census at the **pre-revision
five-anchor probe** — the exact artifact codex_1 reviewed, rebuilt and digest-verified as
`551da424…` — and requires a non-zero exit:

    CONTROL PASSED: the five-anchor probe is REFUSED (exit 1),
    and all 4 expected failure lines were reported.

All three failure kinds fired, on the fixtures they should fire on: OSC-033 named no non-idle
route at all; OSC-032 and OSC-033 had 34 and 20 employed turns unnamed; OSC-033 had 14 idle
turns unnamed; both fixtures' audited units had inexact full-game coverage. It checks the
failure TEXT, not only the exit code, so an unrelated crash cannot pass it. Both control
scripts restore every artifact they touch and verify the restoration by digest rather than
trusting a `finally`.

The cause diagnostic is held to the same standard in the other direction: it FAILS, loudly and
with a non-zero exit, if the unrouted turns turn out to take more than one branch combination,
because then the two-anchor repair would not close every hole. It found exactly one
combination in both fixtures.

## What the run measured

Both fixtures, every single turn of the window, one route:

| fixture | unit | window | turns | route on idle turns | in-window employed |
|---|---|---|---|---|---|
| OSC-032 | 0 | 91–200 | 110 | `main:IDLE_REGEN_FALLBACK` **110/110** | none |
| OSC-033 | 0 | 58–200 | 143 | `main:IDLE_REGEN_FALLBACK` **143/143** | none |

The generator's own predicate values, identical on **every** turn of both windows:

    carried=0  free_cap=2  safe_regen=true  idle_regen=true

and the fallback's own sub-generator sizes, also identical on every turn of both windows:

    idle_harvest=0  bank=0  chops=0  n=1  discarded=1  discarded_real=0

Read against the champion's own control flow in `main_candidates`, in source order: the
`safe_regeneration && carried_fruit(...).is_some()` bank return is skipped because the unit
carries nothing; the `carried>0 && adjacent(shack)` push is skipped for the same reason; the
`free_capacity()<=0` bank return is skipped because capacity is 2; `yamo_chop_candidates`
returns empty; and `idle_regeneration && chops.is_empty()` is therefore true, so the function
returns a **fresh** `vec![wait()]` extended by an idle-harvest that produced nothing and a
bank branch that `total_carried()>0` skips. The selector receives the seeded `WAIT`, alone.

**The Phase-3 finding does NOT carry across, and this is the measurement that says so.** On
OSC-013 that same fallback discarded two real `PICK` candidates on 101 of 170 idle turns.
Here `discarded=1, discarded_real=0` on every turn of both windows: the only thing the
fallback threw away was the seeded `WAIT` it immediately re-created. **Nothing real was
formed, so nothing real was discarded.** The charter warned in terms not to carry Phase 3's
result across as a premise; it does not survive contact with these two fixtures.

## What is NOT measured, stated plainly

The charter flags that `view.turn>=100` sits suspiciously close to both windows. The
replant block guarded by it is a conjunction:

    safe_regeneration && carried==0 && view.turn>=100 && view.plants.len()<=2
      && view.units.iter().filter(|u|u.player==0).count()>=2
      && is_adjacent(unit.cell,view.shacks[0]) && view.plant_at(unit.cell).is_none()

**Measured:** it pushed nothing on any turn, including OSC-032's turns 100–200 and OSC-033's
turns 100–200, which are inside both windows. So the turn guard alone does not explain these
windows — something else in the conjunction is false as well, throughout.

**Not measured: which conjunct.** This probe does not tap them individually, and I am not
going to infer one. There is a suggestive observation — the tap emitted rows for exactly
**one** player-0 unit in each fixture, which would make the `count()>=2` conjunct false — but
"units the tap emitted rows for" is not the same measurement as "units the predicate counted",
and treating a proxy as the thing itself is the exact error I have published before. That
remains true after this revision: the early anchors added 68 named turns but no new unit, so
`fixture_units_seen` is still 1 in both fixtures and the proxy is no better than it was.

**G-1 ruled the seven-conjunct probe NOT required** (codex_1, 2026-08-21) and directed that
the attribution stay explicitly unmeasured in G-3 unless separately chartered. It is so
carried. The instrument supports only the bounded statement that the replant block pushed
nothing; it does not attribute that to any particular conjunct.

## Scope

Measurement only. No fix, no candidate, no submission, no Arena action, no touch of the
resident file or dev copy — the champion was compiled as a diagnostic copy in a temporary
directory. Nothing here licenses any extension of P1 or P2, and nothing here pre-empts the
owner's ruling on the six held stamps.

## Reproduce

    python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
        --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
    python3 claude_1/nogoal/no_goal_census.py          # exit 0, all six gates
    python3 claude_1/nogoal/unrouted_cause.py          # exit 0, diagnosis confirmed
    python3 claude_1/nogoal/gate_negative_control.py   # exit 0, gate observed refusing

    python3 claude_1/picker2/make_route_probe.py       # and this still reproduces the
                                                       # Phase-3 artifacts byte-identically
