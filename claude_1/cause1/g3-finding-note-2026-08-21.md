# G-3 — OSC-032/033: why there was nothing to do, and whether a real game would have got there

Task `20260821-osc032-033-cause-attribution`, gate **G-3**. Work owner claude_1, reviewer
codex_1, integrator local_claude_1. Runs after **G-1 ACCEPTED** (`20260821T081645Z`) and
**G-2 ACCEPTED** (`20260821T084613Z`), and answers the coordinator's **amended** question
(`20260821T082713Z`, card at `6d50a8cb`).

**Measurement only.** No fix, no candidate, no behaviour change, no class-wide claim, and **no
bug-versus-correct-caution ruling** — that one is the owner's, afterwards. Nothing below
authorises an Arena action or touches the resident file or dev copy.

- Instrument: `claude_1/cause1/g3_finding.py` · artifact `claude_1/cause1/g3-finding-2026-08-21.json`
- Base: champion `547fa706…`, probe `64094f36fa70…` — the G-1/G-2-accepted pair, unchanged.
  `cause_attribution.py` and `g2_controls.py` re-run to byte-identical artifacts at this commit.

---

## The answer in one paragraph

On both fixtures **our own troll felled the last tree on the map**, and the map stayed bare for
the rest of the replay because **replanting requires two trolls and a second troll was
arithmetically impossible on these maps from turn 1** — the cheapest second troll the opening can
ever ask for costs PLUM 2 / LEMON 2 / APPLE 1, and each map is missing a kind that never grew on
it at all. And **no real game would have reached the audited windows**: the referee's own end
condition fires on the first bare turn in both fixtures, **turn 82** (OSC-032) and **turn 13**
(OSC-033), while the windows open at 91 and 58. The harness ran to a fixed 200 turns and never
asked.

---

## 1. When and how the map went bare

| | OSC-032 | OSC-033 |
|---|---|---|
| last plant-bearing turn | **81** | **12** |
| the last plant | LEMON `(8,5)`, size 4, health 1, **3 fruits on it** | APPLE `(8,3)`, size 4, health 1, **3 fruits on it** |
| felled by | **OWN_UNIT_CHOP** | **OWN_UNIT_CHOP** |
| evidence | trace command turn 81 `CHOP 0`, audited unit standing on `(8,5)`, chop_power 1, plant health 1 | trace command turn 12 `CHOP 0`, audited unit standing on `(8,3)`, chop_power 1, plant health 1 |
| first bare turn | 82 | 13 |
| bare turns in the harness | 119 | 188 |
| **shack inventory at that moment** | LEMON 2, BANANA 1 | APPLE 1, BANANA 1 |
| **was replanting materially possible?** | yes — seed material was in the shack | yes — seed material was in the shack |

Attribution is taken from an actual `CHOP` command with the unit on the plant's own cell, never
from the unit merely standing there. Where no own command explains a disappearance the instrument
records `UNATTRIBUTED_OWN_SIDE` and says so: **the transcript carries our side's commands only**,
so "the opponent did it" is not observable here and is never claimed. On these two fixtures both
deaths are directly command-evidenced, so nothing rests on that fallback.

For OSC-033 this was the **only plant of the entire game**.

## 2. Would a real game have reached those turns? No.

Computed with the frozen port `sim.engine.has_stalled` (`sim/engine.py:71`; Rust original
`rust/src/game/engine.rs:819`, referee v1.0.5 `Board.hasStalled`), unmodified and unwrapped — the
instrument builds a real `sim.state.GameState` from the referee trace and hands it over, and
takes scores from `sim.engine.recompute_scores` rather than any formula written here.

| | OSC-032 | OSC-033 |
|---|---|---|
| referee ends at turn (full rule) | **82** | **13** |
| reason | `mercy_player_1` | `mercy_player_1` |
| grace counter remaining when it fired | 14 | 13 |
| conservative bound: grace counter **alone** | 96 | 26 |
| harness horizon | 200 | 200 |
| turns played past the referee's end | **118** | **187** |
| audited window | 91–200 (110 turns) | 58–200 (143 turns) |
| **window turns a real game would have played** | **0 of 110** (5 of 110 under the grace-only bound) | **0 of 143** (0 under either) |

**So 110/110 and 143/143 of the "idle turns" are a harness artifact** — under the conservative
grace-only bound, still 105/110 and 143/143. The harness runs
`regression_tests.run_binary_custom` for a fixed `cfg["turns"]` and never calls a stall check;
that is why the replay reaches turns the referee would not have played.

**Scope, stated because it matters.** The full rule ends both games by the **mercy** clause,
which depends on the *opponent* being stuck and behind. In these replays every opponent unit had
`chop_power 0` on all 200 unit-turns and banked nothing — that is the frozen situation's own
opponent profile, not an arbitrary Arena opponent. **The grace-only bound (96 / 26) does not
depend on the opponent at all** and is the number to quote if the opponent is in doubt. Either
way the conclusion for OSC-033 is unchanged, and for OSC-032 it moves from 0 to at most 5 real
window turns out of 110.

One consequence worth naming: OSC-033's opening is abandoned at turn 35, which is itself **past**
that fixture's referee end turn of 13. The *cause* below is a property of the map from turn 1, so
it survives the restriction to turns 1–12, but the abandonment **event** is a harness event there.

## 3. The opening — H-A

The deadline (`enforce_training_deadline`, `candidate-door1.rs:908`) is reached at turn 35 in
both; `strongest_affordable` returns `None`, so `opening_abandoned` is set with reason
`NO_AFFORDABLE_OPTION`. Shortfalls at that moment: OSC-032 PLUM 2 / LEMON 1 / APPLE 1;
OSC-033 PLUM 2 / LEMON 2.

**The floor, derived from the source rather than assumed.** `opening_options` (`:842`) enumerates
movement_speed 1..=3, carry_capacity 1..=max, chop_power 1..=max with **harvest_power fixed at
0**; `training_cost` (`bot/main.py:128`) charges `n + stat²` with `n` = own unit count. With
`n = 1` the cheapest second troll under *any* stats is **PLUM 2, LEMON 2, APPLE 1** — APPLE
because `n` alone already costs 1 at harvest_power 0. IRON is charged only when `view.iron` is
non-empty (`training_affordable`, `:899`); it is empty on both maps.

| measured over the whole replay | OSC-032 | OSC-033 |
|---|---|---|
| best the shack ever held | PLUM 0, LEMON 2, APPLE 0 | PLUM 0, LEMON 0, APPLE 1 |
| kind ever alive on the map | PLUM yes, LEMON yes, APPLE **no** | PLUM **no**, LEMON **no**, APPLE yes |
| **no live source ever existed for** | **APPLE** | **PLUM, LEMON** |
| turns an opponent stood on a source (pre-deadline) | **0 of 34** | 0 of 34 (no source to stand on) |
| opponent chop_power, all unit-turns | 0 | 0 |

**H-A: CONFIRMED in its "absent" half, REFUTED in its "denied" half.**

- The opening could not be completed, and could not have been completed on any turn under any
  stats: each map lacks a kind the floor requires and that never grew on it. **A second troll was
  impossible from turn 1**, not merely missed by the deadline.
- The denial half is refuted by measurement, not by argument: **no opponent unit stood on a
  source on any of the 34 pre-deadline turns** in either fixture, and every opponent unit had
  chop_power 0 throughout.

**One thing I measured and am NOT explaining.** On OSC-032 a fruiting PLUM stood reachable on all
34 pre-deadline turns and **the shack still ended on zero plums** — the map could have paid PLUM
and did not. The instrument reports a one-fruit round-trip *lower bound* (walk to the tree at
speed 1, one HARVEST, walk to a shack door, one DROP: earliest bank turn 29 for plum from turn 1,
23 for lemon from turn 7) — both **inside** the deadline, so the bound settles nothing and must
not be read as "there was time". Why no plum was banked is not measured here and is not claimed.
It does not change the verdict, because APPLE was unobtainable regardless.

## 4. The replant block — H-B

Full game, not just the window (the amendment asked whether any *other* conjunct was false):

| | OSC-032 | OSC-033 |
|---|---|---|
| replant rows measured | 160 | 166 |
| **`c5_own_units_ge_2` false** | **160 / 160** | **166 / 166** |
| only always-false conjunct | `c5_own_units_ge_2` | `c5_own_units_ge_2` |
| turns where **c5 was the only** false conjunct | 101 | 101 |
| other conjuncts false on some turns | `c3_turn_ge_100` 59, `c6_adjacent_shack` 46, `c2_carried_zero` 21, `c7_cell_free` 12 | `c3_turn_ge_100` 65 |
| turns all seven true | **none** | **none** |

**H-B: CONFIRMED.** `c5_own_units_ge_2` is the only conjunct false on *every* measured turn, so a
one-troll bot never passes the replant block. H-B reads **"the ≥2 rule alone"** on 101 turns of
each fixture and **"the ≥2 rule plus X"** on the remaining 59 / 65, where X is `c3_turn_ge_100`
(and on OSC-032 also `c6_adjacent_shack`, `c2_carried_zero`, `c7_cell_free`). Removing the ≥2
rule alone would therefore not have produced a replant on those 59 / 65 turns — but it is the
only conjunct that blocked *all* of them.

## 5. The chop clauses — H-C, and deliverable 3 where it is not vacuous

Inside the windows `view.plants` is empty on every audited turn, so H-C is **inapplicable there**
— the coordinator's amendment already ruled this and I do not re-argue it. Outside the windows,
where plants exist, deliverable 3 has content, and here is its honest denominator:

| | OSC-032 | OSC-033 |
|---|---|---|
| plant-bearing turns | 81 | 12 |
| turns the chop generator entered the loop | 29 | **12 (all of them)** |
| accepted plant rows | 41 | 12 |
| **rejected plant rows** | **0** | **0** |
| rejection clauses seen | none | none |
| turns H-C is **UNOBSERVED** | **52** | 0 |
| what the bot was doing on those 52 | `early:EARLY_GATHER` 22, `early:EARLY_CARRY_BANK` 12, `main:FULL_BANK` 12, `main:SAFE_REGEN_BANK` 6 | — |

**H-C: REFUTED where observed; UNOBSERVED on 52 of OSC-032's 81 plant-bearing turns.** Not one
tree was rejected by a named clause anywhere on either fixture. On OSC-033 that is the *whole*
fixture — 12 of 12 plant-bearing turns asked and accepted — so H-C is refuted outright there. On
OSC-032 the 52 unasked turns are turns the bot returned by an **earlier, productive route**
(gathering or banking), not turns it stood idle; the clause question was never put, so those
turns refute nothing and confirm nothing.

The **eleven unobserved clauses** remain a binding limit on any positive clause claim, per
codex_1's G-1 ruling. Nothing here claims a clause fires that was not seen firing.

---

## 6. Owner brief, plain words

**Why was there nothing to do?** Because there was nothing left on the map, and our own troll is
what took the last of it off. In both games our troll chopped down the map's last tree — a
size-4 tree carrying 3 fruits, on 1 health, standing under it — and from the next turn on there
was no plant anywhere. The shack had seed material in it both times. It could not replant,
because replanting asks for two trolls and there was one.

**Why was there only one troll?** Not because the bot missed a deadline. The cheapest second
troll it is allowed to ask for costs 2 plums, 2 lemons and 1 apple. OSC-032's map has a lemon
tree and a plum tree and **no apple tree at all**; OSC-033's map has one apple tree and **no plum
and no lemon at all**. On both maps the second troll was unaffordable on turn 1 and stayed
unaffordable on every turn after it. The turn-35 abandonment is the bot noticing, not the bot
failing.

**Was it the opponent's doing?** No. No opponent unit stood on a source tree on any turn before
the deadline, and every opponent unit had zero chop power all game.

**And would a real game even have got there?** No. The referee stops a game once the plants are
gone. On OSC-032 it stops at turn 82, on OSC-033 at turn 13 — and the stretches you were shown
start at turn 91 and turn 58. **Every one of those 110 and 143 idle turns is the test harness
running past the end of the game**; on the most conservative reading that ignores the opponent
entirely, at most 5 of OSC-032's 110 turns and none of OSC-033's are real.

**Not claimed.** Whether any of this is a bug or correct caution — that is yours, and this note
does not touch it. Not claimed either: why OSC-032 never banked a plum though one was reachable
all 34 pre-deadline turns; whether felling the last tree was wrong; whether any of this happens
in other games (two fixtures, no corpus claim); and anything at all about the 52 OSC-032 turns
where the chop generator was never asked.

---

## Controls, and what would have caught a wrong answer

- **Parity** and the five clause-tap gates and the referee/tap **identity** agreement gate: the
  G-2-accepted gates, re-run unchanged on this commit.
- **Adapter fidelity, every turn:** the `sim.state.GameState` handed to the frozen predicate must
  match the referee trace by plant canonical record, unit `(id, player, cell, ms, carry)` and
  **both** inventories. Had the adapter dropped plants, "the game ended at once" would have been
  the artifact and would have looked exactly like the finding.
- **Stall non-vacuity, per fixture:** `has_stalled` must be observed returning False on a
  plant-bearing turn *and* True on a bare one, or no end turn is reported.
- **Stall predicate control:** four constructed states, two that must stall and two that must
  not — grace counter positive with a unit on a plant, grace expiry, the fruit-held escape, and
  both-stuck. 4/4.
- **Attribution is command-evidenced or it is not made.**
- **Deliverable 3 refuses to report a vacuous per-plant attribution:** the run fails unless at
  least one out-of-window call saw a real plant.
- **The `never held enough` / `no live source ever existed` split** is kept apart deliberately.
  Collapsing them would have put OSC-032's PLUM — reachable and fruiting for 34 turns — into
  "the map could never pay", which is false and would have made H-A look stronger than it is.
