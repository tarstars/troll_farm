# OSC-032 / OSC-033 — the no-goal instrument, applied to the champion

Task `20260821-osc032-033-no-goal-instrument`. **This is the G-1 package: the instrument and
its gates, published BEFORE the result is treated as a finding**, exactly as the charter
requires. The numbers below are the run output that G-1 governs. They are not a finding yet,
they name no bug, and they judge nothing. Bug-versus-correct-caution is the owner's ruling
afterwards.

## The instrument is the Phase-3 one, unmodified

The charter says a new instrument is justified only where the existing one provably cannot
answer, and to say so if that happens. It did not happen. All five of
`claude_1/picker2/make_route_probe.py`'s anchors match the champion source
`547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` **exactly once**, with no
edit to any anchor, and the builder's own fail-closed guard re-proves that on every run.

What I added is the subject entry and the controls, not an instrument:

| file | what it is |
|---|---|
| `claude_1/picker2/make_route_probe.py` | +1 subject (`door1-champion`) and a `--subject`/`--manifest` CLI. `arm` was hardcoded `"p1p2"`; it now comes from the subject. |
| `claude_1/nogoal/route-probe-manifest-2026-08-21.json` | this task's manifest, written separately |
| `claude_1/picker2/routeprobe-door1-champion.rs` | the built probe, `551da424…` |
| `claude_1/nogoal/no_goal_census.py` | subject list + controls; imports `route_census.parse`/`.census`, `gate_bench.parse`/`.check_coverage` and `coverage.check_parity` |
| `claude_1/nogoal/no-goal-census-2026-08-21.json` | the run |

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
4. **One route row per unit per turn.**
5. **Both ways** — see the limit below; it is the one gate whose shape I had to change.

## The gate I changed, and why — read this before the numbers

The charter words the both-ways control per fixture: *"employed turns of the same fixtures
must come back with non-idle routes."* That silently assumes each fixture HAS employed turns.

**OSC-033 does not** — and the precise reason matters, because I got it wrong once on the way
here and the artifact is what corrected me. OSC-033 carries a single unit. That unit **is**
employed on 20 turns outside its window. But on every one of those 20 turns the generator
returns through a path the five reused anchors **do not name**, so no non-idle route can be
NAMED for this fixture at all. "Supplies no both-ways control" therefore means *the tap named
no non-idle route here*, **not** *this unit never worked*. Failing the run on that would
condemn a working instrument for a gap in the reused probe's anchor set. I wrote the
per-fixture version first, watched it refuse OSC-033, and initially wrote that refusal up as
"idle on all 200 turns" — the artifact's own `outside_window_unrouted_employed_turns: 20` is
what caught it.

The control is therefore taken across the fixtures of this run, on the identical binary: at
least one must return named non-idle routes. **OSC-032 supplies it**
(`SAFE_REGEN_BANK` 6, `CHOPS` 29, `FULL_BANK` 21, all outside its window). Which fixtures
supplied it is recorded per fixture in the artifact, and the runner prints a `NOTE` naming
the weaker standing, so **OSC-033's result must not be read as carrying in-fixture both-ways
evidence — it does not have any.**

Outside-window turns for the audited unit, both fixtures, so the asymmetry is on the table:

| fixture | named non-idle | employed but unnamed | idle but unnamed |
|---|---|---|---|
| OSC-032 | 56 | 34 | 0 |
| OSC-033 | **0** | 20 | 14 |

That is a real reduction in control strength on one of the two fixtures, and it is the
reviewer's to weigh, not mine to smooth over.

Related, and reported rather than dropped: outside the audited windows some turns produce a
`PS3FINAL` with no `PS3ROUTE` — the unit left the generator through a path the five reused
anchors do not name. Those turns are **counted** in the artifact
(`outside_window_unrouted_*`), not skipped. In-window coverage is exact and separately gated.

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
and treating a proxy as the thing itself is the exact error I have published before. If G-1
wants that conjunct named, it is a one-line `eprintln!` of the seven booleans in the same
probe, gated the same way, and I will run it rather than argue it.

## Scope

Measurement only. No fix, no candidate, no submission, no Arena action, no touch of the
resident file or dev copy — the champion was compiled as a diagnostic copy in a temporary
directory. Nothing here licenses any extension of P1 or P2, and nothing here pre-empts the
owner's ruling on the six held stamps.

## Reproduce

    python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
        --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
    python3 claude_1/nogoal/no_goal_census.py
