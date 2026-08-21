# OSC-032 / OSC-033 — G-3: the per-turn route table and the finding

Task `20260821-osc032-033-no-goal-instrument`, gate **G-3**. The instrument and its six
gates were published first and **ACCEPTED_FOR_G3** by codex_1 on 2026-08-21
(`codex_1/reviews/osc032-033-no-goal-instrument-g1-revision-review-2026-08-21.md`);
the instrument itself is `claude_1/nogoal/instrument-note-2026-08-21.md`.

**Measurement only.** Nothing below names a bug, proposes a change, judges the route it
names, or claims anything about any other game. Bug-versus-correct-caution is the
**owner's** ruling afterwards. The acceptance authorized the instrument and nothing else.

- Base: the champion of record `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`
  (Door-1 pure deletion, KEPT by the owner 2026-08-21), compiled as a diagnostic copy in a
  temporary directory. No candidate, no submission, no Arena action, no touch of the
  resident file or the dev copy.
- Table: `claude_1/nogoal/route-table-2026-08-21.json` (one row per unit per turn, 200 turns
  per fixture, plus the contiguous spans below). Generator:
  `claude_1/nogoal/route_table.py` — a **reporter over the accepted probe**; it adds no tap
  and no gate, and it re-runs the parity and one-route-per-turn checks before it will print.
- Histogram artifact from G-1/G-2: `claude_1/nogoal/no-goal-census-2026-08-21.json`.

## The per-turn table, as contiguous route spans

Every turn of both full games is named; there are no unrouted turns and no turn with two
routes. `IN` marks the recorded window.

**OSC-032** — audited unit 0, recorded window turns 91–200, 200/200 turns named:

| | turns | count | list | route |
|---|---|---|---|---|
| out | 1–13 | 13 | work | `early:EARLY_GATHER` |
| out | 14–22 | 9 | work | `early:EARLY_CARRY_BANK` |
| out | 23–31 | 9 | work | `early:EARLY_GATHER` |
| out | 32–34 | 3 | work | `early:EARLY_CARRY_BANK` |
| out | 35–40 | 6 | work | `main:SAFE_REGEN_BANK` |
| out | 41–52 | 12 | work | `main:CHOPS` |
| out | 53–64 | 12 | work | `main:FULL_BANK` |
| out | 65–81 | 17 | work | `main:CHOPS` |
| out | 82–90 | 9 | work | `main:FULL_BANK` |
| **IN** | **91–200** | **110** | **idle** | **`main:IDLE_REGEN_FALLBACK`** |

**OSC-033** — audited unit 0, recorded window turns 58–200, 200/200 turns named:

| | turns | count | list | route |
|---|---|---|---|---|
| out | 1–12 | 12 | work | `early:EARLY_CHOP_FALLBACK` |
| out | 13–20 | 8 | work | `early:EARLY_CARRY_BANK` |
| out | 21–34 | 14 | **idle** | `early:EARLY_CHOP_FALLBACK` |
| out/**IN** | 35–200 | 166 | **idle** | **`main:IDLE_REGEN_FALLBACK`** |

"work" means the generator handed the selector a list longer than the seeded `WAIT`
(`n>1`); "idle" means it handed back `n=1`, the seeded `WAIT` alone.

## The named route, and its distribution

On **every turn of both recorded windows** — 110/110 and 143/143 — the list came back
through one return path and only one:

    main_candidates : IDLE_REGEN_FALLBACK      110/110 (OSC-032)   143/143 (OSC-033)

with the generator's own predicate values identical on every one of those turns:

    carried=0  free_cap=2  safe_regen=true  idle_regen=true

and the fallback's own sub-generator sizes identical on every one of those turns:

    idle_harvest=0  bank=0  chops=0  n=1  discarded=1  discarded_real=0

Read against the champion's control flow in `main_candidates`, in source order: the
`safe_regeneration && carried_fruit(..).is_some()` bank return is skipped because the unit
carries nothing; the `carried>0 && adjacent(shack)` push is skipped for the same reason;
the `free_capacity()<=0` bank return is skipped because capacity is 2; `yamo_chop_candidates`
returns empty; so `idle_regeneration && chops.is_empty()` is true and the function returns a
**fresh** `vec![wait()]`, extended by an idle-harvest that produced nothing and a bank branch
that `total_carried()>0` skips. The selector receives the seeded `WAIT`, alone.

## What was formed, and what was discarded

**Nothing real was formed, so nothing real was discarded.** On every window turn of both
fixtures `discarded=1, discarded_real=0`: the single thing the fallback threw away was the
seeded `WAIT` it immediately re-created. `idle_harvest`, `bank` and `chops` are all 0.

This is the point at which **Phase 3's finding does not carry across**, and the charter
warned in terms not to assume it did. On OSC-013 the same fallback discarded two real `PICK`
candidates on 101 of 170 idle turns. Here the discard is inert. These two cases are the same
*route* as Phase 3's and a different *event* on it.

## Two further measured facts

1. **OSC-032's stall onset coincides with the recorded window exactly; OSC-033's does not.**
   The window is the WAIT span of the *recorded* case. On the champion base, OSC-032's unit
   works through turn 90 (`main:FULL_BANK`, `carried=2 free_cap=0`, `bank=4`) and is idle from
   turn 91 — the window's first turn. OSC-033's unit stops at **turn 21**, 37 turns before its
   recorded window opens, and its first 14 idle turns come back through a *different* route,
   `early:EARLY_CHOP_FALLBACK` with `chops=0 n=1`, until the `early` branch ends after turn 34.
   Stated as measured: on this base the OSC-033 idle run is 180 turns through two routes, of
   which the recorded 143-turn window is the tail.
2. **The tap fires both ways in each fixture, on its own turns.** OSC-032 names 90 employed
   turns across five routes; OSC-033 names 20 across two. Full-game coverage is 200/200 in
   both. This is what makes the all-idle window a measurement rather than a silent tap.

## What is NOT claimed

- **No bug is named.** Returning a lone `WAIT` when no chop, no carry and no harvest exists
  may be correct caution or may be a defect. That is the owner's ruling and this artifact
  does not pre-empt it.
- **Which conjunct of the `view.turn>=100` replant block is false is NOT measured.** The
  block pushed nothing on any turn, including OSC-032's turns 100–200 and OSC-033's turns
  100–200, both inside their windows — so the turn guard alone does not explain these
  windows. Which of the other six conjuncts is also false is not tapped, and I do not infer
  it. There is a suggestive observation (the tap emitted rows for exactly one player-0 unit
  in each fixture, which would make `count()>=2` false), and "units the tap emitted rows for"
  is **not** the same measurement as "units the predicate counted"; treating that proxy as
  the thing itself is an error this programme has already published once. codex_1 ruled the
  seven-conjunct probe **not required** (2026-08-21) and directed the attribution stay
  explicitly unmeasured here. It is so carried.
- **No class-wide claim.** Nothing here says this happens in other games, in other fixtures,
  or on any base other than `547fa706…`. Two fixtures were measured; two fixtures are
  reported.
- **No causal claim about why `yamo_chop_candidates` was empty**, only that it was, on every
  window turn.
- **Nothing about the shelved P1/P2 cure or the owner's open extend-versus-replace design
  question**, which remain unruled and unstarted.

## Reproduce

    python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
        --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
    python3 claude_1/nogoal/no_goal_census.py     # exit 0, the six accepted gates
    python3 claude_1/nogoal/route_table.py        # exit 0, writes the per-turn table
