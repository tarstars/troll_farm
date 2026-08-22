# 20260821-osc032-033-cause-attribution — WHY the chop list was empty, and why there was only one troll

- Status: **CLOSED — DELIVERED 2026-08-21** (G-1 rev 2 `2764db56` ACCEPTED 08:16Z;
  G-2 `58ea9a72` ACCEPTED 08:46Z; G-3 `e8034b79` ACCEPTED 09:07Z) and **OWNER-RULED
  ~09:25Z: UNPLAYABLE** — the real game ends at the first bare turn (82 / 13), none
  of the idle turns exist; our own troll felled the last fruiting tree with seeds
  in the shack, the lone troll barred from replanting by the bot's `own units >= 2`
  rule; second troll unaffordable from turn 1 (map lacked a fruit kind), denial
  refuted. Record: `local_claude_1/adjudications/OSC-032-033-ruling-2026-08-21.md`.
  Chartered 2026-08-21 at the owner's request ("check my idea" + "coordinate the
  bots"), as the follow-up the G-3 brief of
  `20260821-osc032-033-no-goal-instrument` itself named.
- Record owner: local_claude_1 · Work owner: **claude_1** (instrument) ·
  Reviewer: **codex_1** (instrument-first) · Integrator: local_claude_1
- Area: oscillation verdict residue, branch **4b**, bucket F (iteration pool #6)
- Base: the **current champion** `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`
  (Door-1 pure deletion), diagnostic copy only. Resident file, dev copy and the
  live Arena untouched; no candidate, no submission. Session 3 owns the Arena.
- Created UTC: 2026-08-21T07:40:00Z
- Predecessor (CLOSED, all gates accepted): `20260821-osc032-033-no-goal-instrument`
  — it established that on every window turn the main generator returned one
  seeded `WAIT` via `IDLE_REGEN_FALLBACK` with `chops.is_empty()`, and that the
  probe saw **exactly one own unit for the whole game in both fixtures**
  (`fixture_units_seen = 1`). It deliberately did NOT measure why the chop list
  was empty. This task measures that.

## THE QUESTION (owner's, plain words) — AMENDED 2026-08-21 ~08:35Z after G-1

~~The troll stood still 110 / 143 turns while the eligible-action oracle said it
had legal work every turn.~~ **Premise WITHDRAWN by the coordinator** (claude_1's
G-1 §3, `20260821T075136Z`): under the accepted instrument the eligible-action
oracle returns the EMPTY set on 110/110 and 143/143 window turns because
`view.plants` is empty there (OSC-032: plants on turns 1–81, none from 82;
OSC-033: one plant on turns 1–12, none from 13; windows open at 91 and 58). The
"work available every turn" figure in the 4b package came from the fixture's
raw-liveness predicate ("the world is non-terminal"), not from the oracle; the
card conflated the two. The bot's chop filter therefore had **no tree to
reject** inside the windows — H-C cannot apply to the windows themselves.

The question G-3 must now answer, in this order:

1. **When and how did the map go bare?** Per fixture: the last plant's death
   turn, kind, who felled it (own unit / opponent / never felled — e.g. the
   fixture's initial plant set), and whether a seed or fruit was in the shack
   inventory at that moment (i.e. was replanting possible at all).
2. **Does the real referee end the game when no plant exists** (`hasStalled`
   semantics — the mechanics note says the stall check returns false *while
   plants exist*)? If yes: the turn each fixture would have ended in a real
   game, and therefore how many of the 110/143 "idle turns" are simulator
   artifact. This decides whether the owner is ruling on a real-game behaviour
   or a harness one. Cite the referee source, not the note.
3. **The opening:** abandoned at turn 35 in both (instrument output) — the
   missing training item(s), whether a reachable live source of each existed on
   any turn before 35, and whether the opponent's presence on it was the reason
   (the owner's denial hypothesis H-A: CONFIRMED / REFUTED / NOT SEPARABLE).
4. **The replant block:** all seven conjuncts per turn; `c5_own_units_ge_2` is
   always false (instrument output) — state whether any OTHER conjunct was also
   false, so H-B is "the ≥2 rule alone" or "the ≥2 rule plus X".
5. Deliverables 1, 3, 5 of the original goal stand (world state per turn,
   clause per plant per turn OUTSIDE the windows where plants exist, the oracle's
   set per turn). Deliverable 6 (the owner brief) now answers: *why was there
   nothing to do, and would a real game even have reached those turns.*

Three hypotheses travel with the card. They are to be CONFIRMED or REFUTED by
measurement; none is a premise and none may be reported as true without its
evidence line:

- **H-A (owner's idea):** the opening ("collect resources for the second troll")
  could not be completed because the needed fruit kinds (plum / lemon, per
  `training_cost`) were denied or absent in reach; the opening was abandoned at
  the hard deadline and the bot never trained a second troll. *Code note for the
  instrument, not a finding:* `enforce_training_deadline` can abandon (sets
  `opening_abandoned`, permanent) or, under `require_preferred`, keep waiting;
  the route table shows the `early` branch ending after turn 34 in both
  fixtures, so "stuck in the phase forever" is already refuted by the predecessor
  — what remains open is whether the phase FAILED (abandoned) and why.
- **H-B:** a one-troll bot can never replant: the replant block in
  `main_candidates` requires `own units >= 2` (one of its seven conjuncts). If
  the map had no live tree, "nothing to do" follows from H-A + this conjunct.
- **H-C:** a live reachable tree existed (the oracle's claim) but every such tree
  failed a chop clause: predicted size 0 → `wood <= 0`; `predict_tree` None
  (opponent chopping it); `chop_outcome` None; `chop_power <= 0`; unreachable;
  trip longer than the remaining game. And for harvesting, `idle_harvest_candidates`
  failed on: carrying / `harvest_power <= 0` / no fruits / empty-handed opponent
  on the cell / no path to a shack door / trip too long.

## THE GOAL — a cause statement per fixture, neutral words

For each fixture, on the champion re-run, for every turn of the full game (not
only the window), deliver:

1. **World state per turn:** own unit count; the audited unit's stats (speed,
   capacity, harvest power, chop power), cell and carry; every plant (cell, kind,
   size, health, fruits, cooldown) with its BFS reachability from the audited
   unit; the shack inventory (plum/lemon/apple/banana/iron/wood); opponent
   units' cells and carry.
2. **Opening state per turn:** `desired_second`, `training_affordable`,
   `train_now`, `opening_abandoned` (and the turn it flipped), the missing
   item(s) of the training cost and whether a reachable live source of each
   existed (plant of that kind with health > 0 / iron).
3. **Per plant per window turn, the rejecting clause** of `chop_candidates` /
   `yamo_chop_candidates` and of `idle_harvest_candidates` — one named clause per
   plant per turn, fail-closed (a plant with no named clause fails the run).
4. **The replant block's seven conjuncts per turn** (the one measurement the
   predecessor's reviewer ruled not required THERE; it is required HERE because
   H-B turns on it — codex_1's earlier ruling is not contradicted, this card's
   question is different).
5. **The oracle's eligible action set per window turn** (HARVEST / CHOP / BANK /
   PLANT, from `claude_1/hstarve1/oracle.py`), so "work was available" and "the
   bot said no" are finally the same sentence about the same tree.
6. **The owner brief in plain words:** which hypothesis the data supports, with
   the one number per claim; an explicit "not claimed" section. **No
   bug-versus-correct-caution ruling** — that is the owner's, afterwards.

## What to build — reuse, do not reinvent

- Probe builder and gates: `claude_1/picker2/make_route_probe.py` (subject
  `door1-champion`, its seven accepted anchors untouched), `claude_1/nogoal/no_goal_census.py`,
  `claude_1/nogoal/route_table.py`. Add anchors through the same `EXTRA_EDITS`
  per-subject mechanism; the accepted probe's outputs must reproduce
  byte-identically when the new anchors are off.
- Per-turn world state and the oracle: `claude_1/hstarve1/oracle.py` and the
  stage-1 trajectory machinery it reads (`trace_detectors`, the fixture
  harness). The state dump is the referee's view, not the bot's.
- A new instrument only where these provably cannot answer; say so out loud.

## Gates (fail-first, in order)

1. **G-1 instrument review (codex_1):** before any result is a finding. The
   clause tap is the new part; review that it names exactly one clause per
   plant per turn and cannot name a clause on a plant the generator accepted.
2. **G-2 controls:** parity (command stream byte-identical to the uninstrumented
   champion on both fixtures); coverage (one clause row per plant per window
   turn, subject-derived, no borrowed constant); **both ways** — on employed
   turns where chops WERE formed (OSC-032 turns 35–90 carry `main:CHOPS` ×29)
   the tap must report ACCEPTED for the chosen tree, so a tap that only ever
   says "rejected" is caught.
3. **G-3 the finding + owner brief** as in the goal. Hypotheses H-A/H-B/H-C each
   get CONFIRMED / REFUTED / NOT SEPARABLE with the evidence line.

## Explicitly OUT of scope

- Any fix, candidate, behaviour change, harm/benefit judgment or class-wide
  claim ("this happens in other games"). Those are possible follow-ups the owner
  may charter after ruling.
- Any work against the owner's open extend-versus-replace design question; any
  extension of P1/P2; any Arena action (controller local_claude_1, session 3
  running); any touch of the resident file or dev copy.

## Why it is worth doing

Two cases of 34, but the first two in the investigation where the bot sat out
half a game with one troll on the board. If H-A holds, the cost is not two
fixtures — it is every game where the opening starves, and that is a question
the owner will want to ask next. This card only makes the next question
askable; it does not ask it.
