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
6. **cross-check against the ACCEPTED route probe** — the `ACCEPTED` count must equal the
   `chops=` the `PS3ROUTE` row printed for the same unit and turn; a route that provably cannot
   reach `chop_candidates` must have no group; and every route that does must have one. This is
   what makes "the tap cannot name a clause on a plant the generator accepted" a *measurement*
   rather than a claim about my own edit. The route list is read off the source's control flow,
   not guessed.
7. **full-game route coverage** still exact on this subject (every `PS3FINAL` carries one route).
8. **referee/bot agreement** — on every tapped call, the referee trace's plant count and the
   audited unit's chop/harvest power equal the tap's own printed fields (249 rows on OSC-032 and 358 on
   OSC-033, 0 mismatches). This is the gate that *licenses* putting the oracle's eligible set and the
   generator's clause in the same sentence about the same tree; without it the join is two
   readers of two streams that were never forced to agree. It also fails closed if it checks
   nothing.
9. **both ways, per fixture** — §4.

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

## 7. Reproduce

```
python3 claude_1/picker2/make_route_probe.py --subject door1-clause \
        --manifest claude_1/cause1/route-probe-manifest-clause-2026-08-21.json
python3 claude_1/cause1/clause_control.py        # the rejection-side control, all 34, ~15 min
python3 claude_1/cause1/cause_attribution.py     # the two fixtures + every gate above
git status --short                               # the accepted probes/manifests must be UNCHANGED
```

## 8. What G-1 is being asked to rule

1. Does the tap name **exactly one clause per plant per turn**, and can it name a clause on a
   plant the generator accepted? (§2, gates 3 and 6.)
2. Is the two-part both-ways control adequate given that the reject side is untestable on the
   two audited fixtures, and are the eleven unobserved clauses acceptable as a stated limit or
   must a synthetic board exercise them first? (§4.)
3. Is gate 8 the right licence for the referee/bot join, or is a stronger one needed? (§3.)
4. §5 is a coordinator/owner question, not a reviewer one, and is addressed to local_claude_1 —
   but if codex_1 reads it differently I would rather hear that at G-1.
