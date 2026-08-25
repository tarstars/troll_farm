---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["local_claude_1", "user"]
cc: ["codex_1"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T142134Z-20260820-pair-selector-phase-one-unblocked.md"]
supersedes: ["coordination/messages/claude_1/20260820T094549Z-20260820-pair-selector-phase1-deferred.md"]
message_id: coordination/messages/claude_1/20260820T143805Z-20260820-pair-selector-phase1-handoff.md
created_utc: 2026-08-20T14:38:05Z
review_ref: codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md
artifact_ref: agent/claude_1
artifact_commit: 8cacaa080bb7f8ca1a92de0704dde205fcfc64c1
artifact_paths: ["claude_1/picker1/mechanism-note-2026-08-20.md", "claude_1/picker1/make_picker_probe.py", "claude_1/picker1/probe.py", "claude_1/picker1/probe-picker1.rs", "claude_1/picker1/mechanism-2026-08-20.json", "claude_1/picker1/mechanism-all24-2026-08-20.json", "claude_1/picker1/deadlock_check.py", "claude_1/picker1/deadlock-all24-2026-08-20.json", "claude_1/picker1/step0-arm-identity-2026-08-20.py"]
---

- To: local_claude_1, user (OWNER — this is the design gate item)
- CC: codex_1 (reviewer, instrument-first)
- Task: 20260820-pair-selector-anti-benching, **Phase 1 DELIVERED**
- Requires acknowledgement: yes

# handoff: Phase 1 mechanism note + fix design proposal — the picker benches a working troll to keep a promise it then makes unkeepable

DELIVERED, not deferred. The unblock card arrived on a launcher-started session
and the work ran in that session. This discharges my DEFERRED card 3; its
rationale is void as ruled, and step 0 says so with a measurement rather than
by agreement.

## Step 0, as ordered — the byte-identity is measured, not inherited

Both night arms differ by **one hunk, 8 lines**, inside `predicted_opp_chop`.
The three regions that decide the pairing are byte-identical:
`select()` block `8978fca0f9e8375b`, candidate assembly `f7227b5d8cc18f3d`,
`Candidate`/`Target` types `7e7ec38954f68d49`.

**One qualification I will not leave implicit**: that hunk feeds `predict_tree`,
which feeds candidate **scores** — so `select()`'s *inputs* can differ between
arms where the forecast participates. The **mechanism** is arm-independent; the
**arithmetic** is pinned to cure-C `ad3bfefe`, which is what the charter pins
Phase 1 to. Tonight's verdict cannot move the answer.

## The instrument

Print-only taps in the pinned subject. The selector's own `compatible()` and
`stock_compatible()` calls are hoisted into `let` bindings that the original
`if` reads, so the logged verdict IS the verdict used — one scoring path, no
replica. Per situation: parity against `regression_tests.run_binary_custom` on
the uninstrumented subject, then a no-gaps/no-duplicates coverage check, before
any row is read.

**The guard fired and I was wrong.** The first classifier declared a
benched-unit pair tying the winner "impossible by construction" and failed the
run instead of reporting a mechanism. Ties ARE reachable — `score > best_score`
is strict — and that retraction is the second finding below. Recorded in the
note rather than quietly patched.

## What was measured

All **24** `GOAL_SPLIT_WRONG` situations (the charter required four), **2245**
benched-with-work turns. Benched = the selector returned `WAIT` for the unit
while that unit's own generator list held a non-WAIT candidate.

1. **Hard filter, and it is `compatible()`: 2245 of 2245.** Every benched turn
   is blocked at the winner by the same-target-cell clause. `stock_compatible`
   never bit once. This is forced, not incidental: with the partner fixed, a
   positive-scored candidate of mine that survived both predicates would
   out-sum `WAIT` (0.0), so a benching necessarily implicates the filter — and
   the probe confirms it on every turn rather than arguing it.
2. **Then the arithmetic splits.** 1435 turns SCORE PREFERENCE, partner term
   dominating 1435/1435; **810 turns decided by ENUMERATION ORDER** on an exact
   tie, where the pair found first keeps the crown and index 0 of `ids[0]`'s
   list is `WAIT`. Prediction: the benched unit is always the lower id.
   Observed: **10 of 10** tie situations bench unit 0.
3. **The preferred alternative is one the picker itself makes impossible.**
   On **2010 of 2245** turns — and **4 of 4** owner-ruled cases — the partner's
   winning command is a `MOVE` onto the cell the benched troll is standing on,
   which the referee drops unless the occupant vacates, and the same pair
   orders that occupant to `WAIT`. Nothing changes, so it repeats: OSC-017 194
   identical turns, OSC-013 187, OSC-034 94.

The four ruled cases, exactly: OSC-017 `CHOP 0` 222.22 loses to `MOVE 2 10 0`
375.00 (margin 152.78) × 194; OSC-013 86.96 vs 150.00 (63.04) × 187; OSC-034
500.00 vs 500.00 — a tie — × 94; OSC-004 3 ties + 9 preferences.

## Design proposal, for the OWNER's gate (nothing built)

- **P1 — refuse the pair the picker itself makes impossible.** Drop a pair
  where one unit MOVEs onto a cell whose occupant the same pair orders to WAIT.
  Covers 2010/2245 turns and 4/4 ruled cases; smallest blast radius; removes
  only choices the referee discards anyway.
- **P2 — break ties toward fewer WAITs.** Closes the 810 tie turns and removes
  a behaviour currently decided by `BTreeMap` key order, which nobody designed.
- **P3 — price the bench** (WAIT scored as the forgone candidate) and **P4 —
  discount promises against work in hand**: both principled, both change every
  selection in every game. Named, not recommended for a first cut.

**Recommendation: P1 + P2 as one candidate**, with the 235 non-deadlock turns
(OSC-002 189, OSC-001 26, OSC-029 14, OSC-031 6 — contested target, partner
headed elsewhere) explicitly OUT of scope and said so, not hoped away.

Phase 2 stays as chartered: named-costs gate, its own platform session,
fail-first fixtures on the four ruled cases, rebased to whatever resident
tonight settles.

## For the owner, in plain words

Your question was: why does the team-picker bench a troll that has work? The
answer, measured on all 24 cases and not just the four you ruled on:

**The troll is standing on the tree, holding an axe. The picker looks at its
partner, who is further away, decides the partner's future chop is worth more,
and sends the partner to walk onto that same square — so it orders the troll on
the square to stand still and get out of the way. But standing still IS not
getting out of the way. The square stays occupied, the partner never arrives,
and next turn the picker makes exactly the same decision. That is the 194-turn
whale: two trolls, one tree, both idle, forever.**

Where the two are worth exactly the same, it is worse than a judgement call —
the picker benches whichever troll has the lower ID number, purely because that
is the order the loop happens to run in.

Two repairs are on your desk. The narrow one stops the picker choosing a move
it has itself made impossible. The second stops the coin-flip going to loop
order. Together they cover every case you ruled on. Nothing is built until you
say which.
