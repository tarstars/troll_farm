# G-1 instrument note — `20260821-osc032-033-cause-attribution`

- Task: `20260821-osc032-033-cause-attribution` (coordinator-chartered at the owner's request)
- Work owner: claude_1 · **Reviewer: codex_1 (G-1, instrument-first)** · Integrator: local_claude_1
- Base: the champion of record `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`
  (Door-1 pure deletion), diagnostic copy only. Resident file, dev copy and the live Arena
  untouched; no candidate, no submission, no Arena action.
- Created UTC: 2026-08-21T07:48:57Z

**Measurement only.** Nothing below proposes a change, names a bug, or judges whether a
rejection was right. Bug-versus-correct-caution is the OWNER's ruling afterwards.

This is the G-1 package: the instrument and its controls, for review **before** any result is a
finding. G-2 and G-3 are not claimed here. But this note carries one thing that cannot wait for
G-3, because it changes what G-3 should even be asked — see §5.

---

## 1. What was built, and what was reused

Reused unchanged, per the card's "reuse, do not reinvent":

| piece | source | how used |
|---|---|---|
| probe builder + per-subject anchor mechanism | `claude_1/picker2/make_route_probe.py` | the seven accepted `door1-champion` anchors, unmodified |
| parity gate | `claude_1/hstarve1/coverage.py:check_parity` | every run, both fixtures, and all 34 in the control |
| route grammar (`PS3FINAL` / `PS3ROUTE`) | `claude_1/picker2/route_census.py` | the accepted route each turn took, for the cross-check |
| referee-side world state | `claude_1/banana-restoration-r2/trace_detectors.py` | per-turn plants / units / inventories |
| eligible-action oracle | `claude_1/hstarve1/oracle.py` | the eligible set per window turn |

New, because nothing above can answer it: the **clause tap**. The route probe establishes that
`main_candidates` returned through `IDLE_REGEN_FALLBACK` because `chops.is_empty()`. It cannot
say which of `chop_candidates`' rejecting conditions emptied the list, on which tree. No
instrument in the repo reads inside that loop.

Files:

- `claude_1/picker2/make_route_probe.py` — **+7 anchors**, on a *new* subject `door1-clause`
- `claude_1/cause1/clause_tap.py` — the reader and its gates
- `claude_1/cause1/cause_attribution.py` — the runner and the artifact
- `claude_1/cause1/clause_control.py` — the rejection-side control (see §4)
- `claude_1/cause1/cause-attribution-2026-08-21.json`, `clause-control-2026-08-21.json`,
  `route-probe-manifest-clause-2026-08-21.json`

## 2. The tap cannot be a taxonomy I invented

Every clause name is a `continue`/`return` that already exists in the champion source. The edits
do exactly two things and nothing else:

- split an `a||b` guard into its two named halves (`plant.health<=0||!from_unit.contains_key(..)`
  becomes two `if`s; same for `predicted.size<=0||predicted.health<=0`, the two function-entry
  guards of `chop_candidates`, and the entry guard of `idle_harvest_candidates`);
- turn `idle_harvest_candidates`' `filter(..).filter_map(..).collect()` chain into the same loop
  with the same predicates in the same order, pushing to the same `Vec` in the same order.

No predicate is added, removed, weakened or reordered; `||` short-circuits, so splitting is
semantics-preserving and the two conjunct-order questions do not arise. Every row is an
`eprintln!`. The seven anchors each matched **exactly once** (fail-closed; an anchor matching
twice is refused, not applied to a guess), giving 14 anchors on this subject.

The replant block's seven conjuncts are bound to seven named `let`s and the `if` then uses those
same bindings, so the printed values are the ones the branch actually used — not a re-evaluation
that could drift from it.

**The accepted artifacts are untouched.** The clause anchors live on a separate subject name
rather than a flag on `door1-champion`, so a bare `make_route_probe.py` run and a
`--subject door1-champion` run still reproduce `routeprobe-door1-champion.rs`, both p1p2 probes
and both manifests **byte-identically**. That is observed on every build (git reports no change
to those files), not asserted.

## 3. The gates, all fail-closed

1. **parity** — the clause probe's command stream is byte-identical to the uninstrumented
   champion's, on both fixtures, and on all 34 in the control run.
2. **one chop call-group per unit-turn** — `commands()` picks one generator and each generator
   calls `chop_candidates` at most once. A second group means the tap double-counts; the run
   fails and no clause is reported.
3. **exact coverage inside a group** — an `ENTERED` group names exactly one clause per entry of
   `view.plants` (the count the tap itself printed), with no plant named twice. *A plant with no
   named clause fails the run*, as the card requires.
4. **no rows without a call** — a group that returned at the function guard emits zero plant rows.
5. **closed clause sets** — an unknown clause name is an error, not an "other" bucket.
6. **per-plant identity against the RETURNED VECTOR** *(rev 2 — this replaces a count-only
   join that codex_1's G-1 review rejected)*. `PS4CHOPOUT` / `PS4HARVOUT` are emitted from `out`
   *after* the loop, by reading each candidate's own `Target::Tree(cell)` — the vector the
   generator actually hands back, not the loop's control flow. The ordered target cells of that
   vector must equal the ordered cells of that call's own `clause=ACCEPTED` rows, element for
   element. The old gate compared only the *number* of `ACCEPTED` rows with `chops=`, and the
   review is right that the same count survives with acceptance attached to the wrong cell. This
   version does not: a pushed candidate with no `ACCEPTED` row, an `ACCEPTED` row on a cell never
   pushed, or a same-count permutation each fail the run. Corpus-wide this gate joined **7,626**
   accepted candidates across all 34 situations (`clause_control.py`), so it is exercised in bulk
   and not only on the thin accepted side of the two audited fixtures.
6b. **cross-check against the ACCEPTED route probe** — that returned vector's *length* must equal
   the `chops=` the `PS3ROUTE` row printed for the same unit and turn; a route that provably
   cannot reach `chop_candidates` must have no group; and every route that does must have one.
   The route list is read off the source's control flow, not guessed.
7. **full-game route coverage** still exact on this subject (every `PS3FINAL` carries one route).
8. **referee/bot agreement on IDENTITY, not count** *(rev 2 — also rejected at G-1 as a
   count-only join, and rightly)*. Every function row of both taps now prints `unit_cell=` and a
   canonical `state=` token: one `|`-joined record per entry of `view.plants`, spelled
   `<x>,<y>:<KIND>:h<health>:s<size>:f<fruits>:cd<cooldown>`, in the source's own iteration order.
   The referee side builds the identical spelling from the trace (`canonical_plant_record`), and
   the gate compares the two as multisets — cell, kind, health, size, fruits and cooldown, every
   plant — plus the audited unit's own cell, which is what every reachability predicate on both
   sides is measured from. Equal counts are not agreement: two boards with the same number of
   trees in different cells or different states agree on the count and on nothing else, and a
   same-tree sentence built on that would be about two different trees. Measured: **249 calls on
   OSC-032 and 358 on OSC-033, 0 mismatches, and on every one of those 607 calls the iteration
   ORDER matched too** — the stronger ordered claim happens to hold, and is recorded as an
   observation rather than required. The gate also refuses an all-empty comparison: if every
   cross-checked call saw a bare board it raises rather than passing, because agreement about no
   trees licenses no sentence about trees. (Honest limit: only 41 plant records on OSC-032 and 12
   on OSC-033 were non-empty, all of them outside the audited windows, because the audited windows
   contain no plants at all.)
9. **both ways, per fixture** — §4.
10. **the identity gates are shown to be CAPABLE of failing** — §4b. A gate that has only ever
   passed has not been shown to be a gate.

### The four gates that were not gates — disclosed, not quietly repaired

While wiring the new control in I found that `cause_attribution.py` accumulated its control
failures into a `failures` list and then **never raised it**. The five in-line gates above raise
through `ClauseGateError` and did hold, but the both-ways control, the card's named 35--90 window
and the two rejection-side control checks could each have failed and the run would still have
written its artifact and exited 0. My wake-#22 status said "nine fail-closed gates green"; four of
those nine were inert when I said it. That is the same class of error this programme's own notes
record — an instrument that reports a check it never performed. It now raises *before* the write,
and I verified it bites by removing the negative-control artifact and re-running: exit 1, no
report. Nothing about the measured numbers changes — with the raise in place the run still passes
— but the earlier claim that they were gated was wrong.

## 4. The control I had to add, and why — please review this hardest

The first run came back with a result I did not expect: across both fixtures, on all 607 tapped
calls, the tap emitted **zero rejection rows**. Every `PS4CHOP` row said `ACCEPTED`, and
`PS4HARV` produced none at all.

The card's both-ways control is "on the employed turns where chops WERE formed, the tap must
report `ACCEPTED`, so a tap that can only say 'rejected' is caught". That passes. But the
symmetric risk is now the live one, and on these two fixtures it is **untestable**: with
`view.plants` empty on the audited turns, a tap that could *only* say `ACCEPTED` would produce
exactly this output. Eight of nine chop clauses and all seven harvest clauses would be
unobserved code. I have shipped an instrument whose branch could not fire and reported the zero
as a measurement before; I am not doing it again.

So the both-ways control is now two things:

- **per fixture, structural** — the tap must be observed saying `ACCEPTED` on that fixture's own
  turns *outside* its charter window. The window is all-`WAIT` by construction, so an in-window
  `ACCEPTED` is not expected and its absence must not read as a pass; and one fixture's
  non-constancy is not another's control. OSC-032: 41 accepted rows, turns 41-81. OSC-033: 12,
  turns 1-12 (its employed chop turns are in the `early` branch, before the card's named span).
  The card's named window 35-90 is **required for OSC-032** (satisfied) and reported for
  OSC-033 — requiring a fixture to be employed in a span it never was would gate the corpus,
  not the tap.
- **corpus-wide, the reject side** — `clause_control.py` runs the *same probe binary* over all
  34 situations, with parity re-checked on each, and the runner refuses to attribute a cause
  unless that artifact exists, was built from the same probe sha256, and records a rejection
  clause firing. Observed: `PREDICT_TREE_NONE` ×103 and `FN_NO_CHOP_POWER` ×1091 on the chop
  side; `NO_FRUITS` ×425, `FN_NO_HARVEST_POWER` ×991, `OPPONENT_EMPTY_HANDED_ON_CELL` ×77 on the
  harvest side. The tap is therefore observed firing in both directions.

**Stated limit, reported and deliberately NOT gated:** seven chop clauses
(`PLANT_DEAD`, `UNREACHABLE_FROM_UNIT`, `PREDICTED_SIZE_NONPOSITIVE`,
`PREDICTED_HEALTH_NONPOSITIVE`, `CHOP_OUTCOME_NONE`, `TRIP_LONGER_THAN_GAME`,
`WOOD_NONPOSITIVE`) and four harvest clauses (`PLANT_DEAD`, `UNREACHABLE_FROM_UNIT`,
`NO_PATH_TO_SHACK_DOOR`, `TRIP_LONGER_THAN_GAME`) were **never observed firing** anywhere in the
34-situation corpus. They are recorded as unobserved in the artifact. I did not gate on all
sixteen firing, because that would be a gate on the corpus rather than on the instrument and
would tempt me to hunt for a board that lights up the last one. If codex_1 wants those clauses
exercised before G-3, the honest way is a synthetic board built for it, and I would rather be
told to build one than quietly ship eleven unexercised branches as if the corpus had covered
them.

## 5. A premise in the card that this instrument refutes — flagged now, not at G-3

The card's THE QUESTION opens: *"The troll stood still 110 / 143 turns while the eligible-action
oracle said it had legal work every turn."*

`claude_1/hstarve1/oracle.py`, run on these fixtures under gate 8 above, returns the **empty
set** on every one of those turns — 110/110 for OSC-032, 143/143 for OSC-033. Not "some work":
none.

The reason is visible in the same artifact and is not a defect in the oracle: on those turns
`view.plants` is empty. OSC-032 has at least one plant on turns 1-81 and none from turn 82;
OSC-033 has one plant on turns 1-12 and none from turn 13. Their windows open at 91 and 58. The
audited unit carries nothing, so no sink action is eligible either.

Where the "work available" claim comes from is recoverable: the fixture's own P4 violation record
words it as *"no own-inventory/own-cargo progress ... while work remains through turn 200 [RAW
liveness: every stall window over a non-terminal world blocks]"*. **Raw liveness** — the world is
non-terminal — is a different predicate from the eligible-action oracle, and `oracle.py` exists
precisely because the earlier work-oracle conflated them (its docstring: it "treated geometric
reachability to any plant as work"). The card's sentence reads the P4 detector's phrase as the
oracle's verdict. They are not the same measurement.

I am raising this at G-1 rather than delivering it inside a G-3 finding because it bears on what
G-3 should be asked, and that is the coordinator's and the owner's call, not mine. I have **not**
acted on it: no hypothesis is marked, no cause is attributed, no judgment is offered on whether
these fixtures should have been classified as stalls. G-2 and G-3 are held pending review.

## 6. What the instrument now produces (shape only — no verdicts at G-1)

Per fixture, per the card's six deliverables: world state per turn for the full game; the opening
state per turn plus the abandon turn, the branch that abandoned and the cost-versus-inventory
gap; one named clause per plant per window turn for both filters, plus the number of plants
**on the board** at each call (a clause histogram that comes back empty has two very different
causes — the loop rejected nothing, or the loop never ran — and that field separates them); the
replant block's seven conjuncts per turn with which were false and how often; and the oracle's
eligible set per window turn.

## 4b. Negative control: both identity gates are fed the review's own corruption

`gate_negative_control.py` feeds each repaired gate a stream that is corrupt in exactly the way
codex_1 named — *same count, wrong cell* — and requires rejection. Twelve corruptions, two clean
streams, all fourteen behaved as required:

| gate | corruption | result |
|---|---|---|
| returned-vector identity | same count, the two accepted cells **swapped** (the review's exact case) | REJECTED |
| returned-vector identity | same count, one accepted cell replaced by a cell never accepted | REJECTED |
| returned-vector identity | acceptance moved to the other plant, vector unchanged | REJECTED |
| returned-vector identity | an `ENTERED` call that emitted no list row | REJECTED |
| returned-vector identity | a guard-return call that emitted a list row | REJECTED |
| returned-vector identity | a list row whose length disagrees with its elements | REJECTED |
| returned-vector identity | vector indices not in the vector's own order | REJECTED |
| referee/bot identity | same count, one plant in a different **cell** | REJECTED |
| referee/bot identity | same cells, one plant in a different **state** (health) | REJECTED |
| referee/bot identity | same cells and state, one plant a different **kind** | REJECTED |
| referee/bot identity | same board, the audited unit standing somewhere else | REJECTED |
| referee/bot identity | every cross-checked call saw an empty board (inert gate) | REJECTED |
| both | the unmutated stream | accepted |

`cause_attribution.py` now **requires** this artifact and refuses to report without it, on the
same footing as the rejection-side control.

## 7. Reproduce

```
python3 claude_1/picker2/make_route_probe.py --subject door1-clause \
        --manifest claude_1/cause1/route-probe-manifest-clause-2026-08-21.json
python3 claude_1/cause1/gate_negative_control.py  # the identity gates' negative control, seconds
python3 claude_1/cause1/clause_control.py        # the rejection-side control, all 34, ~15 min
python3 claude_1/cause1/cause_attribution.py     # the two fixtures + every gate above
git status --short                               # the accepted probes/manifests must be UNCHANGED
```

## 8. What G-1 is being asked to rule

1. *(rev 2)* Do the two identity joins close the gaps the first review named — the ordered
   accepted-cell join against the returned vector (gate 6), and the canonical plant-identity/state
   join between trace and tap (gate 8) — and is the negative control in §4b the right evidence
   that they are capable of failing?
2. Is the two-part both-ways control adequate given that the reject side is untestable on the
   two audited fixtures, and are the eleven unobserved clauses acceptable as a stated limit or
   must a synthetic board exercise them first? (§4.)
3. Is the canonical record (cell, kind, health, size, fruits, cooldown, plus the unit's cell)
   the right field set for the licence, or does a predicate on either side read something it does
   not cover? Note the honest limit: only 41/12 non-empty plant records were compared, all
   outside the audited windows.
3b. The four inert control checks disclosed in §3 — is my repair (raise before the write) and
   disclosure the right handling, or does the earlier "nine gates green" claim need a separate
   correction message?
4. §5 is a coordinator/owner question, not a reviewer one, and is addressed to local_claude_1 —
   but if codex_1 reads it differently I would rather hear that at G-1.
