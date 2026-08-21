# claude_1 status — wake #25, 2026-08-21

Task `20260821-osc032-033-cause-attribution`: **ALL THREE GATES DELIVERED.** G-1 ACCEPTED, G-2
ACCEPTED, **G-3 delivered this wake** at `e8034b79` (handoff `20260821T090248Z`, commit
`62b0520d`). Queue drained: 0 new, 0 ack-required, and — for the first time in three wakes — no
card of mine outstanding.

## What arrived, and what it unblocked

Five messages, none ack-required, all read in full:

- **codex_1 `20260821T084613Z` — G-2 ACCEPTED.** Reproduced `58ea9a72` independently. Ruled all
  three of my G-2 questions: the card's named both-ways control is OSC-032's 29 `main:CHOPS`
  turns and their route set equals the tap's accepted-tree set exactly; OSC-033's 12
  early-branch accepted rows are **valid supplementary evidence, not the card's named control**,
  and I must not describe them as such; the empty audited boards make in-window per-plant
  coverage **vacuous but not incomplete**; the count-preserving cell mutation and the
  out-of-window planted control are correctly constructed and honestly scoped. That ack also
  discharged the three deferred cards visible to them.
- **codex_1 `20260821T084614Z`** — stale-library README disposition read and recorded; nothing
  assigned.
- **local_claude_1 `20260821T084501Z`** — receipts on all three G-3 cards; r3 is the live one;
  the G-2 questions are codex_1's to rule and the coordinator withholds an opinion. My
  `supersedes`-only retirements noted, no action.
- **local_claude_1 `20260821T084502Z`** — stale-library card DELIVERED and accepted, verified by
  execution. One thing for me, explicitly **not** a card: `build_oscillation_library.py`'s default
  `--out` still points at the STALE tree, so a default run would overwrite it and make the README
  false. My module, my call. **Open, carried to the next wake.**
- **local_claude_1 `20260821T084239Z`** — 4b CLOSED; OSC-026 and OSC-012 ruled BUG by the owner;
  all six 4b candidates were bugs and no "harmless" stamp was issued. Nothing chartered.

## G-3 delivered — the finding

Artifacts `claude_1/cause1/g3_finding.py`, `g3-finding-2026-08-21.json`,
`g3-finding-note-2026-08-21.md` at `e8034b79`. Measurement only; no fix, no candidate, no
class-wide claim, and **no bug-versus-correct-caution ruling** — the owner's.

**In one sentence:** on both fixtures our own troll felled the last tree on the map, it could not
replant because replanting needs two trolls and a second troll was impossible from turn 1, and
**no real game would have reached either audited window.**

- **Map went bare.** OSC-032: LEMON `(8,5)`, health 1, 3 fruits on it, felled turn 81, bare from
  82. OSC-033: APPLE `(8,3)`, health 1, 3 fruits — **the only plant of the whole game** — felled
  turn 12, bare from 13. Both `OWN_UNIT_CHOP`, evidenced by the trace command `CHOP 0` with the
  unit on the plant's own cell. Standing on the tree is not accepted as evidence, and the
  opponent is never named a feller: our transcript carries our side's commands only. Shack held
  seed material both times (LEMON 2 + BANANA 1; APPLE 1 + BANANA 1).
- **The referee's own end turn**, from the frozen `sim.engine.has_stalled` (`sim/engine.py:71`,
  Rust original `rust/src/game/engine.rs:819`), unmodified and unwrapped: **82** and **13**,
  reason `mercy_player_1`, 14 / 13 grace turns still in hand. Harness horizon 200 → **118 / 187
  turns past the end**; **0 of 110 and 0 of 143 window turns** would have been played. The
  conservative **grace-only bound** (which does not depend on the opponent) is **96** and **26**,
  giving 105/110 and 143/143. I quote the conservative one where the opponent could matter — the
  mercy clause turns on this replay's opponent having `chop_power 0` on all 200 unit-turns.
- **H-A CONFIRMED in its "absent" half, REFUTED in its "denied" half.** Source-derived floor: any
  second troll costs at least PLUM 2 / LEMON 2 / APPLE 1 (`opening_options` ms 1..3 / cc 1..max /
  chop 1..max with harvest_power 0, × `training_cost` `n + stat²`, n=1; iron uncharged, both maps
  ironless). OSC-032 has **no apple tree ever**; OSC-033 has **no plum and no lemon ever**. 0 of
  34 pre-deadline turns had an opponent on a source.
- **H-B CONFIRMED.** `c5_own_units_ge_2` false 160/160 and 166/166, the only always-false
  conjunct, all seven never simultaneously true — but it was the **sole** false conjunct on only
  101 turns of each; on the other 59 / 65 `c3_turn_ge_100` (and on OSC-032 `c6_adjacent_shack`,
  `c2_carried_zero`, `c7_cell_free`) was also false. "The ≥2 rule alone" on 101, "plus X" on the rest.
- **H-C REFUTED where observed, UNOBSERVED on 52 turns.** Zero rejected plant rows anywhere on
  either fixture. OSC-033 complete (12 of 12 plant-bearing turns asked, all accepted); OSC-032
  asked on 29 of 81, the other 52 spent on productive routes so the clause question was never
  put. The eleven unobserved clauses remain a binding limit.

**Controls.** The stall projection carries three, because it is the whole of question 2:
per-turn adapter fidelity against the referee trace (plants by canonical record, units by
`(id, player, cell, ms, carry)`, both inventories), non-vacuity per fixture (must be seen both
False-with-plants and True-when-bare), and a 4-case predicate control covering the grace counter,
grace expiry, the fruit-held escape and both-stuck. All raise before the write.

**One label I got wrong and fixed before publishing**, disclosed: the min-cost block first put
OSC-032's PLUM under "items the map could never pay". False — a fruiting plum was reachable all
34 pre-deadline turns and the shack simply never held one. `items_the_shack_never_held_enough_of`
and `items_no_live_source_ever_existed_for` are now kept strictly apart; collapsing them made H-A
look stronger than it is. Why no plum was banked is **not measured and not claimed**.

## Transport — the `ack_for` rule, applied correctly this time

The r3 card was discharged by naming it in the delivery handoff's **`ack_for`**, and the post-mark
sweep reads 0 ack-required. Twice on 2026-08-21 I retired a card with `supersedes` alone, which is
inert. The countermeasure that worked is mechanical, not cognitive: read the predecessor's path
back out of `ack_for` before publishing. `supersedes` is bookkeeping with no transport effect.

The lint also refused this handoff once, correctly: a line-start `DEFERRED:` in the body triggers
the deferral-shape gate (self-address required) even when the sentence says "none". Use
"Deferrals: none." Suite 127 pass (`uvx pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py`);
`scripts/` and `tests/` verified identical to **both** `origin/main` and
`origin/agent/local_claude_1` at the start of this wake.

## Open, carried forward — no card needed, no card outstanding

- **`build_oscillation_library.py`'s default `--out` points at the STALE parent-lineage tree.**
  Raised by the coordinator as explicitly not a card. A default run would overwrite the STALE
  directory with fresh output and make its README false. Mine to move or guard.
- **G-3 is under review by codex_1.** If it returns REVISION_REQUIRED I card the revision then;
  until then there is nothing deferred and nothing owed.
- Not authorised by anything this wake: any fix, candidate, behaviour change, class-wide claim or
  Arena action. The bug-versus-correct-caution ruling on OSC-032/033 is the owner's.
